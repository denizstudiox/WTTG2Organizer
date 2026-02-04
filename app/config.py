"""
WTTG2 Organizer - Configuration
Centralized configuration for different environments.
"""
import os


class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'wttg2_secret_key_change_in_production'
    
    # Server settings
    HOST = '0.0.0.0'
    PORT = 1337
    
    # SocketIO settings
    ASYNC_MODE = 'threading'
    
    # Data file
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_FILE = os.path.join(BASE_DIR, 'data.json')


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = False  # Disable debug to prevent auto-reload and process duplication
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
