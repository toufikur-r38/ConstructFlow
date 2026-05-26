from datetime import datetime
import logging
from flask import Blueprint,  render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import func
from app.extensions import db, limiter
from app.models import DeletedLog, Project, CostEntry, User, EditLog, ProjectEditLog, ProjectDeletedLog, DropdownOption
from werkzeug.security import check_password_hash, generate_password_hash
import json
from decimal import Decimal, InvalidOperation
from app.extensions import cache
from app.utils.decorators import admin_required, write_access_required
from app.utils.dropdown_options import PROJECT_SECTOR, COST_TYPE, get_dropdown_options
admin_bp = Blueprint('admin', __name__)


OPTION_TYPE_LABELS = {
    PROJECT_SECTOR: 'Project Sector',
    COST_TYPE: 'Cost Type',
}


def _render_edit_project(project, auth_error=False):
    return render_template(
        'edit_project.html',
        project=project,
        auth_error=auth_error,
        sectors=get_dropdown_options(PROJECT_SECTOR),
    )


def _render_edit_cost(entry, projects=None, auth_error=False):
    return render_template(
        'edit_cost.html',
        entry=entry,
        projects=projects if projects is not None else Project.query.filter_by(is_void=False).all(),
        cost_types=get_dropdown_options(COST_TYPE),
        auth_error=auth_error,
    )


def _password_matches_current_user(field_name='confirm_password'):
    return check_password_hash(current_user.password, request.form.get(field_name, ''))




@admin_bp.route('/void-project/<int:project_id>', methods=['POST'])
@login_required
@admin_required
@limiter.limit("10 per minute")
def void_project(project_id):
    
    project = db.session.get(Project, project_id)
    if not project:
        flash("Project not found.", "warning")
        return redirect(url_for('projects.view_projects'))

    if project.is_void:
        flash("This project is already voided.", "info")
        return redirect(url_for('projects.view_projects'))

    void_reason = request.form.get('reason', '').strip()
    confirm_password = request.form.get('confirm_password', '')

    if not void_reason:
        flash("A reason for voiding is required.", "warning")
        return redirect(url_for('projects.view_projects'))

    if not check_password_hash(current_user.password, confirm_password):
        flash("Authentication Failed! Incorrect password. No changes were made.", "danger")
        return redirect(url_for('projects.view_projects'))

    try:
        before_data = {
            "project_name": project.project_name,
            "contract_price": str(project.contract_price),
            "sector": project.sector,
            "linked_costs_count": len(project.costs),
            "void_reason": void_reason
        }

        project.is_void = True
        
        
        void_count = 0
        for entry in project.costs:
            if not entry.is_void:
                entry.is_void = True
                entry.remarks = f"[PROJECT VOIDED] {entry.remarks or ''}".strip()
                void_count += 1

        deletion_log = ProjectDeletedLog(
            project_id=project.id,
            deleted_by=current_user.id,
            void_reason=void_reason,
            costs_voided_count=void_count,
            project_snapshot=json.dumps(before_data)
        )
        db.session.add(deletion_log)

        try:
            db.session.commit()
            logging.info(f"ADMIN ACTION: '{current_user.username}' voided Project ID {project.id}. Reason: {void_reason}")
            cache.delete('dashboard_math_data')
            flash(f"Project '{project.project_name}' and {void_count} linked cost entries have been successfully voided.", "success")
        except Exception as e:
            logging.error(f"ERROR VOIDING PROJECT ID {project_id}: {str(e)}")
            db.session.rollback()
            flash(f"An error occurred during the voiding process: {str(e)}", "danger")
    except Exception as e:
        logging.error(f"ERROR VOIDING PROJECT ID {project_id}: {str(e)}") 
        db.session.rollback()
        flash(f"An error occurred during the voiding process: {str(e)}", "danger")

    return redirect(url_for('projects.view_projects'))

