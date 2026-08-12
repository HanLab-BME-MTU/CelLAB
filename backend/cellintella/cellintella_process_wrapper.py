"""
CellIntella Process Wrapper
========================

Runs Local AI in a separate process to avoid threading conflicts with PyWebView.

This wrapper uses multiprocessing to isolate the llama.cpp model from Flask's 
threading context, preventing memory access violations.

Author: Han Lab - Mechanobiology Dry Lab
"""

import multiprocessing as mp
from multiprocessing import Process, Queue, Event
import time
from pathlib import Path
from typing import Optional, Dict, Any
import traceback


def _ai_worker(
    command_queue: Queue,
    response_queue: Queue,
    ready_event: Event,
    model_path: str,
    n_ctx: int,
    n_threads: int,
    verbose: bool
):
    """
    Worker process that hosts the Local AI model
    
    This runs in a completely separate process, isolated from Flask threading.
    """
    
    try:
        # Import here (inside the worker process)
        from backend.cellintella.cellintella_local import CellIntellaLocal
        
        # Initialize model
        if verbose:
            print(f"[Worker Process] Loading model...")
        
        ai = CellIntellaLocal(
            model_path=model_path,
            n_ctx=n_ctx,
            n_threads=n_threads,
            verbose=verbose
        )
        
        # Signal ready
        ready_event.set()
        
        if verbose:
            print(f"[Worker Process] ✅ Ready to process queries")
        
        # Process loop
        while True:
            # Wait for command
            command = command_queue.get()
            
            if command['type'] == 'shutdown':
                break
            
            elif command['type'] == 'query':
                try:
                    response = ai.query(
                        user_message=command['message'],
                        context_type=command.get('context_type'),
                        use_rag=command.get('use_rag', True),
                        **command.get('kwargs', {})
                    )
                    
                    response_queue.put({
                        'success': True,
                        'response': response
                    })
                
                except Exception as e:
                    response_queue.put({
                        'success': False,
                        'error': str(e),
                        'traceback': traceback.format_exc()
                    })
            
            elif command['type'] == 'clear_history':
                ai.clear_history()
                response_queue.put({'success': True})
    
    except Exception as e:
        ready_event.set()  # Signal even on error
        response_queue.put({
            'success': False,
            'error': f"Worker initialization failed: {e}",
            'traceback': traceback.format_exc()
        })


class CellIntellaProcessWrapper:
    """
    Process-isolated wrapper for CellIntella Local AI
    
    This runs the model in a separate process to avoid Flask/PyWebView threading issues.
    
    Usage:
        wrapper = CellIntellaProcessWrapper()
        response = wrapper.query("What is IMMUNIA?")
    """
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        n_ctx: int = 2048,
        n_threads: int = 2,
        verbose: bool = False,
        timeout: int = 60
    ):
        """
        Initialize process wrapper
        
        Args:
            model_path: Path to model (None = auto-detect)
            n_ctx: Context window size
            n_threads: CPU threads
            verbose: Print debug info
            timeout: Seconds to wait for model loading
        """
        
        self.verbose = verbose
        self.timeout = timeout
        
        # Get model path
        if model_path is None:
            CellIntella_dir = Path(__file__).parent
            model_path = CellIntella_dir / 'models' / 'Llama-3.2-3B-Instruct-Q4_K_M.gguf'
        
        # Create communication channels
        self.command_queue = Queue()
        self.response_queue = Queue()
        self.ready_event = Event()
        
        # Start worker process
        if self.verbose:
            print("Starting AI worker process...")
        
        self.worker = Process(
            target=_ai_worker,
            args=(
                self.command_queue,
                self.response_queue,
                self.ready_event,
                str(model_path),
                n_ctx,
                n_threads,
                verbose
            ),
            daemon=True
        )
        
        self.worker.start()
        
        # Wait for ready
        if self.verbose:
            print(f"Waiting for model to load (timeout: {timeout}s)...")
        
        ready = self.ready_event.wait(timeout=timeout)
        
        if not ready:
            self.shutdown()
            raise TimeoutError(f"Model failed to load within {timeout} seconds")
        
        # Check if there was an initialization error
        if not self.response_queue.empty():
            error_msg = self.response_queue.get()
            if not error_msg.get('success', True):
                self.shutdown()
                raise RuntimeError(error_msg.get('error', 'Unknown initialization error'))
        
        if self.verbose:
            print("✅ Worker process ready")
    
    def query(
        self,
        user_message: str,
        context_type: Optional[str] = None,
        timeout: int = None,
        **kwargs
    ) -> str:
        """
        Query the AI model
        
        Args:
            user_message: User's question
            context_type: Context type ('immunia', 'fastia', etc.)
            timeout: Query timeout in seconds (None = use instance timeout)
            **kwargs: Additional arguments
        
        Returns:
            AI response string
        """
        
        if not self.worker.is_alive():
            return "❌ AI worker process is not running"
        
        # Use instance timeout if not specified
        if timeout is None:
            timeout = self.timeout
        
        # Send query
        self.command_queue.put({
            'type': 'query',
            'message': user_message,
            'context_type': context_type,
            'kwargs': kwargs
        })
        
        # Wait for response
        start_time = time.time()
        while True:
            if not self.response_queue.empty():
                result = self.response_queue.get()
                
                if result['success']:
                    return result['response']
                else:
                    error = result.get('error', 'Unknown error')
                    if self.verbose:
                        print(f"❌ Query error: {error}")
                        if 'traceback' in result:
                            print(result['traceback'])
                    return f"I encountered an error: {error}"
            
            if time.time() - start_time > timeout:
                return f"⏱️ Query timed out after {timeout} seconds"
            
            time.sleep(0.1)
    
    def clear_history(self):
        """Clear conversation history"""
        
        if not self.worker.is_alive():
            return
        
        self.command_queue.put({'type': 'clear_history'})
        
        # Wait for confirmation
        if not self.response_queue.empty():
            self.response_queue.get()
    
    def shutdown(self):
        """Shutdown worker process"""
        
        if self.worker.is_alive():
            if self.verbose:
                print("Shutting down AI worker process...")
            
            self.command_queue.put({'type': 'shutdown'})
            self.worker.join(timeout=5)
            
            if self.worker.is_alive():
                if self.verbose:
                    print("Force terminating worker process...")
                self.worker.terminate()
                self.worker.join()
        
        if self.verbose:
            print("✅ Worker process stopped")
    
    def __del__(self):
        """Cleanup on deletion"""
        self.shutdown()


# ============================================================================
# TESTING
# ============================================================================

def test_process_wrapper():
    """Test the process wrapper"""
    
    print("\n" + "="*60)
    print("🧪 Testing CellIntella Process Wrapper")
    print("="*60 + "\n")
    
    try:
        print("Initializing wrapper...")
        wrapper = CellIntellaProcessWrapper(verbose=True)
        
        print("\n" + "-"*60)
        print("Test Query 1:")
        response = wrapper.query("What is IMMUNIA?")
        print(f"Response: {response[:200]}...")
        
        print("\n" + "-"*60)
        print("Test Query 2:")
        response = wrapper.query("How do I segment NK cells?")
        print(f"Response: {response[:200]}...")
        
        print("\n" + "-"*60)
        print("Shutting down...")
        wrapper.shutdown()
        
        print("\n" + "="*60)
        print("✅ All tests passed!")
        print("="*60)
    
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        traceback.print_exc()


if __name__ == '__main__':
    # Required for Windows multiprocessing
    mp.freeze_support()
    test_process_wrapper()
