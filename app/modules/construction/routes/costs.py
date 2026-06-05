from decimal import Decimal, InvalidOperation

from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from flask_login import login_required, current_user
from datetime import datetime, timezone, timedelta
import logging
from app.extensions import cache
from app.utils.decorators import write_access_required
from app.extensions import db , limiter
from app.models import Project, CostEntry
from app.utils.pagination import get_pagination_args
from app.modules.construction.utils.dropdown_options import COST_TYPE, get_dropdown_options
from app.modules.construction.utils.generate_costs_pdf import generate_costs_pdf



costs_bp = Blueprint('costs', __name__, template_folder='../templates')

MAX_COST_TYPE_LEN = 50
MAX_REMARKS_LEN   = 500
BD_TZ = timezone(timedelta(hours=6))


def _today_bd():
    return datetime.now(BD_TZ).date()
 
 
def _render_add_cost():
    projects = (
        Project.query
        .filter(Project.is_void == False, Project.status.in_(['Running', 'Completed']))
        .order_by(Project.project_name.asc())
        .all()
    )
    recent_costs = (
        CostEntry.query
        .filter_by(is_void=False)
        .order_by(CostEntry.logged_at.desc())
        .limit(15)
        .all()
    )
    return render_template(
        'add_cost.html',
        projects=projects,
        recent_costs=recent_costs,
        cost_types=get_dropdown_options(COST_TYPE),
        current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    )
 
 
@costs_bp.route('/add-cost', methods=['GET', 'POST'])
@login_required                   
@write_access_required            
@limiter.limit("30 per minute")   
def add_cost():
 
    if request.method == 'POST':
 
        project_id_str = request.form.get('project_id', '').strip()
        date_str       = request.form.get('date', '').strip()
        cost_type      = request.form.get('cost_type', '').strip()
        qty_str        = request.form.get('quantity', '').strip()
        rate_str       = request.form.get('unit_rate', '').strip()
        remarks        = request.form.get('remarks', '').strip()
 
 
        #  Date — required, must be valid
        if not date_str:
            flash("Date is required.", "danger")
            return _render_add_cost()
 
        try:
            parsed_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            flash("Invalid date format. Please use YYYY-MM-DD.", "danger")
            return _render_add_cost()
 
        # must be a valid integer pointing to a real running project
        try:
            parsed_project_id = int(project_id_str)
        except (ValueError, TypeError):
            flash("Please select a valid project.", "danger")
            return _render_add_cost()
 
        target_project = db.session.get(Project, parsed_project_id)
        if not target_project or target_project.is_void:
            flash("Selected project does not exist or has been voided.", "danger")
            return _render_add_cost()
 
        if target_project.status not in ['Running', 'Completed']:
            flash("Costs can only be added to running or completed projects.", "danger")
            return _render_add_cost()
 
        # Cost type — required, length cap
        if not cost_type:
            flash("Cost type is required.", "danger")
            return _render_add_cost()
 
        if len(cost_type) > MAX_COST_TYPE_LEN:
            flash(f"Cost type must be {MAX_COST_TYPE_LEN} characters or fewer.", "danger")
            return _render_add_cost()

        if cost_type not in get_dropdown_options(COST_TYPE):
            flash("Please select a valid cost type from the managed dropdown list.", "danger")
            return _render_add_cost()
 
        try:
            parsed_qty = Decimal(qty_str) if qty_str else Decimal('0')
            if parsed_qty < 0:
                raise ValueError("Quantity cannot be negative.")
        except (InvalidOperation, ValueError):
            flash("Invalid quantity. Please enter a positive number.", "danger")
            return _render_add_cost()
 
        try:
            parsed_rate = Decimal(rate_str) if rate_str else Decimal('0')
        except InvalidOperation:
            flash("Invalid unit rate. Please enter a valid number.", "danger")
            return _render_add_cost()
 
        #   Remarks length cap
        if len(remarks) > MAX_REMARKS_LEN:
            flash(f"Remarks must be {MAX_REMARKS_LEN} characters or fewer.", "danger")
            return _render_add_cost()
 
        # Total is always derived — never trusted from the form
        parsed_total = parsed_qty * parsed_rate
 
        new_entry = CostEntry(
            project_id=parsed_project_id,
            date=parsed_date,
            cost_type=cost_type,
            quantity=parsed_qty,
            unit_rate=parsed_rate,
            total_amount=parsed_total,
            remarks=remarks or None,   
            user_id=current_user.id,
        )
        db.session.add(new_entry)
 
        try:
            db.session.commit()
            cache.delete('dashboard_math_data')
        except Exception as e:
            db.session.rollback()
            logging.error(
                f"DB ERROR saving cost entry by '{current_user.username}': {e}"
            )
            flash("A database error occurred. The entry was not saved.", "danger")
            return _render_add_cost()
 
        logging.info(
            f"User '{current_user.username}' added cost entry — "
            f"Project: '{target_project.project_name}', "
            f"Type: {cost_type}, Total: {parsed_total}"
        )
        flash("Cost entry saved successfully!", "success")
        return redirect(url_for('costs.add_cost'))
 
    return _render_add_cost()

