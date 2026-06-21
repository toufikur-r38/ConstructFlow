from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy.exc import OperationalError
from werkzeug.security import check_password_hash
import logging
from app.extensions import db, login_manager, limiter
from app.models import User
from app.utils.i18n import translate as t

auth_bp = Blueprint('auth', __name__, template_folder='templates')

@login_manager.user_loader
def load_user(user_id):
    try:
        return db.session.get(User, int(user_id))
    except (TypeError, ValueError):
        return None
    except OperationalError:
        db.session.rollback()
        logging.warning("Database connection failed while loading user; retrying once.", exc_info=True)
        return db.session.get(User, int(user_id))



@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        user = User.query.filter_by(username=username).first()
        if user and user.is_active and check_password_hash(user.password, password):
            login_user(user)
            logging.info(f"Successful login: User '{username}'")
            flash(t('Welcome back, {name}!', name=user.full_name), 'success')
            visible_modules = user.module_names()
            if user.is_super_admin or len(visible_modules) > 1:
                return redirect(url_for('module_hub'))
            if 'construction' not in visible_modules:
                return redirect(url_for('module_hub'))
            if user.role == 'admin':
                return redirect(url_for('dashboard.admin_dashboard'))
            elif user.role == 'operator':
                return redirect(url_for('dashboard.operator_dashboard'))
            else:
                return redirect(url_for('dashboard.viewer_dashboard'))

        elif user and not user.is_active:
            logging.warning(f"Failed login: Deactivated account '{username}' tried to access.")
            flash(t("Your account has been deactivated. Contact the Admin."), "danger")
        else:
            logging.warning(f"Failed login: Invalid credentials for username '{username}'.")
            flash(t('Invalid username or password.'), 'danger')
    return render_template('login.html', username=request.form.get('username', '').strip())
@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logging.info(f"User '{current_user.username}' logged out.")
    logout_user()
    return redirect(url_for('auth.login'))
