"""
CellIntella Manager - Unified AI Interface (FIXED - Lazy Loading)
=======================================

Routes queries between Local (Llama 3.2 3B) and Server (Llama 3.3 70B) AI.

FIX: Uses lazy loading for Local AI to avoid threading conflicts with PyWebView.
The model loads on first query instead of at initialization.

Author: Han Lab - Mechanobiology Dry Lab
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import warnings

# Import AI components
try:
    from .cellintella_local import CellIntellaLocal
    LOCAL_AVAILABLE = True
except ImportError as e:
    LOCAL_AVAILABLE = False
    CellIntellaLocal = None
    print(f"Warning: CellIntellaLocal not available: {e}")

try:
    from .cellintella_server import CellIntellaServer
    SERVER_AVAILABLE = True
except ImportError as e:
    SERVER_AVAILABLE = False
    CellIntellaServer = None
    print(f"Warning: CellIntellaServer not available: {e}")

# Get paths
CellIntella_DIR = Path(__file__).parent


# ============================================================================
# CellIntella MANAGER CLASS
# ============================================================================

class CellIntella:
    """
    Unified CellIntella interface with Local/Server mode switching
    
    This is the main class that CELLAB frontend interacts with.
    It routes queries to either Local AI (default) or Server AI (optional).
    
    Modes:
    - LOCAL (default): Llama 3.2 3B on CPU, always available
    - SERVER (optional): Llama 3.3 70B on GPU, requires authentication
    
    The user can toggle between modes via UI button (green = server active).
    
    Usage:
        # Initialize with default (local) mode
        ai = CellIntella()
        
        # Query
        response = ai.query("How do I segment NK cells?")
        
        # Check available modes
        print(ai.get_available_modes())
        
        # Switch to server (if available)
        if ai.can_use_server():
            ai.set_mode('server')
            ai.authenticate(username='user', password='pass')
            response = ai.query("Advanced literature query", advanced=True)
    
    Attributes:
        mode: Current mode ('local' or 'server')
        local_ai: Local AI instance (Llama 3.2 3B)
        server_ai: Server AI instance (Llama 3.3 70B)
        conversation_history: Unified conversation across modes
    """
    
    def __init__(
        self,
        mode: str = 'local',
        server_url: Optional[str] = None,
        api_key: Optional[str] = None,
        verbose: bool = False
    ):
        """
        Initialize CellIntella Manager
        
        Args:
            mode: Starting mode ('local' or 'server', default: 'local')
            server_url: Server endpoint (None = not configured)
            api_key: Server API key (optional)
            verbose: Print debug information
        """
        
        self.verbose = verbose
        self.mode = 'local'  # Always start in local mode
        self.conversation_history = []
        self.usage_stats = {
            'local_queries': 0,
            'server_queries': 0,
            'mode_switches': 0,
            'session_start': datetime.now().isoformat()
        }
        
        # Initialize local AI with LAZY LOADING (fixes threading issues)
        self.local_ai = None
        self.local_ai_attempted = False  # Track if we tried to load
        if LOCAL_AVAILABLE:
            if self.verbose:
                print("✅ Local AI available (will load on first query)")
        else:
            print("❌ Local AI not available")
        
        # Initialize server AI (placeholder by default)
        self.server_ai = None
        if SERVER_AVAILABLE:
            self.server_ai = CellIntellaServer(
                server_url=server_url,
                api_key=api_key
            )
            if self.verbose:
                print("✅ Server AI interface initialized (placeholder)")
        
        # Set initial mode (force to local if server requested but not available)
        if mode == 'server' and not self.can_use_server():
            print("⚠️  Server mode requested but not available, using local mode")
            self.mode = 'local'
        else:
            self.mode = mode
    
    def _ensure_local_ai_loaded(self):
        """
        Lazy load Local AI on first use using process wrapper
        
        Uses a separate process to avoid Flask/PyWebView threading issues.
        """
        if self.local_ai is not None:
            return True  # Already loaded
        
        if self.local_ai_attempted:
            return False  # Already tried and failed
        
        if not LOCAL_AVAILABLE:
            return False  # Not available
        
        # Try to load using process wrapper
        self.local_ai_attempted = True
        
        try:
            if self.verbose:
                print("Loading Local AI model in separate process...")
            
            # Import process wrapper
            from .cellintella_process_wrapper import CellIntellaProcessWrapper
            
            # Initialize in separate process
            self.local_ai = CellIntellaProcessWrapper(
                n_threads=10,      # Use 4 threads (was 2)
                n_ctx=8192,       # Keep context window
                verbose=self.verbose,
                timeout=500
            )
            
            if self.verbose:
                print("✅ Local AI loaded successfully (process-isolated)")
            
            return True
        
        except Exception as e:
            print(f"⚠️  Failed to load Local AI: {e}")
            if self.verbose:
                import traceback
                traceback.print_exc()
            self.local_ai = None
            return False
    
    def query(
        self,
        user_message: str,
        context_type: Optional[str] = None,
        advanced: bool = False,
        **kwargs
    ) -> Union[str, Dict[str, Any]]:
        """
        Process user query (routes to active AI mode)
        
        Args:
            user_message: User's question
            context_type: 'immunia', 'fastia', 'general', 'error' (auto-detect if None)
            advanced: Use advanced features (literature search, protocols - server only)
            **kwargs: Additional arguments passed to AI engine
        
        Returns:
            Response string (local) or response dict (server)
        """
        
        # Record query in unified history
        self.conversation_history.append({
            'role': 'user',
            'content': user_message,
            'timestamp': datetime.now().isoformat(),
            'mode': self.mode
        })
        
        response = None
        
        # Route to appropriate AI
        if self.mode == 'local':
            response = self._query_local(user_message, context_type, **kwargs)
            self.usage_stats['local_queries'] += 1
        
        elif self.mode == 'server':
            if advanced:
                response = self._query_server_advanced(user_message, **kwargs)
            else:
                response = self._query_server_basic(user_message, context_type, **kwargs)
            self.usage_stats['server_queries'] += 1
        
        # Record response in unified history
        if response:
            response_content = response if isinstance(response, str) else response.get('response', '')
            self.conversation_history.append({
                'role': 'assistant',
                'content': response_content,
                'timestamp': datetime.now().isoformat(),
                'mode': self.mode
            })
        
        return response
    
    def _query_local(
        self,
        user_message: str,
        context_type: Optional[str],
        **kwargs
    ) -> str:
        """Query local AI (Llama 3.2 3B) with lazy loading"""
        
        # Lazy load the model
        if not self._ensure_local_ai_loaded():
            return "❌ Local AI not available. Please check installation."
        
        try:
            response = self.local_ai.query(
                user_message=user_message,
                context_type=context_type,
                **kwargs
            )
            return response
        
        except Exception as e:
            error_msg = f"Local AI error: {e}"
            if self.verbose:
                print(f"❌ {error_msg}")
            return f"I encountered an error. Please try rephrasing your question."
    
    def _query_server_basic(
        self,
        user_message: str,
        context_type: Optional[str],
        **kwargs
    ) -> Dict[str, Any]:
        """Query server AI (basic mode - similar to local)"""
        
        if not self.server_ai:
            # Fallback to local
            print("⚠️  Server AI not available, falling back to local")
            self.set_mode('local')
            return self._query_local(user_message, context_type, **kwargs)
        
        # Check authentication
        if not self.server_ai.is_authenticated:
            return {
                'success': False,
                'error': 'Not authenticated',
                'response': 'Please authenticate with server before using server mode.'
            }
        
        try:
            result = self.server_ai.query_advanced(
                user_message=user_message,
                include_literature=False,
                include_protocols=False,
                **kwargs
            )
            return result
        
        except Exception as e:
            error_msg = f"Server AI error: {e}"
            if self.verbose:
                print(f"❌ {error_msg}")
            
            # Fallback to local
            print("⚠️  Server error, falling back to local mode")
            self.set_mode('local')
            return self._query_local(user_message, context_type, **kwargs)
    
    def _query_server_advanced(
        self,
        user_message: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Query server AI (advanced mode - with literature/protocols)"""
        
        if not self.server_ai:
            return {
                'success': False,
                'error': 'Server not available',
                'response': 'Advanced features require server mode, which is not available.'
            }
        
        if not self.server_ai.is_authenticated:
            return {
                'success': False,
                'error': 'Not authenticated',
                'response': 'Please authenticate with server before using advanced features.'
            }
        
        try:
            result = self.server_ai.query_advanced(
                user_message=user_message,
                include_literature=kwargs.get('include_literature', True),
                include_protocols=kwargs.get('include_protocols', True),
                **kwargs
            )
            return result
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'response': f'Advanced query failed: {e}'
            }
    
    def set_mode(self, mode: str) -> bool:
        """
        Switch between local and server modes
        
        Args:
            mode: 'local' or 'server'
        
        Returns:
            True if mode switched successfully
        """
        
        if mode not in ['local', 'server']:
            print(f"❌ Invalid mode: {mode}. Use 'local' or 'server'")
            return False
        
        # Check if requested mode is available
        if mode == 'local' and not LOCAL_AVAILABLE:
            print("❌ Local AI not available")
            return False
        
        if mode == 'server' and not self.can_use_server():
            print("❌ Server AI not available or not configured")
            return False
        
        # Switch mode
        previous_mode = self.mode
        self.mode = mode
        self.usage_stats['mode_switches'] += 1
        
        if self.verbose:
            print(f"🔄 Switched from {previous_mode} to {mode} mode")
        
        return True
    
    def can_use_server(self) -> bool:
        """
        Check if server mode is available
        
        Returns:
            True if server mode can be used
        """
        
        if not self.server_ai:
            return False
        
        # Check if server is configured
        if not self.server_ai.is_configured:
            return False
        
        # For now, always return False since server is placeholder
        # This will return True once server is deployed
        status = self.server_ai.get_server_status()
        return status.get('available', False)
    
    def authenticate(
        self,
        username: str,
        password: str
    ) -> bool:
        """
        Authenticate with server
        
        Args:
            username: University username
            password: User password
        
        Returns:
            True if authentication successful
        """
        
        if not self.server_ai:
            print("❌ Server AI not available")
            return False
        
        return self.server_ai.authenticate(username, password)
    
    def get_current_mode(self) -> str:
        """
        Get current AI mode
        
        Returns:
            'local' or 'server'
        """
        return self.mode
    
    def get_available_modes(self) -> Dict[str, bool]:
        """
        Get availability status of all modes
        
        Returns:
            Dictionary with mode availability
        """
        
        return {
            'local': LOCAL_AVAILABLE,
            'server': self.can_use_server()
        }
    
    def get_mode_info(self) -> Dict[str, Any]:
        """
        Get detailed information about current mode
        
        Returns:
            Dictionary with mode details
        """
        
        info = {
            'current_mode': self.mode,
            'available_modes': self.get_available_modes()
        }
        
        if self.mode == 'local' and self.local_ai:
            info['local_info'] = self.local_ai.get_model_info()
        
        if self.mode == 'server' and self.server_ai:
            info['server_info'] = self.server_ai.get_server_status()
            info['authenticated'] = self.server_ai.is_authenticated
        
        return info
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """
        Get usage statistics
        
        Returns:
            Dictionary with usage stats
        """
        
        stats = self.usage_stats.copy()
        stats['total_queries'] = stats['local_queries'] + stats['server_queries']
        stats['session_duration'] = self._get_session_duration()
        
        return stats
    
    def _get_session_duration(self) -> str:
        """Calculate session duration"""
        start = datetime.fromisoformat(self.usage_stats['session_start'])
        duration = datetime.now() - start
        
        hours = duration.seconds // 3600
        minutes = (duration.seconds % 3600) // 60
        
        return f"{hours}h {minutes}m"
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        
        if self.local_ai:
            self.local_ai.clear_history()
        
        if self.verbose:
            print("✅ Conversation history cleared")
    
    def get_history(self) -> List[Dict[str, str]]:
        """
        Get unified conversation history
        
        Returns:
            List of message dictionaries
        """
        return self.conversation_history.copy()
    
    def export_session(self, output_path: str):
        """
        Export complete session data
        
        Args:
            output_path: Path to output file
        """
        
        session_data = {
            'export_time': datetime.now().isoformat(),
            'mode_info': self.get_mode_info(),
            'usage_stats': self.get_usage_stats(),
            'conversation_history': self.conversation_history
        }
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
        
        if self.verbose:
            print(f"✅ Session exported to: {output_file}")
    
    def get_server_features(self) -> Dict[str, bool]:
        """
        Get available server features
        
        Returns:
            Dictionary of feature availability
        """
        
        if not self.server_ai:
            return {
                'literature_search': False,
                'protocol_database': False,
                'advanced_analysis': False,
                'multi_modal': False
            }
        
        status = self.server_ai.get_server_status()
        return status.get('features', {})
    
    def __repr__(self) -> str:
        """String representation"""
        mode_emoji = "💻" if self.mode == 'local' else "🌐"
        return f"CellIntella({mode_emoji} mode={self.mode}, queries={self.usage_stats['local_queries'] + self.usage_stats['server_queries']})"


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def create_CellIntella(
    mode: str = 'local',
    verbose: bool = False
) -> CellIntella:
    """
    Convenience function to create CellIntella instance
    
    Args:
        mode: Starting mode ('local' or 'server')
        verbose: Print debug info
    
    Returns:
        CellIntella instance
    """
    return CellIntella(mode=mode, verbose=verbose)


