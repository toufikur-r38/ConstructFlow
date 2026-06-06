import re
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from decimal import Decimal, InvalidOperation
import logging
from sqlalchemy import func
from app.extensions import db, limiter
from app.models import CostEntry, Project
from app.extensions import cache
from app.utils.decorators import  write_access_required
from app.utils.pagination import get_pagination_args
from app.modules.construction.utils.dropdown_options import PROJECT_SECTOR, get_dropdown_options
projects_bp = Blueprint('projects', __name__, template_folder='../templates')


MAX_NAME_LEN   = 200
MAX_SECTOR_LEN = 100
MAX_FIRM_LEN   = 200
MAX_TENDER_LEN = 100
MAX_ADDR_LEN   = 500
YEAR_PATTERN   = re.compile(r'^\d{4}(?:-\d{4})?$')   # e.g. "2024" or "2023-2024"
VALID_PROJECT_STATUSES = ('Running', 'Completed', 'On Hold')

def _render_add_project(all_projects):
    return render_template(
        'add_project.html',
        projects=all_projects,
        sectors=get_dropdown_options(PROJECT_SECTOR),
    )
 
 
@projects_bp.route('/add-project', methods=['GET', 'POST'])
@login_required
@write_access_required
@limiter.limit("20 per minute")
def add_project():
    all_projects = Project.query.filter_by(is_void=False).all()
 
    if request.method == 'POST':
 
        project_name       = request.form.get('project_name', '').strip()
        sector             = request.form.get('sector', '').strip()
        firm_name          = request.form.get('firm_name', '').strip()
        tender_id          = request.form.get('tender_id', '').strip()
        noa_str            = request.form.get('noa_date', '').strip()
        work_order_year    = request.form.get('work_order_year', '').strip()
        price_str          = request.form.get('contract_price', '').strip()
        address            = request.form.get('address', '').strip()
        additional_details = request.form.get('additional_details', '').strip()
 
      
        if not project_name:
            flash("Project name is required.", "danger")
            return _render_add_project(all_projects)
 
        if len(project_name) > MAX_NAME_LEN:
            flash(f"Project name must be {MAX_NAME_LEN} characters or fewer.", "danger")
            return _render_add_project(all_projects)
 
        # 2b. Optional text field length caps
        if len(sector) > MAX_SECTOR_LEN:
            flash(f"Sector must be {MAX_SECTOR_LEN} characters or fewer.", "danger")
            return _render_add_project(all_projects)

        if sector not in get_dropdown_options(PROJECT_SECTOR):
            flash("Please select a valid project sector from the managed dropdown list.", "danger")
            return _render_add_project(all_projects)
 
        if len(firm_name) > MAX_FIRM_LEN:
            flash(f"Firm name must be {MAX_FIRM_LEN} characters or fewer.", "danger")
            return _render_add_project(all_projects)
 
        if len(tender_id) > MAX_TENDER_LEN:
            flash(f"Tender ID must be {MAX_TENDER_LEN} characters or fewer.", "danger")
            return _render_add_project(all_projects)
 
        if len(address) > MAX_ADDR_LEN:
            flash(f"Address must be {MAX_ADDR_LEN} characters or fewer.", "danger")
            return _render_add_project(all_projects)
 
        parsed_noa = None
        if noa_str:
            try:
                parsed_noa = datetime.strptime(noa_str, '%Y-%m-%d').date()
            except ValueError:
                flash("Invalid NOA date. Please use YYYY-MM-DD format.", "danger")
                return _render_add_project(all_projects)
 
        if work_order_year and not YEAR_PATTERN.match(work_order_year):
            flash("Work order year must be a 4-digit year (e.g. 2024) or range (e.g. 2023-2024).", "danger")
            return _render_add_project(all_projects)
 
        parsed_price = Decimal('0')
        if price_str:
            try:
                parsed_price = Decimal(price_str)
                if parsed_price < 0:
                    raise ValueError("Price cannot be negative.")
            except (InvalidOperation, ValueError):
                flash("Invalid contract price. Please enter a positive number.", "danger")
                return _render_add_project(all_projects)
 
        normalized_tender_id = tender_id or None
        duplicate = Project.query.filter(
            Project.project_name == project_name,
            Project.tender_id.is_(None) if normalized_tender_id is None else Project.tender_id == normalized_tender_id,
            Project.is_void == False
        ).first()
        if duplicate:
            flash(
                f"A project named '{project_name}' with Tender ID '{tender_id}' already exists.",
                "warning"
            )
            return _render_add_project(all_projects)
 
        new_project = Project(
            project_name=project_name,
            sector=sector or None,
            firm_name=firm_name or None,
            tender_id=normalized_tender_id,
            noa_date=parsed_noa,
            work_order_year=work_order_year or None,
            contract_price=parsed_price,
            address=address or None,
            additional_details=additional_details or None,
            user_id=current_user.id,
        )
        db.session.add(new_project)
 
        try:
            db.session.commit()
            cache.delete('dashboard_math_data')
        except Exception as e:
            db.session.rollback()
            logging.error(
                f"DB ERROR saving project by '{current_user.username}': {e}"
            )
            flash("A database error occurred. The project was not saved.", "danger")
            return _render_add_project(all_projects)
 
        logging.info(
            f"User '{current_user.username}' created project "
            f"'{project_name}' (Tender: {tender_id or 'N/A'})"
        )
        flash("New project saved successfully!", "success")
        return redirect(url_for('projects.add_project'))
 
    return _render_add_project(all_projects)
