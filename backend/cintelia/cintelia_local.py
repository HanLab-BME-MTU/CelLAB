"""
cintelia Local - CPU-based AI Assistant
=======================================

Local AI assistant powered by Llama 3.2 3B.

This module:
- Runs Llama 3.2 3B on CPU (no GPU required)
- Uses llama-cpp-python for efficient inference
- Integrates with ContextBuilder for documentation retrieval
- Manages conversation history
- Provides context-aware responses

The model runs entirely on CPU with quantized weights (Q4_K_M),
making it lightweight and portable.

Requirements:
- llama-cpp-python
- Llama 3.2 3B model (2GB GGUF format)

Author: Han Lab - Mechanobiology Dry Lab
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# Import context builder
try:
    from .context_builder import ContextBuilder, detect_context_type
    from .prompt_templates import build_prompt, get_few_shot_example
    CONTEXT_AVAILABLE = True
except ImportError:
    CONTEXT_AVAILABLE = False
    print("Warning: Context builder not available")

# Import llama-cpp-python
try:
    from llama_cpp import Llama
    LLAMA_CPP_AVAILABLE = True
except ImportError:
    LLAMA_CPP_AVAILABLE = False
    Llama = None
    print("Warning: llama-cpp-python not installed")
    print("Install with: pip install llama-cpp-python")

# Get paths
cintelia_DIR = Path(__file__).parent
MODELS_DIR = cintelia_DIR / "models"
MODEL_PATH = MODELS_DIR / "Llama-3.2-3B-Instruct-Q4_K_M.gguf"


# ============================================================================
# cintelia LOCAL CLASS
# ============================================================================

class cinteliaLocal:
    """
    Local AI assistant using Llama 3.2 3B
    
    Runs on CPU without GPU requirements. Provides context-aware
    responses for IMMUNIA, FASTIA, and general CELLAB queries.
    
    Usage:
        ai = cinteliaLocal()
        response = ai.query(
            "How do I fix NK cell segmentation?",
            context_type='immunia'
        )
        print(response)
    
    Attributes:
        llm: Llama model instance
        context_builder: Documentation retrieval system
        conversation_history: List of past messages
    """
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        n_ctx: int = 2048,     # Changed from 8192
        n_threads: int = 2,    # Changed from 4
        n_gpu_layers: int = 0,
        verbose: bool = False
    ):
        """
        Initialize cintelia Local
        
        Args:
            model_path: Path to GGUF model file (default: auto-detect)
            n_ctx: Context window size (default: 8192)
            n_threads: CPU threads to use (default: 4)
            n_gpu_layers: GPU layers (0 = CPU-only, default)
            verbose: Print debug info
        """
        
        self.verbose = verbose
        self.llm = None
        self.context_builder = None
        self.conversation_history = []
        
        # Check if llama-cpp-python is available
        if not LLAMA_CPP_AVAILABLE:
            raise ImportError(
                "llama-cpp-python is required for cinteliaLocal.\n"
                "Install with: pip install llama-cpp-python"
            )
        
        # Get model path
        if model_path is None:
            model_path = MODEL_PATH
        else:
            model_path = Path(model_path)
        
        # Check if model exists
        if not model_path.exists():
            raise FileNotFoundError(
                f"Model not found: {model_path}\n\n"
                f"Download the model:\n"
                f"1. Run: python -m backend.cintelia.model_downloader\n"
                f"2. Or manually download from:\n"
                f"   https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF\n"
                f"3. Place in: {MODELS_DIR}"
            )
        
        # Initialize Llama model
        if self.verbose:
            print(f"Loading model from: {model_path}")
            print(f"Context window: {n_ctx} tokens")
            print(f"CPU threads: {n_threads}")
        
        try:
            self.llm = Llama(
                model_path=str(model_path),
                n_ctx=n_ctx,
                n_threads=n_threads,
                n_gpu_layers=0,
                n_batch=512,           # Add batch size
                use_mmap=True,         # Enable memory mapping
                use_mlock=False,       # Disable memory locking
                verbose=verbose
            )
            
            if self.verbose:
                print("✅ Model loaded successfully")
        
        except Exception as e:
            raise RuntimeError(f"Failed to load model: {e}")
        
        # Initialize context builder
        if CONTEXT_AVAILABLE:
            self.context_builder = ContextBuilder()
            if self.verbose:
                print("✅ Context builder initialized")
        else:
            if self.verbose:
                print("⚠️  Context builder not available - responses will be less accurate")
                
        # Initialize RAG system
        try:
            from backend.cintelia.cintelia_rag import cinteliaDocumentStore
            # self.doc_store = cinteliaDocumentStore(verbose=self.verbose)
            
            
            docs_path = Path(__file__).parent / "documents"
            self.doc_store = cinteliaDocumentStore(docs_folder=str(docs_path), verbose=self.verbose)
            
            if self.verbose:
                if self.doc_store.has_documents():
                    print("✅ RAG system initialized with documents")
                else:
                    print("⚠️  RAG system initialized (no documents loaded)")
        except Exception as e:
            if self.verbose:
                print(f"⚠️  RAG system not available: {e}")
            self.doc_store = None
            
    def _apply_chat_template(self, prompt):
        """Apply Llama chat template to prompt"""
        # Simple template - adjust based on your model
        return f"<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
        
    def query(self, user_message, context_type=None, use_rag=True, **kwargs):
        """
        Query the AI model
        
        Args:
            user_message: User's question
            context_type: Context type ('immunia', 'fastia', etc.)
            use_rag: Whether to use document retrieval (default: True)
        """
        
        # Get base context
        system_context = self.context_builder.build_context(user_message, context_type)        
        
        # Retrieve relevant documents if RAG is enabled
        doc_context = ""
        if use_rag and self.doc_store and self.doc_store.has_documents():
            doc_context = self.doc_store.retrieve(user_message, n_results=3)
            
            if self.verbose and doc_context:
                print("📚 Retrieved relevant documents")
        
        # Build full prompt
        if doc_context:
            full_prompt = f"""{system_context}

    {doc_context}

    INSTRUCTIONS:
    - Use the provided research documents to answer questions
    - Always cite sources using [Source: filename]
    - Quote relevant passages when helpful
    - If answer is not in documents, use your general knowledge but mention this

    Question: {user_message}

    Answer (with citations if using documents):"""
        else:
            full_prompt = f"""{system_context}

    Question: {user_message}

    Answer:"""
        
        # Apply chat template
        formatted_prompt = self._apply_chat_template(full_prompt)
        
        if self.verbose:
            print(f"Prompt length: {len(formatted_prompt)} chars")
        
        # Generate response
        response = self.llm(
            formatted_prompt,
            max_tokens=512,
            temperature=0.7,
            stop=["<|eot_id|>", "Question:", "USER:"]
        )
        
        return response['choices'][0]['text'].strip()
    
    def _build_basic_prompt(self, user_message: str, context_type: str) -> str:
        """
        Build basic prompt without context builder (fallback)
        
        Args:
            user_message: User's question
            context_type: Context type
        
        Returns:
            Formatted prompt
        """
        
        system_prompt = f"""You are cintelia, an AI assistant for CELLAB - a cellular analysis workbench.

