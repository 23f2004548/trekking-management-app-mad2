class Config():
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class LocalDevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///trekking.db'
    JWT_SECRET_KEY = 'tma_v2_super_secret_jwt_key_placement_satyam_2026_modern_app'
    
    # Caching
    CACHE_TYPE = 'SimpleCache'
    CACHE_DEFAULT_TIMEOUT = 300
    
    # Celery & Redis
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'
    
    # SMTP Config for reminders / reports
    SMTP_SERVER = "localhost"
    SMTP_PORT = 1025
    SENDER_EMAIL = "noreply@trekkingapp.com"
    SENDER_PASSWORD = ""