@projects_bp.route('/view-projects')
@login_required
def view_projects():
    sector_filter = request.args.get('sector_filter')
    search_query = request.args.get('search', '').strip()
    status_filter = request.args.get('status_filter', 'all').strip()
    page, per_page = get_pagination_args(request)
    
    query = Project.query.filter_by(is_void=False)

    if sector_filter and sector_filter != 'all':
        query = query.filter(Project.sector == sector_filter)

    if status_filter in VALID_PROJECT_STATUSES:
        query = query.filter(Project.status == status_filter)
    
    if search_query:
        query = query.filter(
            (Project.project_name.ilike(f'%{search_query}%')) | 
            (Project.firm_name.ilike(f'%{search_query}%')) |
            (Project.tender_id.ilike(f'%{search_query}%'))
        )

    pagination = query.order_by(Project.logged_at.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    all_projects = pagination.items

    project_ids = [project.id for project in all_projects]
    spent_by_project = {}
    if project_ids:
        spent_rows = (
            db.session.query(
                CostEntry.project_id,
                func.coalesce(func.sum(CostEntry.total_amount), 0).label('spent')
            )
            .filter(
                CostEntry.is_void == False,
                CostEntry.project_id.in_(project_ids)
            )
            .group_by(CostEntry.project_id)
            .all()
        )
        spent_by_project = {project_id: spent or Decimal('0') for project_id, spent in spent_rows}

    project_financials = {}
    for project in all_projects:
        budget = project.contract_price or Decimal('0')
        spent = spent_by_project.get(project.id, Decimal('0'))
        left = budget - spent
        percent = round((spent / budget * 100), 1) if budget > 0 else 0
        project_financials[project.id] = {
            'spent': spent,
            'left': left,
            'percent': percent,
        }
    
    available_sectors = db.session.query(Project.sector)\
        .filter(Project.is_void == False)\
        .distinct()\
        .order_by(Project.sector.asc())\
        .all()
    
    sectors_list = [s[0] for s in available_sectors if s[0]]
    
    return render_template('view_projects.html', 
                           projects=all_projects, 
                           sectors=sectors_list,
                           statuses=VALID_PROJECT_STATUSES,
                           project_financials=project_financials,
                           pagination=pagination)
