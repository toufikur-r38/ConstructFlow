import logging

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db, limiter
from app.models import User
from app.utils.decorators import admin_required


admin_bp = Blueprint('admin', __name__, template_folder='templates')


def _password_matches_current_user(field_name='confirm_password'):
    return check_password_hash(current_user.password, request.form.get(field_name, ''))


@admin_bp.route('/register', methods=['GET', 'POST'])
@login_required
@admin_required
@limiter.limit("5 per minute")
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        full_name = request.form.get('full_name', '').strip()
        password = request.form.get('password', '').strip()
        role = request.form.get('role', '').strip()

        if not username or not password or not full_name or not role:
            flash("All fields are required.", "danger")
            return redirect(url_for('admin.register'))

        valid_roles = ['admin', 'operator', 'viewer']
        if role not in valid_roles:
            flash("Invalid role selected.", "danger")
            return redirect(url_for('admin.register'))

        user_exists = User.query.filter_by(username=username).first()
        if user_exists:
            flash("Username already taken. Please choose another.", "warning")
            return redirect(url_for('admin.register'))

        hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(
            username=username,
            full_name=full_name,
            password=hashed_pw,
            role=role
        )

        db.session.add(new_user)
        db.session.commit()
        logging.info(f"ADMIN ACTION: '{current_user.username}' created a new {role} account for '{username}'")

        flash(f"User '{full_name}' created successfully as {role.upper()}!", "success")
        return redirect(url_for('admin.register'))

    all_users = User.query.all()
    return render_template('register.html', users=all_users)


@admin_bp.route('/edit-user/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for('admin.register'))

    if request.method == 'POST':
        confirm_password = request.form.get('confirm_password', '').strip()
        if not check_password_hash(current_user.password, confirm_password):
            return render_template('edit_user.html', user=user, auth_error=True)

        full_name = request.form.get('full_name', '').strip()
        if full_name:
            user.full_name = full_name

        valid_roles = ['admin', 'operator', 'viewer']
        new_role = request.form.get('role')
        if new_role not in valid_roles:
            flash("Invalid role selected.", "danger")
            return redirect(url_for('admin.edit_user', user_id=user_id))

        if user.id == current_user.id and new_role != 'admin':
            flash("You cannot remove your own Admin privileges.", "warning")
        else:
            user.role = new_role

        new_password = request.form.get('password', '').strip()
        if new_password:
            user.password = generate_password_hash(new_password, method='pbkdf2:sha256')

        db.session.commit()
        logging.info(
            f"SECURITY AUDIT: Admin '{current_user.username}' updated user profile configuration for "
            f"'{user.username}' - Assigned Privilege Level: {user.role.upper()}"
        )
        flash(f"User '{user.full_name}' updated successfully.", "success")
        return redirect(url_for('admin.register'))

    return render_template('edit_user.html', user=user, auth_error=False)


@admin_bp.route('/toggle-user-status/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(user_id):
    if user_id == current_user.id:
        flash("You cannot deactivate your own account.", "danger")
        return redirect(url_for('admin.register'))

    if not _password_matches_current_user():
        flash("Authentication failed. Incorrect password. No changes were made.", "danger")
        return redirect(url_for('admin.register'))

    user = db.session.get(User, user_id)
    if user:
        user.is_active = not user.is_active
        db.session.commit()
        status = "activated" if user.is_active else "deactivated"
        logging.info(
            f"SECURITY AUDIT: Admin '{current_user.username}' {status} user account: '{user.username}'"
        )
        flash(f"User '{user.full_name}' has been {status}.", "success")
    else:
        flash("User not found.", "danger")

    return redirect(url_for('admin.register'))
