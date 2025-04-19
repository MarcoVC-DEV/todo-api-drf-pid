from rest_framework.pagination import LimitOffsetPagination



class DefaultPaginationLOS(LimitOffsetPagination):
    default_limit = 10