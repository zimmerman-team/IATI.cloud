
class PassContextMixin(object):
    """
    Pass request and params object to the serializer for sub-filtering
    """
    def get_serializer_context(self):
        return {
            'request': self.request
        }
