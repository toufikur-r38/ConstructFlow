import logging

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db, limiter
from app.models import AVAILABLE_MODULES, User, UserModule
from app.utils.decorators import admin_required
from app.utils.pagination import get_pagination_args


admin_bp = Blueprint('admin', __name__, template_folder='templates')


def _password_matches_current_user(field_name='confirm_password'):
    return check_password_hash(current_user.password, request.form.get(field_name, ''))


def _selected_modules(form_data):
    module_names = set(form_data.getlist('modules'))
    return sorted(module_names.intersection(AVAILABLE_MODULES.keys()))


def _sync_user_modules(user, module_names):
    desired_modules = set(module_names)

    user.module_access[:] = [
        module
        for module in user.module_access
        if module.module_name in desired_modules
    ]

    existing_modules = {module.module_name for module in user.module_access}
    for module_name in sorted(desired_modules - existing_modules):
        user.module_access.append(UserModule(module_name=module_name))


def _render_edit_user(user, auth_error=False, form_data=None):
    selected_module_names = _selected_modules(form_data) if form_data else user.module_names()
    return render_template(
        'edit_user.html',
        user=user,
        auth_error=auth_error,
        form_data=form_data,
        available_modules=AVAILABLE_MODULES,
        selected_module_names=selected_module_names,
    )


def _render_register(form_data=None):
    page, per_page = get_pagination_args(request)
    selected_module_names = _selected_modules(form_data) if form_data else ['construction']
    pagination = (
        User.query
        .order_by(User.username.asc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )
    return render_template(
        'register.html',
        users=pagination.items,
        pagination=pagination,
        form_data=form_data,
        available_modules=AVAILABLE_MODULES,
        selected_module_names=selected_module_names,
    )


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
        module_names = _selected_modules(request.form)
        is_super_admin = current_user.can_manage_system() and request.form.get('is_super_admin') == '1'

        if not username or not password or not full_name or not role:
            flash("All fields are required.", "danger")
            return _render_register(request.form)

        valid_roles = ['admin', 'operator', 'viewer']
        if role not in valid_roles:
            flash("Invalid role selected.", "danger")
            return _render_register(request.form)

        if not module_names and not is_super_admin:
            flash("flash.select_user_module", "danger")
            return _render_register(request.form)

        user_exists = User.query.filter_by(username=username).first()
        if user_exists:
            flash("Username already taken. Please choose another.", "warning")
            return _render_register(request.form)

        hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(
            username=username,
            full_name=full_name,
            password=hashed_pw,
            role=role,
            is_super_admin=is_super_admin,
        )
        _sync_user_modules(new_user, module_names)

        db.session.add(new_user)
        db.session.commit()
        logging.info(f"ADMIN ACTION: '{current_user.username}' created a new {role} account for '{username}'")

        flash(f"User '{full_name}' created successfully as {role.upper()}!", "success")
        return redirect(url_for('admin.register'))

    return _render_register()


@admin_bp.route('/edit-user/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for('admin.register'))

    if user.is_super_admin and not current_user.can_manage_system():
        flash("flash.super_admin_edit_only", "danger")
        return redirect(url_for('admin.register'))

    if request.method == 'POST':
        confirm_password = request.form.get('confirm_password', '').strip()
        if not check_password_hash(current_user.password, confirm_password):
            return _render_edit_user(user, auth_error=True, form_data=request.form)

        full_name = request.form.get('full_name', '').strip()
        if full_name:
            user.full_name = full_name

        valid_roles = ['admin', 'operator', 'viewer']
        new_role = request.form.get('role')
        if new_role not in valid_roles:
            flash("Invalid role selected.", "danger")
            return _render_edit_user(user, auth_error=False, form_data=request.form)

        if user.id == current_user.id and new_role != 'admin':
            flash("You cannot remove your own Admin privileges.", "warning")
        else:
            user.role = new_role

        module_names = _selected_modules(request.form)
        new_is_super_admin = user.is_super_admin
        if current_user.can_manage_system():
            new_is_super_admin = request.form.get('is_super_admin') == '1'
            if user.id == current_user.id and not new_is_super_admin:
                new_is_super_admin = True
                flash("flash.cannot_remove_own_super_admin", "warning")

        if not module_names and not new_is_super_admin:
            flash("flash.select_user_module", "danger")
            return _render_edit_user(user, auth_error=False, form_data=request.form)

        user.is_super_admin = new_is_super_admin
        _sync_user_modules(user, module_names)

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

    return _render_edit_user(user, auth_error=False, form_data=None)


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
        if user.is_super_admin and not current_user.can_manage_system():
            flash("flash.super_admin_change_only", "danger")
            return redirect(url_for('admin.register'))

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
