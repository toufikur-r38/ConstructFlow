from decimal import InvalidOperation
from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED

from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from flask_login import login_required, current_user
from datetime import datetime, timezone, timedelta
import logging
from sqlalchemy.orm import joinedload
from app.utils.decorators import module_access_required, write_access_required
from app.extensions import db , limiter
from app.models import Project, CostEntry
from app.utils.db_errors import friendly_database_error
from app.utils.pagination import get_pagination_args
from app.modules.construction.utils.dashboard_cache import invalidate_dashboard_math
from app.modules.construction.utils.dropdown_options import COST_TYPE, get_dropdown_options
from app.modules.construction.utils.generate_costs_excel import generate_costs_excel
from app.modules.construction.utils.generate_costs_pdf import generate_costs_pdf
from app.modules.construction.utils.money import calculate_total, to_money
from app.modules.construction.utils.project_sorting import sort_projects_by_status_then_name



costs_bp = Blueprint('costs', __name__, template_folder='../templates')

DETAIL_PDF_ROW_THRESHOLD = 5000
ALL_PROJECTS_FILTER = '__all_projects__'
MAX_COST_TYPE_LEN = 50
MAX_REMARKS_LEN   = 500
BD_TZ = timezone(timedelta(hours=6))
COST_TEXT_LIMITS = (
    ("Cost type", MAX_COST_TYPE_LEN),
    ("Remarks", MAX_REMARKS_LEN),
)


def _today_bd():
    return datetime.now(BD_TZ).date()
 
 
def _running_project_choices():
    return (
        Project.query
        .filter(Project.is_void == False, Project.status == 'Running')
        .order_by(Project.project_name.asc())
        .all()
    )


def _cost_filter_project_choices():
    projects = (
        Project.query
        .filter(Project.is_void == False)
        .order_by(Project.project_name.asc())
        .all()
    )
    return sort_projects_by_status_then_name(projects)


def _project_filter_choices(selected_project=None):
    projects = _cost_filter_project_choices()
    if selected_project and all(project.id != selected_project.id for project in projects):
        projects.append(selected_project)
    return projects


def _selected_project_from_filter(project_id, allow_voided=False):
    try:
        parsed_project_id = int(project_id)
    except (TypeError, ValueError):
        raise ValueError("Invalid project filter selected.")

    project = db.session.get(Project, parsed_project_id)
    if not project or (project.is_void and not allow_voided):
        raise ValueError("Selected project does not exist or has been voided.")

    return project


def _project_scope_from_filter(project_filter, allow_voided=False):
    if project_filter == ALL_PROJECTS_FILTER:
        return None, True
    if project_filter:
        return _selected_project_from_filter(project_filter, allow_voided=allow_voided), False
    return None, False


def _has_export_filter(project_filter, cost_type, start_date, end_date):
    return bool(
        (project_filter and project_filter != ALL_PROJECTS_FILTER)
        or cost_type
        or start_date
        or end_date
    )


def _visible_cost_query(selected_project=None, include_all_projects=False, include_voided=False):
    query = (
        CostEntry.query
        .join(Project, CostEntry.project_id == Project.id)
    )
    if include_voided and selected_project:
        query = query.filter(CostEntry.project_id == selected_project.id)
        if selected_project.is_void:
            return query.filter(Project.id == selected_project.id)
        return query.filter(Project.is_void == False)

    query = query.filter(CostEntry.is_void == False, Project.is_void == False)
    if selected_project:
        return query.filter(CostEntry.project_id == selected_project.id)
    if include_all_projects:
        return query
    return query.filter(Project.status == 'Running')


def _summarize_cost_query(query, project=None):
    summary_rows = (
        query
        .with_entities(
            CostEntry.cost_type.label('cost_type'),
            db.func.count(CostEntry.id).label('records'),
            db.func.coalesce(db.func.sum(CostEntry.total_amount), 0).label('total'),
        )
        .group_by(CostEntry.cost_type)
        .order_by(CostEntry.cost_type.asc())
        .all()
    )
    summary = [
        {
            'cost_type': row.cost_type,
            'records': row.records,
            'total': row.total,
        }
        for row in summary_rows
    ]
    total_expenditure = sum((to_money(row.total) for row in summary_rows), to_money(0))
    projects_covered = 1 if project else (
        query
        .with_entities(db.func.count(db.distinct(CostEntry.project_id)))
        .scalar()
        or 0
    )
    return summary, total_expenditure, projects_covered


