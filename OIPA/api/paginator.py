from tastypie.paginator import Paginator

class NoCountPaginator(Paginator):

    def get_next(self, limit, offset, count):
        count_param = self.request_data.get('count', None)
        if not count_param == 'false':
            return super(NoCountPaginator, self).get_next(limit, offset, count)
        else:
            count = 2 ** 64
            return super(NoCountPaginator, self).get_next(limit, offset, count)

    def get_count(self):
        count_param = self.request_data.get('count', None)
        if not count_param == 'false':
            return super(NoCountPaginator, self).get_count()
        else:
            return None