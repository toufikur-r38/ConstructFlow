from flask import Blueprint, render_template, redirect, url_for
from flask_login import  login_required, current_user
from app.modules.construction.services.dashboard_service import get_dashboard_math
from app.utils.decorators import admin_required, module_access_required
dashboard_bp = Blueprint('dashboard', __name__, template_folder='../templates')


def _render_dashboard(dashboard_mode):
    data = get_dashboard_math()
    return render_template(
        'dashboard.html',
        dashboard_mode=dashboard_mode,
        running_count=data['running_count'],
        projects_in_danger=data['projects_in_danger'],
        spent_today=data['spent_today'],
        spent_this_month=data['spent_this_month'],
        project_stats=data['project_stats'],
    )

@dashboard_bp.route('/')
@login_required
@module_access_required('construction')
def index():
    # Check the logged-in user's role and redirect to the right function
    if current_user.role == 'admin' or current_user.is_super_admin:
        return redirect(url_for('dashboard.admin_dashboard'))
    elif current_user.role == 'operator':
        return redirect(url_for('dashboard.operator_dashboard'))
    else:
        return redirect(url_for('dashboard.viewer_dashboard'))

@dashboard_bp.route('/admin-dashboard')
@login_required
@module_access_required('construction')
@admin_required
def admin_dashboard():
    return _render_dashboard('admin')

#  OPERATOR DASHBOARD
@dashboard_bp.route('/operator-dashboard')
@login_required
@module_access_required('construction')
def operator_dashboard():
    if current_user.role != 'operator' and not current_user.is_super_admin:
        return redirect(url_for('dashboard.index'))
    return _render_dashboard('operator')
#  VIEWER DASHBOARD 
@dashboard_bp.route('/viewer-dashboard')
@login_required
@module_access_required('construction')
def viewer_dashboard():
    if current_user.role != 'viewer' and not current_user.is_super_admin:
        return redirect(url_for('dashboard.index'))

    return _render_dashboard('viewer')
