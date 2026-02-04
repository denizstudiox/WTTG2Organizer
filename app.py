"""
WTTG2 Organizer - Entry Point
Simplified entry point using application factory pattern.
"""
from app import create_app, socketio

# Create application instance
app = create_app('default')

if __name__ == '__main__':
    print("=" * 60)
    print("STARTING WTTG2 ORGANIZER SERVER")
    print("=" * 60)
    print(f"Server: http://localhost:1337")
    print(f"Press Ctrl+C to stop")
    print("=" * 60)
    
    # Run server (debug=False to prevent process duplication)
    socketio.run(app, 
                 host='0.0.0.0', 
                 port=1337, 
                 debug=False,
                 use_reloader=False)
