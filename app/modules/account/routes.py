import logging

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


account_bp = Blueprint('account', __name__, template_folder='templates')


@account_bp.route('/account/profile')
@login_required
def profile():
    return render_template('profile.html')


@account_bp.route('/account/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not check_password_hash(current_user.password, current_password):
            flash("Current password is incorrect. No changes were made.", "danger")
            return render_template('change_password.html')

        if len(new_password) < 8:
            flash("New password must be at least 8 characters.", "danger")
            return render_template('change_password.html')

        if new_password != confirm_password:
            flash("New password and confirmation do not match.", "danger")
            return render_template('change_password.html')

        current_user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
        db.session.commit()
        logging.info(f"SECURITY AUDIT: User '{current_user.username}' changed their own password.")
        flash("Your password has been updated successfully.", "success")
        return redirect(url_for('account.profile'))

    return render_template('change_password.html')