@admin_bp.route('/restore-project/<int:id>', methods=['POST'])
@login_required
@admin_required
def restore_project(id):
    project = db.get_or_404(Project, id)

    if not _password_matches_current_user():
        flash("Authentication failed. Incorrect password. No changes were made.", "danger")
        return redirect(url_for('admin.all_removed_projects'))

    project.is_void = False
    
    restored_costs_count = 0
    for entry in project.costs:
        if entry.is_void and entry.remarks and entry.remarks.startswith("[PROJECT VOIDED]"):
            entry.is_void = False
            # Remove the void tag so it looks perfectly normal again
            entry.remarks = entry.remarks.replace("[PROJECT VOIDED] ", "", 1)
            restored_costs_count += 1
            
    deleted_log = ProjectDeletedLog.query.filter_by(project_id=id).first()
    if deleted_log:
        db.session.delete(deleted_log)
        
    db.session.commit()
    cache.delete('dashboard_math_data')
    logging.info(
        f"ADMIN ACTION: '{current_user.username}' restored Project ID {project.id} "
        f"('{project.project_name}') with {restored_costs_count} linked costs."
    )
    flash(f"Project '{project.project_name}' and {restored_costs_count} linked costs have been successfully restored.", "success")
    return redirect(url_for('admin.all_removed_projects'))


VALID_STATUSES = ['Running', 'Completed', 'On Hold']
 
 
def _project_snapshot(project: Project) -> dict:
    return {
        "project_name":      project.project_name,
        "sector":            project.sector,
        "firm_name":         project.firm_name,
        "tender_id":         project.tender_id,
        "noa_date":          project.noa_date.isoformat() if project.noa_date else None,
        "work_order_year":   project.work_order_year,
        "status":            project.status,
        "contract_price":    str(project.contract_price),   # Decimal â†’ str for JSON
        "address":           project.address,
        "additional_details": project.additional_details,
    }
 
