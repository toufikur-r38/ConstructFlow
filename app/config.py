import os
import secrets

class Config:
    # AUTHENTICATION 
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)

    #DATABASE ---
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'construction.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    #CACHE ---
    CACHE_TYPE = 'SimpleCache'
    CACHE_DEFAULT_TIMEOUT = 300

    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV') != 'development' and os.environ.get('FLASK_DEBUG') != '1'
    SESSION_COOKIE_HTTPONLY = True 
    SESSION_COOKIE_SAMESITE = 'Lax'
