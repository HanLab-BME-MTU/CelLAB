"""
CelLAB Launcher — starts Flask server and opens PyWebView window.

Usage:
    python cellab_launcher.py          # development mode
    cellab.exe                         # bundled distribution
"""

import sys
import os
import threading
import socket
import time

def get_base_dir():
    """Get the base directory — works for both dev and PyInstaller bundle."""
    if getattr(sys, '_MEIPASS', None):
        # PyInstaller bundle: files extracted to temp dir
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

def find_free_port(start=5000, end=5050):
    """Find an available port."""
    for port in range(start, end):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('127.0.0.1', port))
                return port
            except OSError:
                continue
    return start

def start_flask(port):
    """Start the Flask server in a background thread."""
    # Set environment before importing app
    os.environ['CELLAB_PORT'] = str(port)
    os.environ['CELLAB_BASE_DIR'] = get_base_dir()
    os.environ['CELLAB_NO_BROWSER'] = '1'  # Don't auto-open browser

    # Suppress Flask startup banner
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.WARNING)

    # Import and run Flask app
    sys.path.insert(0, get_base_dir())
    from app import app
    app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False)

def wait_for_server(port, timeout=15):
    """Wait until Flask is responding."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.5)
                s.connect(('127.0.0.1', port))
                return True
        except (ConnectionRefusedError, OSError):
            time.sleep(0.2)
    return False

def main():
    port = find_free_port()
    print(f"CelLAB starting on port {port}...")

    # Start Flask in background thread
    flask_thread = threading.Thread(target=start_flask, args=(port,), daemon=True)
    flask_thread.start()

    # Wait for server to be ready
    if not wait_for_server(port):
        print("ERROR: Flask server failed to start")
        sys.exit(1)

    print(f"Server ready. Opening CelLAB window...")

    # Open PyWebView window
    import webview
    window = webview.create_window(
        title='CelLAB — Cellular Analysis Workbench',
        url=f'http://127.0.0.1:{port}',
        width=1400,
        height=900,
        min_size=(1024, 700),
        resizable=True,
        text_select=True,
    )
    webview.start(debug=False)

    # Window closed — exit
    print("CelLAB closed.")
    os._exit(0)

if __name__ == '__main__':
    import multiprocessing
    multiprocessing.freeze_support()
    main()