def _safe_report_name(value):
    return "".join(
        c if c.isalnum() or c in ('_', '-') else '_'
        for c in value
    )


def _render_add_cost(late_project=None, form_data=None):
    projects = [late_project] if late_project else _running_project_choices()
    recent_costs = (
        CostEntry.query
        .join(Project, CostEntry.project_id == Project.id)
        .filter(CostEntry.is_void == False, Project.is_void == False, Project.status == 'Running')
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
        late_project=late_project,
        form_data=form_data,
        form_action=(
            url_for('costs.add_late_cost', project_id=late_project.id)
            if late_project else url_for('costs.add_cost')
        ),
    )
 
 
@costs_bp.route('/add-cost', methods=['GET', 'POST'])
@login_required
@module_access_required('construction')
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
            return _render_add_cost(form_data=request.form)
 
        try:
            parsed_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            flash("Invalid date format. Please use YYYY-MM-DD.", "danger")
            return _render_add_cost(form_data=request.form)
 
        # must be a valid integer pointing to a real running project
        try:
            parsed_project_id = int(project_id_str)
        except (ValueError, TypeError):
            flash("Please select a valid project.", "danger")
            return _render_add_cost(form_data=request.form)
 
        target_project = db.session.get(Project, parsed_project_id)
        if not target_project or target_project.is_void:
            flash("Selected project does not exist or has been voided.", "danger")
            return _render_add_cost(form_data=request.form)
 
        if target_project.status != 'Running':
            flash("Costs can only be added to running projects.", "danger")
            return _render_add_cost(form_data=request.form)
 
        # Cost type — required, length cap
        if not cost_type:
            flash("Cost type is required.", "danger")
            return _render_add_cost(form_data=request.form)
 
        if len(cost_type) > MAX_COST_TYPE_LEN:
            flash(f"Cost type must be {MAX_COST_TYPE_LEN} characters or fewer.", "danger")
            return _render_add_cost(form_data=request.form)

        if cost_type not in get_dropdown_options(COST_TYPE):
            flash("Please select a valid cost type from the managed dropdown list.", "danger")
            return _render_add_cost(form_data=request.form)
 
        try:
            parsed_qty = to_money(qty_str)
        except InvalidOperation:
            flash("Invalid quantity. Please enter a valid number.", "danger")
            return _render_add_cost(form_data=request.form)
 
        try:
            parsed_rate = to_money(rate_str)
        except InvalidOperation:
            flash("Invalid unit rate. Please enter a valid number.", "danger")
            return _render_add_cost(form_data=request.form)
 
        #   Remarks length cap
        if len(remarks) > MAX_REMARKS_LEN:
            flash(f"Remarks must be {MAX_REMARKS_LEN} characters or fewer.", "danger")
            return _render_add_cost(form_data=request.form)
 
        # Total is always derived — never trusted from the form
        parsed_total = calculate_total(parsed_qty, parsed_rate)
 
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
            invalidate_dashboard_math()
        except Exception as e:
            db.session.rollback()
            logging.error(
                f"DB ERROR saving cost entry by '{current_user.username}': {e}"
            )
            flash(friendly_database_error(e, "save this cost entry", COST_TEXT_LIMITS), "danger")
            return _render_add_cost(form_data=request.form)
 
        logging.info(
            f"User '{current_user.username}' added cost entry — "
            f"Project: '{target_project.project_name}', "
            f"Type: {cost_type}, Total: {parsed_total}"
        )
        flash("Cost entry saved successfully!", "success")
        return redirect(url_for('costs.add_cost'))

    selected_project_id = request.args.get('project_id', '').strip()
    initial_form_data = {'project_id': selected_project_id} if selected_project_id else None
    return _render_add_cost(form_data=initial_form_data)


