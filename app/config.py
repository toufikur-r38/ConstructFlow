import os
import secrets


def _truthy(value):
    return str(value).lower() in {'1', 'true', 'yes', 'on'}


def _is_development():
    return os.environ.get('FLASK_ENV') == 'development' or _truthy(os.environ.get('FLASK_DEBUG'))


class Config:
    IS_DEVELOPMENT = _is_development()

    # AUTHENTICATION 
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)

    # DATABASE ---
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if not DATABASE_URL and not IS_DEVELOPMENT:
        raise RuntimeError("DATABASE_URL is required outside development. Refusing to start with SQLite.")

    SQLALCHEMY_DATABASE_URI = DATABASE_URL or 'sqlite:///' + os.path.join(BASE_DIR, 'construction.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = (
        {
            'pool_pre_ping': True,
            'pool_recycle': 1800,
        }
        if SQLALCHEMY_DATABASE_URI.startswith('postgresql')
        else {}
    )

    # CACHE ---
    REDIS_URL = os.environ.get('REDIS_URL')
    CACHE_TYPE = os.environ.get('CACHE_TYPE') or ('RedisCache' if REDIS_URL else 'SimpleCache')
    CACHE_REDIS_URL = os.environ.get('CACHE_REDIS_URL') or REDIS_URL
    CACHE_DEFAULT_TIMEOUT = 300

    RATELIMIT_STORAGE_URI = os.environ.get('RATELIMIT_STORAGE_URI') or (REDIS_URL if REDIS_URL else 'memory://')
    if not IS_DEVELOPMENT and RATELIMIT_STORAGE_URI == 'memory://':
        raise RuntimeError("RATELIMIT_STORAGE_URI or REDIS_URL is required outside development.")

    SESSION_COOKIE_SECURE = not IS_DEVELOPMENT
    SESSION_COOKIE_HTTPONLY = True 
    SESSION_COOKIE_SAMESITE = 'Lax'
    REMEMBER_COOKIE_SECURE = not IS_DEVELOPMENT
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = 'Lax'
