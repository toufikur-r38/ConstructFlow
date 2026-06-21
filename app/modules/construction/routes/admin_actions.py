from datetime import datetime
import logging
from flask import Blueprint,  render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import func
from app.extensions import db, limiter
from app.models import DeletedLog, Project, CostEntry, EditLog, ProjectEditLog, ProjectDeletedLog, DropdownOption
from werkzeug.security import check_password_hash
import json
from decimal import Decimal, InvalidOperation
from app.extensions import cache
from app.utils.decorators import admin_required, module_access_required, write_access_required
from app.utils.db_errors import friendly_database_error
from app.utils.pagination import DEFAULT_LOG_PER_PAGE, get_pagination_args
from app.modules.construction.utils.dropdown_options import PROJECT_SECTOR, COST_TYPE, get_dropdown_options
construction_admin_bp = Blueprint('construction_admin', __name__, template_folder='../templates')


OPTION_TYPE_LABELS = {
    PROJECT_SECTOR: 'Project Sector',
    COST_TYPE: 'Cost Type',
}

PROJECT_VOID_REMARK_PREFIX = "[PROJECT VOIDED]"


def _render_edit_project(project, auth_error=False, form_data=None):
    return render_template(
        'edit_project.html',
        project=project,
        auth_error=auth_error,
        form_data=form_data,
        sectors=get_dropdown_options(PROJECT_SECTOR),
    )


def _render_edit_cost(entry, projects=None, auth_error=False, form_data=None):
    return render_template(
        'edit_cost.html',
        entry=entry,
        projects=projects if projects is not None else Project.query.filter_by(is_void=False).all(),
        cost_types=get_dropdown_options(COST_TYPE),
        auth_error=auth_error,
        form_data=form_data,
    )


def _password_matches_current_user(field_name='confirm_password'):
    return check_password_hash(current_user.password, request.form.get(field_name, ''))


def _project_voided_remark(remark):
    return f"{PROJECT_VOID_REMARK_PREFIX} {remark or ''}".strip()


def _restore_project_voided_remark(remark):
    if remark == PROJECT_VOID_REMARK_PREFIX:
        return None
    if remark and remark.startswith(f"{PROJECT_VOID_REMARK_PREFIX} "):
        restored = remark.replace(f"{PROJECT_VOID_REMARK_PREFIX} ", "", 1)
        return restored or None
    return remark




@construction_admin_bp.route('/void-project/<int:project_id>', methods=['POST'])
@login_required
@module_access_required('construction')
@write_access_required
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
        voided_cost_snapshots = []
        for entry in project.costs:
            if not entry.is_void:
                voided_cost_snapshots.append({
                    "id": entry.id,
                    "remarks": entry.remarks,
                })
                entry.is_void = True
                entry.remarks = _project_voided_remark(entry.remarks)
                void_count += 1

        before_data["voided_costs"] = voided_cost_snapshots

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

@construction_admin_bp.route('/restore-project/<int:id>', methods=['POST'])
@login_required
@module_access_required('construction')
@admin_required
def restore_project(id):
    project = db.get_or_404(Project, id)

    if not _password_matches_current_user():
        flash("Authentication failed. Incorrect password. No changes were made.", "danger")
        return redirect(url_for('construction_admin.all_removed_projects'))

    deleted_log = (
        ProjectDeletedLog.query
        .filter_by(project_id=id)
        .order_by(ProjectDeletedLog.deleted_at.desc())
        .first()
    )
    original_cost_remarks = {}
    if deleted_log:
        try:
            project_snapshot = json.loads(deleted_log.project_snapshot or '{}')
        except (TypeError, json.JSONDecodeError):
            project_snapshot = {}

        for cost_snapshot in project_snapshot.get("voided_costs", []):
            cost_id = cost_snapshot.get("id")
            if cost_id is not None:
                original_cost_remarks[int(cost_id)] = cost_snapshot.get("remarks")

    project.is_void = False

    restored_costs_count = 0
    for entry in project.costs:
        has_saved_remark = entry.id in original_cost_remarks
        has_project_void_tag = (
            not original_cost_remarks
            and bool(entry.remarks and entry.remarks.startswith(PROJECT_VOID_REMARK_PREFIX))
        )
        if entry.is_void and (has_saved_remark or has_project_void_tag):
            entry.is_void = False
            entry.remarks = (
                original_cost_remarks[entry.id]
                if has_saved_remark
                else _restore_project_voided_remark(entry.remarks)
            )
            restored_costs_count += 1

    if deleted_log:
        db.session.delete(deleted_log)
        
    db.session.commit()
    cache.delete('dashboard_math_data')
    logging.info(
        f"ADMIN ACTION: '{current_user.username}' restored Project ID {project.id} "
        f"('{project.project_name}') with {restored_costs_count} linked costs."
    )
    flash(f"Project '{project.project_name}' and {restored_costs_count} linked costs have been successfully restored.", "success")
    return redirect(url_for('construction_admin.all_removed_projects'))


