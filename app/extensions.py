from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache

db = SQLAlchemy()
csrf = CSRFProtect()
cache = Cache()

login_manager = LoginManager()
login_manager.login_view = 'auth.login' 

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["1000 per day", "300 per hour"],
    storage_uri="memory://"
)