@costs_bp.route('/add-late-cost/<int:project_id>', methods=['GET', 'POST'])
@login_required
@module_access_required('construction')
@write_access_required
@limiter.limit("10 per minute")
def add_late_cost(project_id):
    project = db.session.get(Project, project_id)
    if not project or project.is_void:
        flash("Selected project does not exist or has been voided.", "danger")
        return redirect(url_for('costs.view_costs'))

    if project.status != 'Completed':
        flash("Late costs are only needed for completed projects.", "warning")
        return redirect(url_for('costs.view_costs', project_filter=project.id))

    if request.method == 'POST':
        date_str  = request.form.get('date', '').strip()
        cost_type = request.form.get('cost_type', '').strip()
        qty_str   = request.form.get('quantity', '').strip()
        rate_str  = request.form.get('unit_rate', '').strip()
        remarks   = request.form.get('remarks', '').strip()

        if not date_str:
            flash("Date is required.", "danger")
            return _render_add_cost(late_project=project, form_data=request.form)

        try:
            parsed_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            flash("Invalid date format. Please use YYYY-MM-DD.", "danger")
            return _render_add_cost(late_project=project, form_data=request.form)

        if not cost_type:
            flash("Cost type is required.", "danger")
            return _render_add_cost(late_project=project, form_data=request.form)

        if len(cost_type) > MAX_COST_TYPE_LEN:
            flash(f"Cost type must be {MAX_COST_TYPE_LEN} characters or fewer.", "danger")
            return _render_add_cost(late_project=project, form_data=request.form)

        if cost_type not in get_dropdown_options(COST_TYPE):
            flash("Please select a valid cost type from the managed dropdown list.", "danger")
            return _render_add_cost(late_project=project, form_data=request.form)

        try:
            parsed_qty = to_money(qty_str)
        except InvalidOperation:
            flash("Invalid quantity. Please enter a valid number.", "danger")
            return _render_add_cost(late_project=project, form_data=request.form)

        try:
            parsed_rate = to_money(rate_str)
        except InvalidOperation:
            flash("Invalid unit rate. Please enter a valid number.", "danger")
            return _render_add_cost(late_project=project, form_data=request.form)

        if len(remarks) > MAX_REMARKS_LEN:
            flash(f"Remarks must be {MAX_REMARKS_LEN} characters or fewer.", "danger")
            return _render_add_cost(late_project=project, form_data=request.form)

        if not remarks:
            flash("A clear remark is required for late costs on completed projects.", "danger")
            return _render_add_cost(late_project=project, form_data=request.form)

        parsed_total = calculate_total(parsed_qty, parsed_rate)

        new_entry = CostEntry(
            project_id=project.id,
            date=parsed_date,
            cost_type=cost_type,
            quantity=parsed_qty,
            unit_rate=parsed_rate,
            total_amount=parsed_total,
            remarks=remarks,
            user_id=current_user.id,
        )
        db.session.add(new_entry)

        try:
            db.session.commit()
            invalidate_dashboard_math()
        except Exception as e:
            db.session.rollback()
            logging.error(
                f"DB ERROR saving late cost entry by '{current_user.username}': {e}"
            )
            flash(friendly_database_error(e, "save this late cost entry", COST_TEXT_LIMITS), "danger")
            return _render_add_cost(late_project=project, form_data=request.form)

        logging.info(
            f"User '{current_user.username}' added late cost entry - "
            f"Project: '{project.project_name}', Type: {cost_type}, Total: {parsed_total}"
        )
        flash("Late cost entry saved successfully!", "success")
        return redirect(url_for('costs.view_costs', project_filter=project.id))

    return _render_add_cost(late_project=project)