VALID_STATUSES = ['Running', 'Completed', 'On Hold']
MAX_PROJECT_NAME_LEN = 200
MAX_PROJECT_SECTOR_LEN = 100
MAX_PROJECT_FIRM_LEN = 200
MAX_PROJECT_TENDER_LEN = 100
MAX_PROJECT_ADDR_LEN = 500
MAX_COST_TYPE_LEN = 50
MAX_COST_REMARKS_LEN = 500
PROJECT_TEXT_LIMITS = (
    ("Project name", MAX_PROJECT_NAME_LEN),
    ("Sector", MAX_PROJECT_SECTOR_LEN),
    ("Firm name", MAX_PROJECT_FIRM_LEN),
    ("Tender ID", MAX_PROJECT_TENDER_LEN),
    ("Address", MAX_PROJECT_ADDR_LEN),
)
COST_TEXT_LIMITS = (
    ("Cost type", MAX_COST_TYPE_LEN),
    ("Remarks", MAX_COST_REMARKS_LEN),
)
 
 
def _project_snapshot(project: Project) -> dict:
    return {
        "project_name":      project.project_name,
        "sector":            project.sector,
        "firm_name":         project.firm_name,
        "tender_id":         project.tender_id,
        "noa_date":          project.noa_date.isoformat() if project.noa_date else None,
        "completion_date":   project.completion_date.isoformat() if project.completion_date else None,
        "work_order_year":   project.work_order_year,
        "status":            project.status,
        "contract_price":    str(project.contract_price),   # Decimal → str for JSON
        "address":           project.address,
        "additional_details": project.additional_details,
    }
 
