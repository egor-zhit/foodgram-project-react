from rest_framework.pagination import PageNumberPagination


class LimitPagination(PageNumberPagination):
    """Лимит обьектов на странице."""
    page_size = 6
    page_size_query_param = 'limit'
