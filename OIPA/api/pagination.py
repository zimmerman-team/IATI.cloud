
from rest_framework import pagination
from rest_framework.response import Response

# TODO: Include 'last' link, see
# https://developer.github.com/guides/traversing-with-pagination/ -
# 2016-01-20


class CustomPagination(pagination.PageNumberPagination):
    page_size = 10  # default
    max_page_size = 2000
    page_size_query_param = 'page_size'


class CustomTransactionPagination(CustomPagination):
    max_page_size = 2000


class IatiXMLPagination(pagination.PageNumberPagination):
    page_size = 10  # default
    max_page_size = 2000
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        next_url = self.get_next_link()
        previous_url = self.get_previous_link()

        if next_url is not None and previous_url is not None:
            link = '<{next_url}>; rel="next", <{previous_url}>; rel="prev"'
        elif next_url is not None:
            link = '<{next_url}>; rel="next"'
        elif previous_url is not None:
            link = '<{previous_url}>; rel="prev"'
        else:
            link = ''

        link = link.format(next_url=next_url, previous_url=previous_url)
        headers = {'Link': link} if link else {}

        return Response(data, headers=headers)


class IatiXMLUnlimitedPagination(IatiXMLPagination):
    page_size = 0
    max_page_size = 0
