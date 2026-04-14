from datetime import date


def get_season(d: date) -> str:
    month = d.month
    if month in (12, 1, 2):
        return "summer"
    if month in (3, 4, 5):
        return "autumn"
    if month in (6, 7, 8):
        return "winter"
    return "spring"


def paginate_query(query, page: int, per_page: int):
    """Apply pagination to a SQLAlchemy query. Returns (items, total, pages)."""
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return pagination.items, pagination.total, pagination.pages