@construction_admin_bp.route('/edit-project/<int:project_id>', methods=['GET', 'POST'])
@login_required
@module_access_required('construction')
@write_access_required
def edit_project(project_id):
    project = db.session.get(Project, project_id)
    if not project:
        flash("Project not found.", "warning")
        return redirect(url_for('projects.view_projects'))
 
    if request.method == 'POST':
 
        project_name       = request.form.get('project_name', '').strip()
        sector             = request.form.get('sector', '').strip()
        firm_name          = request.form.get('firm_name', '').strip()
        tender_id          = request.form.get('tender_id', '').strip()
        work_order_year    = request.form.get('work_order_year', '').strip()
        address            = request.form.get('address', '').strip()
        additional_details = request.form.get('additional_details', '').strip()
        status             = request.form.get('status', '').strip()
        noa_str            = request.form.get('noa_date', '').strip()
        completion_str     = request.form.get('completion_date', '').strip()
        price_str          = request.form.get('contract_price', '').strip()
 
 
        if not project_name:
            flash("Project name is required.", "danger")
            return _render_edit_project(project, form_data=request.form)

        if len(project_name) > MAX_PROJECT_NAME_LEN:
            flash(f"Project name must be {MAX_PROJECT_NAME_LEN} characters or fewer.", "danger")
            return _render_edit_project(project, form_data=request.form)

        if len(sector) > MAX_PROJECT_SECTOR_LEN:
            flash(f"Sector must be {MAX_PROJECT_SECTOR_LEN} characters or fewer.", "danger")
            return _render_edit_project(project, form_data=request.form)

        if len(firm_name) > MAX_PROJECT_FIRM_LEN:
            flash(f"Firm name must be {MAX_PROJECT_FIRM_LEN} characters or fewer.", "danger")
            return _render_edit_project(project, form_data=request.form)

        if len(tender_id) > MAX_PROJECT_TENDER_LEN:
            flash(f"Tender ID must be {MAX_PROJECT_TENDER_LEN} characters or fewer.", "danger")
            return _render_edit_project(project, form_data=request.form)

        if len(address) > MAX_PROJECT_ADDR_LEN:
            flash(f"Address must be {MAX_PROJECT_ADDR_LEN} characters or fewer.", "danger")
            return _render_edit_project(project, form_data=request.form)
 
        if status not in VALID_STATUSES:
            flash(f"Invalid status. Allowed values: {', '.join(VALID_STATUSES)}.", "danger")
            return _render_edit_project(project, form_data=request.form)

        allowed_sectors = get_dropdown_options(PROJECT_SECTOR)
        if sector not in allowed_sectors and sector != project.sector:
            flash("Please select a valid project sector from the managed dropdown list.", "danger")
            return _render_edit_project(project, form_data=request.form)
 
        parsed_noa = None
        if noa_str:
            try:
                parsed_noa = datetime.strptime(noa_str, '%Y-%m-%d').date()
            except ValueError:
                flash("Invalid date format. Please use YYYY-MM-DD.", "danger")
                return _render_edit_project(project, form_data=request.form)

        parsed_completion = None
        if completion_str:
            try:
                parsed_completion = datetime.strptime(completion_str, '%Y-%m-%d').date()
            except ValueError:
                flash("Invalid completion date format. Please use YYYY-MM-DD.", "danger")
                return _render_edit_project(project, form_data=request.form)

        if status == 'Completed' and not parsed_completion:
            flash("Completion date is required when project status is Completed.", "danger")
            return _render_edit_project(project, form_data=request.form)

        if status != 'Completed':
            parsed_completion = None
 
        parsed_price = Decimal('0')
        if price_str:
            try:
                parsed_price = Decimal(price_str)
                if parsed_price < 0:
                    raise ValueError("Price cannot be negative.")
            except (InvalidOperation, ValueError):
                flash("Invalid contract price. Please enter a positive number.", "danger")
                return _render_edit_project(project, form_data=request.form)

        if (
            project.project_name == project_name
            and (project.sector or '') == sector
            and (project.firm_name or '') == firm_name
            and (project.tender_id or '') == tender_id
            and project.noa_date == parsed_noa
            and (project.work_order_year or '') == work_order_year
            and (project.address or '') == address
            and (project.additional_details or '') == additional_details
            and project.status == status
            and project.completion_date == parsed_completion
            and (project.contract_price or Decimal('0')) == parsed_price
        ):
            flash("No changes detected. Nothing was updated.", "info")
            return _render_edit_project(project, form_data=request.form)

        confirm_password = request.form.get('confirm_password', '')
        if not check_password_hash(current_user.password, confirm_password):
            return _render_edit_project(project, auth_error=True, form_data=request.form)
 
        before_data   = _project_snapshot(project)
        original_name = project.project_name
 
        project.project_name       = project_name
        project.sector             = sector
        project.firm_name          = firm_name
        project.tender_id          = tender_id
        project.noa_date           = parsed_noa
        project.completion_date    = parsed_completion
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
            flash(friendly_database_error(e, "save your project changes", PROJECT_TEXT_LIMITS), "danger")
            return _render_edit_project(project, form_data=request.form)
 
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
 
@construction_admin_bp.route('/void-cost/<int:cost_id>', methods=['POST'])
@login_required
@module_access_required('construction')
@write_access_required
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

@construction_admin_bp.route('/restore-cost/<int:id>', methods=['POST'])
@login_required
@module_access_required('construction')
@admin_required
def restore_cost(id):
    cost = db.get_or_404(CostEntry, id)

    if not _password_matches_current_user():
        flash("Authentication failed. Incorrect password. No changes were made.", "danger")
        return redirect(url_for('construction_admin.all_removed_costs'))

    if cost.project and cost.project.is_void:
        flash(
            f"First restore the project '{cost.project.project_name}', then restore this cost.",
            "warning"
        )
        return redirect(url_for('construction_admin.all_removed_costs'))

    cost.is_void = False
    
    if cost.remarks and cost.remarks.startswith(PROJECT_VOID_REMARK_PREFIX):
        cost.remarks = _restore_project_voided_remark(cost.remarks)
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
    return redirect(url_for('construction_admin.all_removed_costs'))
