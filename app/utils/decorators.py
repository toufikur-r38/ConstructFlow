from functools import wraps
from flask import redirect, url_for, flash, request
from flask_login import current_user
import logging



def module_access_required(module_name):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not current_user.has_module(module_name):
                logging.warning(
                    f"SECURITY: '{current_user.username}' (Role: {current_user.role}) "
                    f"attempted unauthorized module access to {request.path}"
                )
                flash("flash.unauthorized_module_access", "danger")
                return redirect(url_for('account.profile'))
            return f(*args, **kwargs)
        return decorated
    return decorator


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.role != 'admin' and not current_user.is_super_admin:
            logging.warning(f"SECURITY: '{current_user.username}' (Role: {current_user.role}) attempted unauthorized access to {request.path}")
            
            flash("Unauthorized. Admins only.", "danger")
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated

def write_access_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role not in ['admin', 'operator'] and not current_user.is_super_admin:
            logging.warning(f"SECURITY: '{current_user.username}' (Role: {current_user.role}) attempted unauthorized write to {request.path}")
            flash("Unauthorized. Only Admins and Operators can modify data.", "danger")
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function