@costs_bp.route('/view-costs')
@login_required
@module_access_required('construction')
def view_costs():
    project_id     = request.args.get('project_filter', '').strip()
    cost_type      = request.args.get('type_filter', '').strip()
    start_date_str = request.args.get('start_date', '').strip()
    end_date_str   = request.args.get('end_date', '').strip()
    include_voided = request.args.get('include_voided') == '1' and bool(project_id)
    effective_end_date = end_date_str
    page, per_page = get_pagination_args(request)

    selected_project = None
    include_all_projects = False

    # Project filter — only apply if a real value was selected
    if project_id:
        try:
            selected_project, include_all_projects = _project_scope_from_filter(
                project_id,
                allow_voided=include_voided,
            )
            include_voided = bool(include_voided and selected_project)
        except ValueError as exc:
            include_voided = False
            flash(str(exc), "danger")

    query = _visible_cost_query(
        selected_project,
        include_all_projects=include_all_projects,
        include_voided=include_voided,
    )

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

    pagination = query.order_by(CostEntry.date.asc(), CostEntry.id.asc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    costs = pagination.items
    project_choices = _project_filter_choices(selected_project)

    category_query = _visible_cost_query(
        selected_project,
        include_all_projects=include_all_projects,
        include_voided=include_voided,
    )
    available_categories = [row[0] for row in
        category_query.with_entities(CostEntry.cost_type)
        .distinct()
        .order_by(CostEntry.cost_type.asc())
        .all()
    ]

    return render_template('view_costs.html',
                           costs=costs,
                           projects=project_choices,
                           selected_project=selected_project,
                           categories=available_categories,
                           effective_end_date=effective_end_date,
                           detail_pdf_row_threshold=DETAIL_PDF_ROW_THRESHOLD,
                           all_projects_filter=ALL_PROJECTS_FILTER,
                           include_voided=include_voided,
                           pagination=pagination)



@costs_bp.route('/view-costs/pdf')
@login_required
@module_access_required('construction')
def download_pdf():
    project_id     = request.args.get('project_filter', '').strip()
    cost_type      = request.args.get('type_filter', '').strip()
    start_date_str = request.args.get('start_date', '').strip()
    end_date_str   = request.args.get('end_date', '').strip()
    effective_end_date = end_date_str
    project = None
    include_all_projects = False

    if not _has_export_filter(project_id, cost_type, start_date_str, end_date_str):
        flash("Please select at least one filter before generating a PDF report.", "warning")
        return redirect(url_for('costs.view_costs'))

    if project_id:
        try:
            project, include_all_projects = _project_scope_from_filter(project_id)
        except ValueError as exc:
            flash(str(exc), "danger")
            return redirect(url_for('costs.view_costs'))

    query = _visible_cost_query(project, include_all_projects=include_all_projects)

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

    matching_count = query.order_by(None).count()
    cost_type_summary, total_expenditure, projects_covered = _summarize_cost_query(query, project)

    generated_at = datetime.now(BD_TZ)
    timestamp = generated_at.strftime('%Y%m%d_%H%M')
    if matching_count > DETAIL_PDF_ROW_THRESHOLD:
        cover_pdf = generate_costs_pdf(
            costs=[],
            project=project,
            cost_type_filter=cost_type,
            start_date=start_date_str,
            end_date=effective_end_date,
            include_ledger=False,
            total_records=matching_count,
            total_expenditure=total_expenditure,
            projects_covered=projects_covered,
            cost_type_summary=cost_type_summary,
            generated_at=generated_at,
        )
        excel_rows = (
            query
            .with_entities(
                CostEntry.date.label('date'),
                Project.project_name.label('project_name'),
                CostEntry.cost_type.label('cost_type'),
                CostEntry.quantity.label('quantity'),
                CostEntry.unit_rate.label('unit_rate'),
                CostEntry.total_amount.label('total_amount'),
                CostEntry.remarks.label('remarks'),
            )
            .order_by(CostEntry.date.asc(), CostEntry.id.asc())
            .yield_per(1000)
        )
        ledger_excel = generate_costs_excel(
            rows=excel_rows,
            project=project,
            cost_type_filter=cost_type,
            start_date=start_date_str,
            end_date=effective_end_date,
            generated_at=generated_at,
        )
        zip_buffer = BytesIO()
        with ZipFile(zip_buffer, 'w', ZIP_DEFLATED) as bundle:
            bundle.writestr('Report_Cover.pdf', cover_pdf)
            bundle.writestr('Cost_Ledger.xlsx', ledger_excel)
        zip_buffer.seek(0)
        return Response(
            zip_buffer.getvalue(),
            mimetype='application/zip',
            headers={
                'Content-Disposition': f'attachment; filename="SR_Enterprise_Report_{timestamp}.zip"'
            }
        )

    costs = (
        query
        .options(joinedload(CostEntry.project))
        .order_by(CostEntry.date.asc(), CostEntry.id.asc())
        .all()
    )
    pdf_bytes = generate_costs_pdf(
        costs=costs,
        project=project,
        cost_type_filter=cost_type,
        start_date=start_date_str,
        end_date=effective_end_date,
        total_records=matching_count,
        total_expenditure=total_expenditure,
        projects_covered=projects_covered,
        cost_type_summary=cost_type_summary,
        generated_at=generated_at,
    )
    if project:
        safe_name = _safe_report_name(project.project_name)
        filename = f"{safe_name}_Expenditure_Report.pdf"
    else:
        filename = f"SR_Expenditure_Report_{timestamp}.pdf"
    return Response(
        pdf_bytes,
        mimetype='application/pdf',
        headers={
            'Content-Disposition': f'attachment; filename="{filename}"'
        }
    )
