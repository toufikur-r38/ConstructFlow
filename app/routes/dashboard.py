from flask import Blueprint,  render_template, request, redirect, url_for, flash
from flask_login import  login_required, current_user
from app.utils.dashboard_service import get_dashboard_math
from app.utils.decorators import admin_required
dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    # Check the logged-in user's role and redirect to the right function
    if current_user.role == 'admin':
        return redirect(url_for('dashboard.admin_dashboard'))
    elif current_user.role == 'operator':
        return redirect(url_for('dashboard.operator_dashboard'))
    else:
        return redirect(url_for('dashboard.viewer_dashboard'))

@dashboard_bp.route('/admin-dashboard')
@login_required
@admin_required
def admin_dashboard():
      
    data = get_dashboard_math()
    return render_template('admin_dashboard.html', 
                           running_count=data['running_count'], 
                           projects_in_danger=data['projects_in_danger'],
                           spent_today=data['spent_today'], 
                           spent_this_month=data['spent_this_month'],
                           project_stats=data['project_stats'])

#  OPERATOR DASHBOARD
@dashboard_bp.route('/operator-dashboard')
@login_required
def operator_dashboard():
    if current_user.role != 'operator' :
        return redirect(url_for('dashboard.index'))
        
    data = get_dashboard_math()
    return render_template('operator_dashboard.html', 
                           running_count=data['running_count'], 
                           projects_in_danger=data['projects_in_danger'],
                           spent_today=data['spent_today'], 
                           spent_this_month=data['spent_this_month'],
                           project_stats=data['project_stats'])
#  VIEWER DASHBOARD 
@dashboard_bp.route('/viewer-dashboard')
@login_required
def viewer_dashboard():
    if current_user.role != 'viewer' :
        return redirect(url_for('dashboard.index'))

    data = get_dashboard_math()
    return render_template('viewer_dashboard.html', 
                           running_count=data['running_count'], 
                           projects_in_danger=data['projects_in_danger'],
                           spent_today=data['spent_today'], 
                           spent_this_month=data['spent_this_month'],
                           project_stats=data['project_stats'])

