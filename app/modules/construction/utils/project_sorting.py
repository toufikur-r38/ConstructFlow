PROJECT_STATUS_RANK = {
    'Running': 0,
    'Completed': 1,
    'On Hold': 2,
}


def project_status_sort_key(project):
    return (
        PROJECT_STATUS_RANK.get(getattr(project, 'status', None), 99),
        (getattr(project, 'project_name', '') or '').casefold(),
    )


def sort_projects_by_status_then_name(projects):
    return sorted(projects, key=project_status_sort_key)
