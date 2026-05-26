from functools import wraps
from flask import redirect, url_for, flash, request
from flask_login import current_user
import logging



def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.role != 'admin':
            logging.warning(f"SECURITY: '{current_user.username}' (Role: {current_user.role}) attempted unauthorized access to {request.path}")
            
            flash("Unauthorized. Admins only.", "danger")
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated

def write_access_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role not in ['admin', 'operator']:
            logging.warning(f"SECURITY: '{current_user.username}' (Role: {current_user.role}) attempted unauthorized write to {request.path}")
            flash("Unauthorized. Only Admins and Operators can modify data.", "danger")
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function