You help with:
- IMMUNIA pipeline (immune cell analysis)
- FASTIA pipeline (focal adhesion analysis)
- Image processing and troubleshooting

Current context: {context_type}

Provide concise, technical, helpful answers."""
        
        prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

{system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>

{user_message}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""
        return prompt
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        if self.verbose:
            print("✅ Conversation history cleared")
    
    def get_history(self) -> List[Dict[str, str]]:
        """
        Get conversation history
        
        Returns:
            List of message dictionaries
        """
        return self.conversation_history.copy()
    
    def export_conversation(self, output_path: str):
        """
        Export conversation to JSON file
        
        Args:
            output_path: Path to output file
        """
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        conversation_data = {
            'export_time': datetime.now().isoformat(),
            'model': 'Llama-3.2-3B-Instruct-Q4_K_M',
            'messages': self.conversation_history
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(conversation_data, f, indent=2, ensure_ascii=False)
        
        if self.verbose:
            print(f"✅ Conversation exported to: {output_file}")
    
    def get_parameter_help(
        self,
        parameter_name: str,
        context_type: str = 'immunia'
    ) -> str:
        """
        Get help for a specific parameter
        
        Args:
            parameter_name: Name of parameter
            context_type: 'immunia' or 'fastia'
        
        Returns:
            Parameter information
        """
        
        if not self.context_builder:
            return "Context builder not available. Cannot retrieve parameter info."
        
        param_info = self.context_builder.get_parameter_info(
            parameter_name,
            context_type
        )
        
        if param_info:
            info_str = f"**Parameter: {param_info['name']}**\n\n"
            
            if param_info.get('description'):
                info_str += f"Description: {param_info['description']}\n"
            
            if param_info.get('type'):
                info_str += f"Type: {param_info['type']}\n"
            
            if param_info.get('default') is not None:
                info_str += f"Default: {param_info['default']}\n"
            
            if param_info.get('function'):
                info_str += f"Used in: {param_info['function']}\n"
            
            return info_str
        else:
            return f"Parameter '{parameter_name}' not found in {context_type} documentation."
    
    def list_parameters(self, context_type: str = 'immunia') -> List[str]:
        """
        List all available parameters
        
        Args:
            context_type: 'immunia' or 'fastia'
        
        Returns:
            List of parameter names
        """
        
        if not self.context_builder:
            return []
        
        return self.context_builder.list_available_parameters(context_type)
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get model information
        
        Returns:
            Dictionary with model details
        """
        
        return {
            'model_name': 'Llama-3.2-3B-Instruct',
            'quantization': 'Q4_K_M',
            'size_gb': 2.0,
            'context_window': self.llm.n_ctx() if self.llm else None,
            'model_path': str(MODEL_PATH) if MODEL_PATH.exists() else None,
            'context_builder_available': self.context_builder is not None,
            'conversation_turns': len(self.conversation_history) // 2
        }
    
    def __del__(self):
        """Cleanup on deletion"""
        if self.llm:
            del self.llm