@costs_bp.route('/view-costs')
@login_required
def view_costs():
    project_id     = request.args.get('project_filter', '').strip()
    cost_type      = request.args.get('type_filter', '').strip()
    start_date_str = request.args.get('start_date', '').strip()
    end_date_str   = request.args.get('end_date', '').strip()
    effective_end_date = end_date_str
    page, per_page = get_pagination_args(request)

    query = CostEntry.query

    # Project filter — only apply if a real value was selected
    if project_id:
        try:
            parsed_project_id = int(project_id)
        except (TypeError, ValueError):
            flash("Invalid project filter selected.", "danger")
            parsed_project_id = None

        if parsed_project_id is not None:
            query = query.filter(CostEntry.project_id == parsed_project_id)

    # Category filter — only apply if not empty
    if cost_type:
        query = query.filter(CostEntry.cost_type == cost_type)

    # Date filters — protected with try/except
    if start_date_str:
        try:
            start_dt = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            query = query.filter(CostEntry.date >= start_dt)
        except ValueError:
            flash("Invalid start date format.", "danger")

    if end_date_str:
        try:
            end_dt = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            query = query.filter(CostEntry.date <= end_dt)
        except ValueError:
            flash("Invalid end date format.", "danger")

    pagination = query.filter_by(is_void=False).order_by(CostEntry.date.asc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    costs = pagination.items
    all_projects = Project.query.filter_by(is_void=False).all()

    available_categories = [row[0] for row in
        db.session.query(CostEntry.cost_type)
        .filter(CostEntry.is_void == False)
        .distinct()
        .order_by(CostEntry.cost_type.asc())
        .all()
    ]

    return render_template('view_costs.html',
                           costs=costs,
                           projects=all_projects,
                           categories=available_categories,
                           effective_end_date=effective_end_date,
                           pagination=pagination)



@costs_bp.route('/view-costs/pdf')
@login_required
def download_pdf():
    project_id     = request.args.get('project_filter', '').strip()
    cost_type      = request.args.get('type_filter', '').strip()
    start_date_str = request.args.get('start_date', '').strip()
    end_date_str   = request.args.get('end_date', '').strip()
    effective_end_date = end_date_str
    query = CostEntry.query
    project = None

    if not any([project_id, cost_type, start_date_str, end_date_str]):
        flash("Please select at least one filter before generating a PDF report.", "warning")
        return redirect(url_for('costs.view_costs'))

    if project_id:
        try:
            parsed_project_id = int(project_id)
        except (TypeError, ValueError):
            flash("Invalid project selected for PDF export.", "danger")
            return redirect(url_for('costs.view_costs'))

        project = db.session.get(Project, parsed_project_id)
        if not project or project.is_void:
            flash("Selected project does not exist or has been voided.", "danger")
            return redirect(url_for('costs.view_costs'))

        query = query.filter(CostEntry.project_id == parsed_project_id)

    if cost_type:
        query = query.filter(CostEntry.cost_type == cost_type)
    parsed_start = None
    parsed_end = None

    if start_date_str:
        try:
            parsed_start = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            query = query.filter(CostEntry.date >= parsed_start)
        except ValueError:
            flash("Invalid start date selected for PDF export.", "danger")
            return redirect(url_for('costs.view_costs'))
    if end_date_str:
        try:
            parsed_end = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            query = query.filter(CostEntry.date <= parsed_end)
        except ValueError:
            flash("Invalid end date selected for PDF export.", "danger")
            return redirect(url_for('costs.view_costs'))

    if parsed_start and parsed_end and parsed_end < parsed_start:
        flash("PDF export end date cannot be before start date.", "danger")
        return redirect(url_for('costs.view_costs'))

    costs = query.filter_by(is_void=False).order_by(CostEntry.date.asc()).all()
    pdf_bytes = generate_costs_pdf(
        costs=costs,
        project=project,
        cost_type_filter=cost_type,
        start_date=start_date_str,
        end_date=effective_end_date,
    )
    if project:
        safe_name = "".join(
            c if c.isalnum() or c in ('_', '-') else '_'
            for c in project.project_name
        )
        filename = f"{safe_name}_Expenditure_Report.pdf"
    else:
        filename = f"ConstructFlow_Expenditure_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    return Response(
        pdf_bytes,
        mimetype='application/pdf',
        headers={
            'Content-Disposition': f'attachment; filename="{filename}"'
        }
    )