def check_availability() -> Dict[str, bool]:
    """
    Check which AI modes are available
    
    Returns:
        Dictionary with availability status
    """
    return {
        'local': LOCAL_AVAILABLE,
        'server': SERVER_AVAILABLE
    }


# ============================================================================
# TESTING
# ============================================================================

def test_cellintella_manager():
    """Test CellIntella manager with mode switching"""
    
    print("\n" + "="*60)
    print("🤖 CellIntella Manager - Test Suite")
    print("="*60 + "\n")
    
    # Check availability
    print("Checking availability...")
    availability = check_availability()
    print(f"Local AI available: {availability['local']}")
    print(f"Server AI available: {availability['server']}")
    
    try:
        # Initialize in local mode (default)
        print("\n" + "-"*60)
        print("Initializing CellIntella (default: local mode)...")
        ai = CellIntella(verbose=True)
        
        print("\n" + "-"*60)
        print("Current mode info:")
        print(json.dumps(ai.get_mode_info(), indent=2))
        
        # Test local query
        print("\n" + "-"*60)
        print("Test Query (Local Mode):")
        response = ai.query("What is IMMUNIA?")
        print(f"Response: {response[:200]}...")
        
        # Try to switch to server mode
        print("\n" + "-"*60)
        print("Attempting to switch to server mode...")
        success = ai.set_mode('server')
        
        if success:
            print("✅ Switched to server mode")
            print("Note: Server is currently a placeholder")
            
            # Test server query
            response = ai.query("Test server query")
            print(f"Server response: {response}")
        else:
            print("⚠️  Server mode not available (expected - not deployed yet)")
        
        # Switch back to local
        print("\n" + "-"*60)
        print("Switching back to local mode...")
        ai.set_mode('local')
        
        # Show usage stats
        print("\n" + "-"*60)
        print("Usage Statistics:")
        print(json.dumps(ai.get_usage_stats(), indent=2))
        
        # Export session
        print("\n" + "-"*60)
        print("Exporting session...")
        ai.export_session('CellIntella_test_session.json')
        
        print("\n" + "="*60)
        print("✅ All tests completed!")
        print("="*60)
    
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == '__main__':
    """Run test suite"""
    test_cellintella_manager()
