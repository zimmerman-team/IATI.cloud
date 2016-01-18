
from rest_framework import pagination

class CustomPagination(pagination.PageNumberPagination):
    page_size = 10
    max_page_size = 2000
    page_size_query_param = 'page_size'


# TODO: pagination using Link header? see http://www.django-rest-framework.org/api-guide/pagination/#header-based-pagination - 2016-01-18
class IatiXMLPagination(pagination.PageNumberPagination):
    page_size = 10
    max_page_size = 100
    page_size_query_param = 'page_size'
