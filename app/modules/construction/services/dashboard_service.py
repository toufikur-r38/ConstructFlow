from datetime import date
from sqlalchemy import func
from app.extensions import db, cache
from app.models import Project, CostEntry


# Calculates the math for the dashboards features
@cache.cached(timeout=60, key_prefix='dashboard_math_data')
def get_dashboard_math():
    today = date.today()
    first_day_of_month = today.replace(day=1)

    running_projects = Project.query.filter_by(status='Running', is_void=False).all()

    cost_sums = db.session.query(
        CostEntry.project_id,
        func.sum(CostEntry.total_amount)
    ).filter(CostEntry.is_void == False).group_by(CostEntry.project_id).all()
    
    cost_dict = {pid: (total or 0) for pid, total in cost_sums}

    spent_today = db.session.query(func.sum(CostEntry.total_amount)).filter(
        CostEntry.is_void == False,
        CostEntry.date == today
    ).scalar() or 0

    spent_this_month = db.session.query(func.sum(CostEntry.total_amount)).filter(
        CostEntry.is_void == False,
        CostEntry.date >= first_day_of_month
    ).scalar() or 0

    project_stats = []
    projects_in_danger = 0
    total_budget = 0
    total_spent = 0

    for p in running_projects:
        spent = cost_dict.get(p.id, 0)
        budget = p.contract_price or 0
        left = budget - spent
        percent = round((spent / budget * 100), 1) if budget > 0 else 0
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
    utilization = round((total_spent / total_budget * 100), 1) if total_budget > 0 else 0
    top_projects = sorted(project_stats, key=lambda item: item['percent'], reverse=True)[:3]

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
