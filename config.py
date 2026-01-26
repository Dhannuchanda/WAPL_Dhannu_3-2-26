"""
Configuration for different environments
"""
import os

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY', '4912607a8134bfce8bc6f56c27071068ffd364ed38b905ccf61d69bb9d9df861')
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file upload

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    SESSION_FILE_DIR = '/tmp/flask_session'

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True

# Get environment
env = os.environ.get('FLASK_ENV', 'development').lower()

if env == 'production':
    config = ProductionConfig()
else:
    config = DevelopmentConfig()
