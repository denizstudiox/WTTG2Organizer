"""
WTTG2 Organizer - Application Factory
Creates and configures the Flask application instance with SocketIO support.
"""
from flask import Flask
from flask_socketio import SocketIO

# Initialize SocketIO (will be bound to app in create_app)
socketio = SocketIO()


def create_app(config_name='default'):
    """
    Application factory pattern.
    Creates and configures Flask app with SocketIO.
    
    Args:
        config_name: Configuration to use ('default', 'development', 'production')
    
    Returns:
        Flask application instance
    """
    # Create Flask app
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    # Load configuration
    from app.config import config
    app.config.from_object(config[config_name])
    
    # Initialize SocketIO with app
    socketio.init_app(app, 
                      cors_allowed_origins="*",
                      logger=False,
                      engineio_logger=False)
    
    # Register blueprints
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    # Register SocketIO events
    from app import socket_handlers
    socket_handlers.register_handlers(socketio)
    
    return app