@admin_bp.route('/edit-project/<int:project_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_project(project_id):
    project = db.session.get(Project, project_id)
    if not project:
        flash("Project not found.", "warning")
        return redirect(url_for('projects.view_projects'))
 
    if request.method == 'POST':
 
        confirm_password = request.form.get('confirm_password', '')
        if not check_password_hash(current_user.password, confirm_password):
            return _render_edit_project(project, auth_error=True)
 
        project_name       = request.form.get('project_name', '').strip()
        sector             = request.form.get('sector', '').strip()
        firm_name          = request.form.get('firm_name', '').strip()
        tender_id          = request.form.get('tender_id', '').strip()
        work_order_year    = request.form.get('work_order_year', '').strip()
        address            = request.form.get('address', '').strip()
        additional_details = request.form.get('additional_details', '').strip()
        status             = request.form.get('status', '').strip()
        noa_str            = request.form.get('noa_date', '').strip()
        price_str          = request.form.get('contract_price', '').strip()
 
 
        if not project_name:
            flash("Project name is required.", "danger")
            return _render_edit_project(project)
 
        if status not in VALID_STATUSES:
            flash(f"Invalid status. Allowed values: {', '.join(VALID_STATUSES)}.", "danger")
            return _render_edit_project(project)

        allowed_sectors = get_dropdown_options(PROJECT_SECTOR)
        if sector not in allowed_sectors and sector != project.sector:
            flash("Please select a valid project sector from the managed dropdown list.", "danger")
            return _render_edit_project(project)
 
        parsed_noa = None
        if noa_str:
            try:
                parsed_noa = datetime.strptime(noa_str, '%Y-%m-%d').date()
            except ValueError:
                flash("Invalid date format. Please use YYYY-MM-DD.", "danger")
                return _render_edit_project(project)
 
        parsed_price = Decimal('0')
        if price_str:
            try:
                parsed_price = Decimal(price_str)
                if parsed_price < 0:
                    raise ValueError("Price cannot be negative.")
            except (InvalidOperation, ValueError):
                flash("Invalid contract price. Please enter a positive number.", "danger")
                return _render_edit_project(project)
 
        before_data   = _project_snapshot(project)
        original_name = project.project_name
 
        project.project_name       = project_name
        project.sector             = sector
        project.firm_name          = firm_name
        project.tender_id          = tender_id
        project.noa_date           = parsed_noa
        project.work_order_year    = work_order_year
        project.status             = status
        project.contract_price     = parsed_price
        project.address            = address
        project.additional_details = additional_details
 
        after_data = _project_snapshot(project)
 
        edit_log = ProjectEditLog(
            project_id=project.id,
            project_name_snapshot=original_name,
            changed_by=current_user.id,
            before_snapshot=json.dumps(before_data),
            after_snapshot=json.dumps(after_data),
        )
        db.session.add(edit_log)
 
        try:
            db.session.commit()
            cache.delete('dashboard_math_data')
        except Exception as e:
            db.session.rollback()
            logging.error(
                f"ERROR editing Project ID {project_id} "
                f"by '{current_user.username}': {e}"
            )
            flash("A database error occurred. No changes were saved.", "danger")
            return _render_edit_project(project)
 
        logging.info(
            f"ADMIN ACTION: '{current_user.username}' edited Project ID {project_id} "
            f"(was: '{original_name}')"
        )
        flash(
            f"Project '{project.project_name}' updated and audit log saved.",
            "success"
        )
        return redirect(url_for('projects.view_projects'))
 
    return _render_edit_project(project)
 
@admin_bp.route('/void-cost/<int:cost_id>', methods=['POST'])
@login_required
@admin_required
@limiter.limit("15 per minute")
def void_cost(cost_id):
    
    entry = db.session.get(CostEntry, cost_id)
    if not entry:
        flash("Entry not found.", "danger")
        return redirect(url_for('costs.view_costs'))
    
    if entry.is_void:
        flash("This entry has already been voided.", "warning")
        return redirect(url_for('costs.view_costs'))

    reason = request.form.get('void_reason', '').strip()
    if not reason:
        flash("A reason is required to void an entry.", "danger")
        return redirect(url_for('costs.view_costs'))

    confirm_password = request.form.get('confirm_password', '')
    if not check_password_hash(current_user.password, confirm_password):
        flash("Authentication failed. Incorrect password. No changes were made.", "danger")
        return redirect(url_for('costs.view_costs'))

    data_to_save = {
        "date": entry.date.strftime('%Y-%m-%d') if entry.date else None,
        "category": entry.cost_type,
        "quantity": str(entry.quantity or 0),
        "unit_rate": str(entry.unit_rate or 0),
        "total_amount": str(entry.total_amount or 0),
        "remarks": entry.remarks
    }
    
    void_log = DeletedLog(
        cost_id=entry.id,
        deleted_by=current_user.id,
        project_id=entry.project_id,
        project_name_snapshot=entry.project.project_name,
        data_snapshot=json.dumps(data_to_save),
        void_reason=reason
    )
    
    db.session.add(void_log)
    entry.is_void = True
    try:
        db.session.commit()
        cache.delete('dashboard_math_data')
        logging.info(
            f"ADMIN ACTION: '{current_user.username}' voided Cost ID {entry.id} "
            f"(Project: '{entry.project.project_name if entry.project else 'Unknown'}', "
            f"Type: '{entry.cost_type}', Total: {entry.total_amount}). Reason: {reason}"
        )
        flash(f"Entry from {entry.date} has been successfully voided.", "success")
    except Exception as e:
        logging.error(f"ERROR VOIDING COST ENTRY ID {cost_id}: {str(e)}")
        db.session.rollback()
        flash(f"An error occurred while voiding the cost entry: {str(e)}", "danger")
    return redirect(url_for('costs.view_costs'))

@admin_bp.route('/restore-cost/<int:id>', methods=['POST'])
@login_required
@admin_required
def restore_cost(id):
    cost = db.get_or_404(CostEntry, id)

    if not _password_matches_current_user():
        flash("Authentication failed. Incorrect password. No changes were made.", "danger")
        return redirect(url_for('admin.all_removed_costs'))

    cost.is_void = False
    
    if cost.remarks and cost.remarks.startswith("[PROJECT VOIDED] "):
        cost.remarks = cost.remarks.replace("[PROJECT VOIDED] ", "", 1)
    deleted_log = DeletedLog.query.filter_by(cost_id=id).first()
    if deleted_log:
        db.session.delete(deleted_log)
    db.session.commit()
    cache.delete('dashboard_math_data')
    logging.info(
        f"ADMIN ACTION: '{current_user.username}' restored Cost ID {cost.id} "
        f"(Project: '{cost.project.project_name if cost.project else 'Unknown'}', "
        f"Type: '{cost.cost_type}', Total: {cost.total_amount})."
    )
    flash("Cost entry has been successfully restored.", "success")
    return redirect(url_for('admin.all_removed_costs'))
@admin_bp.route('/edit-cost/<int:cost_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_cost(cost_id):
    entry = db.session.get(CostEntry, cost_id)
    if not entry:
        flash("Cost entry not found.", "danger")
        return redirect(url_for('costs.view_costs'))
 
    if request.method == 'POST':
 
        admin_password = request.form.get('admin_password', '')
        if not check_password_hash(current_user.password, admin_password):
            return _render_edit_cost(entry, auth_error=True)

        date_str    = request.form.get('date', '').strip()
        project_id_str = request.form.get('project_id', '').strip()
        cost_type   = request.form.get('cost_type', '').strip()
        qty_str     = request.form.get('quantity', '').strip()
        rate_str    = request.form.get('unit_rate', '').strip()
        remarks     = request.form.get('remarks', '').strip()
 
 
        if not date_str:
            flash("Date is required.", "danger")
            return _render_edit_cost(entry)
 
        try:
            parsed_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            flash("Invalid date format. Please use YYYY-MM-DD.", "danger")
            return _render_edit_cost(entry)
 
        try:
            parsed_project_id = int(project_id_str)
        except (ValueError, TypeError):
            flash("Invalid project selected.", "danger")
            return _render_edit_cost(entry)
 
        target_project = db.session.get(Project, parsed_project_id)
        if not target_project:
            flash("Selected project does not exist.", "danger")
            return _render_edit_cost(entry)
 
        # 2c. Cost type â€” required
        if not cost_type:
            flash("Cost type is required.", "danger")
            return _render_edit_cost(entry)

        allowed_cost_types = get_dropdown_options(COST_TYPE)
        if cost_type not in allowed_cost_types and cost_type != entry.cost_type:
            flash("Please select a valid cost type from the managed dropdown list.", "danger")
            return _render_edit_cost(entry)
 
        try:
            parsed_qty = Decimal(qty_str) if qty_str else Decimal('0')
            if parsed_qty < 0:
                raise ValueError("Quantity cannot be negative.")
        except (InvalidOperation, ValueError):
            flash("Invalid quantity. Please enter a positive number.", "danger")
            return _render_edit_cost(entry)
 
        try:
            parsed_rate = Decimal(rate_str) if rate_str else Decimal('0')
        except (InvalidOperation):
            flash("Invalid unit rate. Please enter a positive number.", "danger")
            return _render_edit_cost(entry)
 
        parsed_total = parsed_qty * parsed_rate
 
        before_data = {
            "date":         entry.date.strftime('%Y-%m-%d') if entry.date else None,
            "project":      entry.project.project_name if entry.project else None,
            "category":     entry.cost_type,
            "quantity":     str(entry.quantity or 0),    # str() keeps Decimal precision
            "unit_rate":    str(entry.unit_rate or 0),
            "total_amount": str(entry.total_amount or 0),
            "remarks":      entry.remarks,
        }
        original_project_name = entry.project.project_name if entry.project else None
 
        entry.date       = parsed_date
        entry.project_id = parsed_project_id
        entry.cost_type  = cost_type
        entry.quantity   = parsed_qty
        entry.unit_rate  = parsed_rate
        entry.total_amount = parsed_total
        entry.remarks    = remarks
 
        after_data = {
            "date":         entry.date.strftime('%Y-%m-%d'),
            "project":      target_project.project_name,
            "category":     entry.cost_type,
            "quantity":     str(entry.quantity),
            "unit_rate":    str(entry.unit_rate),
            "total_amount": str(entry.total_amount),
            "remarks":      entry.remarks,
        }
 
        edit_log = EditLog(
            cost_id=entry.id,
            changed_by=current_user.id,
            project_id=entry.project_id,
            project_name_snapshot=original_project_name,  # original, not new
            before_snapshot=json.dumps(before_data),
            after_snapshot=json.dumps(after_data),
        )
        db.session.add(edit_log)
 
        try:
            db.session.commit()
            cache.delete('dashboard_math_data')
        except Exception as e:
            db.session.rollback()
            logging.error(
                f"ERROR editing Cost ID {cost_id} "
                f"by '{current_user.username}': {e}"
            )
            flash("A database error occurred. No changes were saved.", "danger")
            return _render_edit_cost(entry)
 
        logging.info(
            f"ADMIN ACTION: '{current_user.username}' edited Cost ID {cost_id} "
            f"(Project: '{original_project_name}', Total: {parsed_total})"
        )
        flash("Changes saved and audit log updated.", "success")
        return redirect(url_for('costs.view_costs'))
 
    # â”€â”€ GET â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    return _render_edit_cost(entry)
 

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

        VALID_ROLES = ['admin', 'operator', 'viewer']
        if role not in VALID_ROLES:
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

        VALID_ROLES = ['admin', 'operator', 'viewer']
        new_role = request.form.get('role')
        if new_role not in VALID_ROLES:
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
            f"'{user.username}' â€” Assigned Privilege Level: {user.role.upper()}"
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

@admin_bp.route('/audit-log')
@login_required
@admin_required
def audit_log():
   
    
    voided_costs = DeletedLog.query\
        .order_by(DeletedLog.deleted_at.desc()).limit(10).all()
    
    voided_projects = ProjectDeletedLog.query\
        .order_by(ProjectDeletedLog.deleted_at.desc()).limit(10).all()
    
    edited_costs = EditLog.query\
        .order_by(EditLog.changed_at.desc()).limit(10).all()
    
    edited_projects = ProjectEditLog.query\
        .order_by(ProjectEditLog.changed_at.desc()).limit(10).all()
    
    return render_template('audit_log.html',
        voided_costs=voided_costs,
        voided_projects=voided_projects,
        edited_costs=edited_costs,
        edited_projects=edited_projects,
        voided_costs_count=DeletedLog.query.count(),
        voided_projects_count=ProjectDeletedLog.query.count(),
        edited_costs_count=EditLog.query.count(),
        edited_projects_count=ProjectEditLog.query.count()
    )

# --- Routes to render the HTML pages ---
@admin_bp.route('/all-removed-projects')
@login_required
@admin_required
def all_removed_projects():
    voided_projects = Project.query.filter_by(is_void=True).all()
    return render_template('all_removed_projects.html', projects=voided_projects)

@admin_bp.route('/all-removed-costs')
@login_required
@admin_required
def all_removed_costs():
    voided_costs = CostEntry.query.filter_by(is_void=True).all()
    return render_template('all_removed_costs.html', costs=voided_costs)

@admin_bp.route('/all-edited-costs')
@login_required
@admin_required
def all_edited_costs():
    # Fetch all logs, order by newest first
    edited_costs = EditLog.query.order_by(EditLog.changed_at.desc()).all()
    return render_template('all_edited_costs.html', edited_costs=edited_costs)

@admin_bp.route('/all-edited-projects')
@login_required
@admin_required
def all_edited_projects():
    # Fetch all logs, order by newest first
    edited_projects = ProjectEditLog.query.order_by(ProjectEditLog.changed_at.desc()).all()
    return render_template('all_edited_projects.html', edited_projects=edited_projects)


@admin_bp.route('/dropdown-options', methods=['GET', 'POST'])
@login_required
@write_access_required
def dropdown_options():
    if request.method == 'POST':
        option_type = request.form.get('option_type', '').strip()
        name = request.form.get('name', '').strip()

        if option_type not in OPTION_TYPE_LABELS:
            flash("Invalid dropdown type selected.", "danger")
            return redirect(url_for('admin.dropdown_options'))

        if not name:
            flash("Option name is required.", "danger")
            return redirect(url_for('admin.dropdown_options'))

        if len(name) > 100:
            flash("Option name must be 100 characters or fewer.", "danger")
            return redirect(url_for('admin.dropdown_options'))

        existing = DropdownOption.query.filter(
            DropdownOption.option_type == option_type,
            func.lower(DropdownOption.name) == name.lower()
        ).first()
        if existing:
            flash(f"{OPTION_TYPE_LABELS[option_type]} '{name}' already exists.", "warning")
            return redirect(url_for('admin.dropdown_options'))

        db.session.add(DropdownOption(
            option_type=option_type,
            name=name,
            created_by=current_user.id,
        ))
        db.session.commit()
        logging.info(
            f"ADMIN ACTION: '{current_user.username}' added dropdown option "
            f"'{name}' to {OPTION_TYPE_LABELS[option_type]}."
        )
        flash(f"{OPTION_TYPE_LABELS[option_type]} '{name}' added.", "success")
        return redirect(url_for('admin.dropdown_options'))

    sectors = DropdownOption.query.filter_by(option_type=PROJECT_SECTOR).order_by(DropdownOption.name.asc()).all()
    cost_types = DropdownOption.query.filter_by(option_type=COST_TYPE).order_by(DropdownOption.name.asc()).all()

    return render_template(
        'dropdown_options.html',
        sectors=sectors,
        cost_types=cost_types,
    )


@admin_bp.route('/dropdown-options/<int:option_id>/delete', methods=['POST'])
@login_required
@write_access_required
def delete_dropdown_option(option_id):
    option = db.get_or_404(DropdownOption, option_id)
    label = OPTION_TYPE_LABELS.get(option.option_type, 'Dropdown option')
    name = option.name

    db.session.delete(option)
    db.session.commit()
    logging.info(
        f"ADMIN ACTION: '{current_user.username}' removed dropdown option "
        f"'{name}' from {label}."
    )
    flash(f"{label} '{name}' removed from future dropdowns.", "success")
    return redirect(url_for('admin.dropdown_options'))

