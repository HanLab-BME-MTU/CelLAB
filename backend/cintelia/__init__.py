"""
cintelia - Context-aware AI Assistant for CELLAB
================================================

cintelia is an embedded AI assistant that helps researchers with:
- IMMUNIA pipeline (immune cell analysis)
- FASTIA pipeline (focal adhesion analysis)
- Image processing and troubleshooting
- Protocol guidance and literature support

Architecture:
- LOCAL: Llama 3.2 3B (CPU-only, embedded in CELLAB)
- SERVER: Llama 3.3 70B (Future - university server with GPU)

Usage:
    from backend.cintelia import cintelia
    
    # Initialize local AI
    ai = cintelia(mode='local')
    
    # Query with context
    response = ai.query(
        "How do I adjust segmentation threshold for NK cells?",
        context_type='immunia'
    )
    
    print(response)

Author: Han Lab - Mechanobiology Dry Lab
Version: 1.0.0
"""

import os
import sys
from pathlib import Path

# Package metadata
__version__ = "1.0.0"
__author__ = "Han Lab - Mechanobiology Dry Lab"
__license__ = "MIT"

# Get package directory
cintelia_DIR = Path(__file__).parent
MODELS_DIR = cintelia_DIR / "models"
DOCS_DIR = cintelia_DIR / "docs"

# Ensure directories exist
MODELS_DIR.mkdir(exist_ok=True)
DOCS_DIR.mkdir(exist_ok=True)

# Model configuration
MODEL_CONFIG = {
    'local': {
        'name': 'Llama-3.2-3B-Instruct-Q4_K_M.gguf',
        'size_gb': 2.0,
        'url': 'https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q4_K_M.gguf',
        'sha256': None,  # Optional: Add checksum for verification
        'context_length': 8192,
        'requires_gpu': False
    },
    'server': {
        'name': 'Llama-3.3-70B-Instruct',
        'size_gb': 40.0,
        'url': None,  # Deployed on university server
        'context_length': 131072,
        'requires_gpu': True
    }
}

# Check if local model exists
def check_model_installed():
    """Check if local model is installed"""
    model_path = MODELS_DIR / MODEL_CONFIG['local']['name']
    return model_path.exists()

# Initialize availability flags
SERVER_AVAILABLE = False
cintelia = None
cinteliaLocal = None
cinteliaServer = None

# Import main interface
try:
    from .cintelia_manager import cintelia
    from .cintelia_local import cinteliaLocal
    
    # Only import server if dependencies available
    try:
        from .cintelia_server import cinteliaServer
        SERVER_AVAILABLE = True
    except ImportError:
        SERVER_AVAILABLE = False
        cinteliaServer = None
    
except ImportError as e:
    # Graceful degradation if dependencies missing
    print(f"Warning: cintelia core not available: {e}")

# Import utilities (with graceful degradation)
try:
    from .documentation_parser import DocumentationParser
except ImportError:
    DocumentationParser = None

try:
    from .context_builder import ContextBuilder
except ImportError:
    ContextBuilder = None

try:
    from .conversation_manager import ConversationManager
except ImportError:
    ConversationManager = None

try:
    from .model_downloader import download_model, verify_model
except ImportError:
    download_model = None
    verify_model = None

# Public API
__all__ = [
    'cintelia',
    'cinteliaLocal',
    'cinteliaServer',
    'DocumentationParser',
    'ContextBuilder',
    'ConversationManager',
    'download_model',
    'verify_model',
    'check_model_installed',
    'cintelia_DIR',
    'MODELS_DIR',
    'DOCS_DIR',
    'MODEL_CONFIG',
    'SERVER_AVAILABLE'
]

# Initialization message (only show if imported directly, not during module runs)
if __name__ != '__main__':
    # Model status check on import
    if check_model_installed():
        print(f"✅ cintelia Local model found: {MODEL_CONFIG['local']['name']}")
    else:
        print(f"⚠️  cintelia Local model not found!")
        print(f"   Run: python -m backend.cintelia.model_downloader")
        print(f"   Or download manually from:")
        print(f"   {MODEL_CONFIG['local']['url']}")
        print(f"   Place in: {MODELS_DIR}")

    # Server availability
    if SERVER_AVAILABLE:
        print("🌐 cintelia Server mode available")
    else:
        print("💻 cintelia Local mode only")

    print(f"📦 cintelia v{__version__} initialized")
    print(f"📁 Package directory: {cintelia_DIR}")