@construction_admin_bp.route('/edit-cost/<int:cost_id>', methods=['GET', 'POST'])
@login_required
@module_access_required('construction')
@write_access_required
def edit_cost(cost_id):
    entry = db.session.get(CostEntry, cost_id)
    if not entry:
        flash("Cost entry not found.", "danger")
        return redirect(url_for('costs.view_costs'))
 
    if request.method == 'POST':
 
        date_str    = request.form.get('date', '').strip()
        project_id_str = request.form.get('project_id', '').strip()
        cost_type   = request.form.get('cost_type', '').strip()
        qty_str     = request.form.get('quantity', '').strip()
        rate_str    = request.form.get('unit_rate', '').strip()
        remarks     = request.form.get('remarks', '').strip()
 
 
        if not date_str:
            flash("Date is required.", "danger")
            return _render_edit_cost(entry, form_data=request.form)
 
        try:
            parsed_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            flash("Invalid date format. Please use YYYY-MM-DD.", "danger")
            return _render_edit_cost(entry, form_data=request.form)
 
        try:
            parsed_project_id = int(project_id_str)
        except (ValueError, TypeError):
            flash("Invalid project selected.", "danger")
            return _render_edit_cost(entry, form_data=request.form)
 
        target_project = db.session.get(Project, parsed_project_id)
        if not target_project:
            flash("Selected project does not exist.", "danger")
            return _render_edit_cost(entry, form_data=request.form)

        if target_project.is_void:
            flash("Costs cannot be moved to a voided project. Restore the project first.", "danger")
            return _render_edit_cost(entry, form_data=request.form)
 
        # 2c. Cost type — required
        if not cost_type:
            flash("Cost type is required.", "danger")
            return _render_edit_cost(entry, form_data=request.form)

        if len(cost_type) > MAX_COST_TYPE_LEN:
            flash(f"Cost type must be {MAX_COST_TYPE_LEN} characters or fewer.", "danger")
            return _render_edit_cost(entry, form_data=request.form)

        if len(remarks) > MAX_COST_REMARKS_LEN:
            flash(f"Remarks must be {MAX_COST_REMARKS_LEN} characters or fewer.", "danger")
            return _render_edit_cost(entry, form_data=request.form)

        allowed_cost_types = get_dropdown_options(COST_TYPE)
        if cost_type not in allowed_cost_types and cost_type != entry.cost_type:
            flash("Please select a valid cost type from the managed dropdown list.", "danger")
            return _render_edit_cost(entry, form_data=request.form)
 
        try:
            parsed_qty = Decimal(qty_str) if qty_str else Decimal('0')
        except InvalidOperation:
            flash("Invalid quantity. Please enter a valid number.", "danger")
            return _render_edit_cost(entry, form_data=request.form)
 
        try:
            parsed_rate = Decimal(rate_str) if rate_str else Decimal('0')
        except InvalidOperation:
            flash("Invalid unit rate. Please enter a valid number.", "danger")
            return _render_edit_cost(entry, form_data=request.form)
 
        parsed_total = parsed_qty * parsed_rate

        if (
            entry.date == parsed_date
            and entry.project_id == parsed_project_id
            and entry.cost_type == cost_type
            and (entry.quantity or Decimal('0')) == parsed_qty
            and (entry.unit_rate or Decimal('0')) == parsed_rate
            and (entry.total_amount or Decimal('0')) == parsed_total
            and (entry.remarks or '') == remarks
        ):
            flash("No changes detected. Nothing was updated.", "info")
            return _render_edit_cost(entry, form_data=request.form)

        admin_password = request.form.get('admin_password', '')
        if not check_password_hash(current_user.password, admin_password):
            return _render_edit_cost(entry, auth_error=True, form_data=request.form)
 
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
            flash(friendly_database_error(e, "save your cost changes", COST_TEXT_LIMITS), "danger")
            return _render_edit_cost(entry, form_data=request.form)
 
        logging.info(
            f"ADMIN ACTION: '{current_user.username}' edited Cost ID {cost_id} "
            f"(Project: '{original_project_name}', Total: {parsed_total})"
        )
        flash("Changes saved and audit log updated.", "success")
        return redirect(url_for('costs.view_costs'))
 
    # ── GET ───────────────────────────────────────────────────────────────────
    return _render_edit_cost(entry)
 

