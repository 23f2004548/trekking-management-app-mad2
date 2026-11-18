import os
from datetime import timedelta

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BACKEND_DIR, "instance", "trekking.db")

class Config():
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class LocalDevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH.replace(os.sep, '/')}"
    JWT_SECRET_KEY = 'tma_v2_super_secret_jwt_key_placement_satyam_2026_modern_app'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
    
    # Caching
    CACHE_TYPE = 'SimpleCache'
    CACHE_DEFAULT_TIMEOUT = 300
    
    # SMTP Config for MailHog
    SMTP_SERVER = "localhost"
    SMTP_PORT = 1025
    SENDER_EMAIL = "noreply@trekkingapp.com"
    SENDER_PASSWORD = ""
