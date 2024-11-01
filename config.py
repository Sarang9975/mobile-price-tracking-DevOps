import os

class Config:
    """Configuration class for the Mobile Price Predictor application."""
    
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # AWS Configuration
    AWS_REGION = os.environ.get('AWS_REGION', 'ap-south-1')
    SAGEMAKER_ENDPOINT = os.environ.get('SAGEMAKER_ENDPOINT', 'Custom-sklearn-model-2024-11-19-07-30-02')
    
    # Application Configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = 'static'
    
    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Feature Validation
    MIN_BATTERY_POWER = 0
    MAX_BATTERY_POWER = 10000
    MIN_RAM = 0
    MAX_RAM = 100000
    MIN_CLOCK_SPEED = 0.0
    MAX_CLOCK_SPEED = 10.0 