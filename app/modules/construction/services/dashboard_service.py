from datetime import date
from sqlalchemy import func
from app.extensions import db, cache
from app.models import Project, CostEntry
from app.modules.construction.utils.dashboard_cache import DASHBOARD_CACHE_KEY
from app.modules.construction.utils.money import percent_used, to_money, ZERO


# Calculates the math for the dashboards features
@cache.cached(timeout=60, key_prefix=DASHBOARD_CACHE_KEY)
def get_dashboard_math():
    today = date.today()
    first_day_of_month = today.replace(day=1)

    running_projects = Project.query.filter_by(status='Running', is_void=False).all()

    cost_sums = (
        db.session.query(
            CostEntry.project_id,
            func.sum(CostEntry.total_amount)
        )
        .join(Project, CostEntry.project_id == Project.id)
        .filter(CostEntry.is_void == False, Project.is_void == False)
        .group_by(CostEntry.project_id)
        .all()
    )
    
    cost_dict = {pid: to_money(total) for pid, total in cost_sums}

    spent_today = (
        db.session.query(func.sum(CostEntry.total_amount))
        .join(Project, CostEntry.project_id == Project.id)
        .filter(
            CostEntry.is_void == False,
            Project.is_void == False,
            CostEntry.date == today
        )
        .scalar()
    )
    spent_today = to_money(spent_today)

    spent_this_month = (
        db.session.query(func.sum(CostEntry.total_amount))
        .join(Project, CostEntry.project_id == Project.id)
        .filter(
            CostEntry.is_void == False,
            Project.is_void == False,
            CostEntry.date >= first_day_of_month
        )
        .scalar()
    )
    spent_this_month = to_money(spent_this_month)

    project_stats = []
    projects_in_danger = 0
    total_budget = ZERO
    total_spent = ZERO

    for p in running_projects:
        spent = cost_dict.get(p.id, ZERO)
        budget = to_money(p.contract_price)
        left = budget - spent
        percent = percent_used(spent, budget)
        total_budget += budget
        total_spent += spent

        if percent >= 80:
            projects_in_danger += 1

        project_stats.append({
            'id': p.id,
            'name': p.project_name,
            'budget': budget,
            'spent': spent,
            'left': left,
            'percent': percent,
        })

    budget_left = total_budget - total_spent
    utilization = percent_used(total_spent, total_budget)
    project_stats = sorted(
        project_stats,
        key=lambda item: (-item['percent'], item['name'].casefold())
    )
    top_projects = project_stats[:5]

    return {
        'running_count': len(running_projects),
        'spent_today': spent_today,
        'spent_this_month': spent_this_month,
        'projects_in_danger': projects_in_danger,
        'project_stats': project_stats,
        'total_budget': total_budget,
        'total_spent': total_spent,
        'budget_left': budget_left,
        'utilization': utilization,
        'top_projects': top_projects,
    }