# ============================================================================
# STANDALONE TESTING
# ============================================================================

def test_cintelia_local():
    """Test cintelia Local with sample queries"""
    
    print("\n" + "="*60)
    print("🤖 cintelia Local - Test Suite")
    print("="*60 + "\n")
    
    try:
        # Initialize
        print("Initializing cintelia Local...")
        ai = cinteliaLocal(verbose=True)
        
        print("\n" + "="*60)
        print("Model Info:")
        print(json.dumps(ai.get_model_info(), indent=2))
        print("="*60 + "\n")
        
        # Test queries
        test_cases = [
            {
                'query': "What is IMMUNIA?",
                'context': 'general'
            },
            {
                'query': "How do I fix NK cell segmentation that detects too many small objects?",
                'context': 'immunia'
            },
            {
                'query': "What is the gaussian_sigma parameter?",
                'context': 'immunia'
            },
            {
                'query': "My tracking is failing. What should I check?",
                'context': 'error'
            }
        ]
        
        for i, test in enumerate(test_cases, 1):
            print(f"\n{'='*60}")
            print(f"Test {i}/{len(test_cases)}")
            print(f"{'='*60}")
            print(f"Query: {test['query']}")
            print(f"Context: {test['context']}")
            print(f"\nResponse:")
            print("-" * 60)
            
            response = ai.query(
                test['query'],
                context_type=test['context'],
                max_tokens=300
            )
            
            print(response)
            print("-" * 60)
        
        # Export conversation
        print("\n" + "="*60)
        print("Exporting conversation...")
        ai.export_conversation('cintelia_test_conversation.json')
        print("="*60)
        
        print("\n✅ All tests completed successfully!")
        
    except FileNotFoundError as e:
        print(f"\n❌ Model not found: {e}")
        print("\nTo download the model:")
        print("1. Run: python -m backend.cintelia.model_downloader")
        print("2. Or manually download from:")
        print("   https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF")
        print(f"3. Place in: {MODELS_DIR}")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == '__main__':
    """Run test suite"""
    test_cintelia_local()
