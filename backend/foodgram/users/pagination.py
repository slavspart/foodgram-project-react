from rest_framework.pagination import PageNumberPagination

class LimitPagination(PageNumberPagination):
    """Класс для пагинации"""
    page_size_query_param = 'limit' 