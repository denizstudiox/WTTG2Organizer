"""
WTTG2 Organizer - Desktop Launcher
Wraps the Flask/SocketIO server in a native window using pywebview.
Hides the console and ensures shutdown when window is closed.
"""
import webview
import threading
import os
import sys
import time
import socket
import logging
from app import create_app, socketio

# Setup File Logging for debugging in pythonw
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "launcher_debug.log")
logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='w'
)

def log(msg):
    logging.info(msg)
    if sys.stdout is not None:
        print(msg)
        sys.stdout.flush()

# Configuration
PORT = 1337
URL = f"http://localhost:{PORT}"

def is_server_ready(port):
    """Check if the server is listening on the given port"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            return s.connect_ex(('localhost', port)) == 0
    except:
        return False

def run_server():
    """Start the Flask server in a separate thread"""
    try:
        log("Creating Flask App...")
        app = create_app('default')
        log(f"Starting SocketIO on port {PORT}...")
        socketio.run(app, 
                     host='0.0.0.0', 
                     port=PORT, 
                     debug=False, 
                     use_reloader=False,
                     allow_unsafe_werkzeug=True)
    except Exception as e:
        log(f"CRITICAL: Server Error: {e}")
        logging.exception("Server Traceback:")

def start_launcher():
    """Main launcher logic"""
    try:
        log("--- STARTING LAUNCHER ---")
        # Start server in daemon thread
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()

        # Wait for server to be ready
        log("Waiting for server to initialize...")
        max_retries = 20 # Increased retries
        for i in range(max_retries):
            if is_server_ready(PORT):
                log("Server is ready!")
                break
            log(f"Server not ready... retrying ({i+1}/{max_retries})")
            time.sleep(1)
        else:
            log("Error: Server failed to start in time.")
            os._exit(1)

        # Create window
        log("Creating pywebview window...")
        window = webview.create_window(
            'WTTG2 ORGANIZER v2.0', 
            URL,
            width=1100,
            height=750,
            min_size=(800, 600)
        )

        # Start the webview loop
        log("Starting webview loop (this blocks until window closes)...")
        # debug=False for production, but we have file logs now
        webview.start()
        
        log("Window closed naturally.")
    except Exception as e:
        log(f"CRITICAL: Launcher Error: {e}")
        logging.exception("Launcher Traceback:")
    finally:
        # Once window is closed, kill the entire process
        log("Shutting down system process...")
        os._exit(0)

if __name__ == '__main__':
    start_launcher()
