from app.extensions import cache


DASHBOARD_CACHE_KEY = 'dashboard_math_data'


def invalidate_dashboard_math():
    cache.delete(DASHBOARD_CACHE_KEY)
