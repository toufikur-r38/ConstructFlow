DEFAULT_PER_PAGE = 25
DEFAULT_LOG_PER_PAGE = 50
MIN_PER_PAGE = 10
MAX_PER_PAGE = 100
PER_PAGE_CHOICES = (10, 25, 50, 100)


def get_pagination_args(request, default_per_page=DEFAULT_PER_PAGE):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', default_per_page, type=int)

    if page < 1:
        page = 1

    if per_page is None:
        per_page = default_per_page

    if per_page > MAX_PER_PAGE:
        per_page = MAX_PER_PAGE
    elif per_page < MIN_PER_PAGE:
        per_page = MIN_PER_PAGE
    elif per_page not in PER_PAGE_CHOICES:
        per_page = default_per_page

    return page, per_page