@construction_admin_bp.route('/audit-log')
@login_required
@module_access_required('construction')
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
@construction_admin_bp.route('/all-removed-projects')
@login_required
@module_access_required('construction')
@admin_required
def all_removed_projects():
    page, per_page = get_pagination_args(request)
    pagination = (
        Project.query
        .filter_by(is_void=True)
        .order_by(Project.id.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )
    return render_template('all_removed_projects.html', projects=pagination.items, pagination=pagination)

@construction_admin_bp.route('/all-removed-costs')
@login_required
@module_access_required('construction')
@admin_required
def all_removed_costs():
    page, per_page = get_pagination_args(request)
    pagination = (
        CostEntry.query
        .filter_by(is_void=True)
        .order_by(CostEntry.date.desc(), CostEntry.id.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )
    return render_template('all_removed_costs.html', costs=pagination.items, pagination=pagination)

@construction_admin_bp.route('/all-edited-costs')
@login_required
@module_access_required('construction')
@admin_required
def all_edited_costs():
    # Fetch all logs, order by newest first
    page, per_page = get_pagination_args(request, DEFAULT_LOG_PER_PAGE)
    pagination = (
        EditLog.query
        .order_by(EditLog.changed_at.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )
    return render_template('all_edited_costs.html', edited_costs=pagination.items, pagination=pagination)

@construction_admin_bp.route('/all-edited-projects')
@login_required
@module_access_required('construction')
@admin_required
def all_edited_projects():
    # Fetch all logs, order by newest first
    page, per_page = get_pagination_args(request, DEFAULT_LOG_PER_PAGE)
    pagination = (
        ProjectEditLog.query
        .order_by(ProjectEditLog.changed_at.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )
    return render_template('all_edited_projects.html', edited_projects=pagination.items, pagination=pagination)


def _render_dropdown_options(form_data=None):
    sectors = DropdownOption.query.filter_by(option_type=PROJECT_SECTOR).order_by(DropdownOption.name.asc()).all()
    cost_types = DropdownOption.query.filter_by(option_type=COST_TYPE).order_by(DropdownOption.name.asc()).all()

    return render_template(
        'dropdown_options.html',
        sectors=sectors,
        cost_types=cost_types,
        form_data=form_data,
    )


@construction_admin_bp.route('/dropdown-options', methods=['GET', 'POST'])
@login_required
@module_access_required('construction')
@write_access_required
def dropdown_options():
    if request.method == 'POST':
        option_type = request.form.get('option_type', '').strip()
        name = request.form.get('name', '').strip()

        if option_type not in OPTION_TYPE_LABELS:
            flash("Invalid dropdown type selected.", "danger")
            return _render_dropdown_options(request.form)

        if not name:
            flash("Option name is required.", "danger")
            return _render_dropdown_options(request.form)

        if len(name) > 100:
            flash("Option name must be 100 characters or fewer.", "danger")
            return _render_dropdown_options(request.form)

        existing = DropdownOption.query.filter(
            DropdownOption.option_type == option_type,
            func.lower(DropdownOption.name) == name.lower()
        ).first()
        if existing:
            flash(f"{OPTION_TYPE_LABELS[option_type]} '{name}' already exists.", "warning")
            return _render_dropdown_options(request.form)

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
        return redirect(url_for('construction_admin.dropdown_options'))

    return _render_dropdown_options()


@construction_admin_bp.route('/dropdown-options/<int:option_id>/delete', methods=['POST'])
@login_required
@module_access_required('construction')
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
    return redirect(url_for('construction_admin.dropdown_options'))

