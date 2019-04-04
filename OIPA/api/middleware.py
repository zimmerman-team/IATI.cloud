from django.urls import resolve


# This middleware is used to give a name and an extension for
# files exported by using the renderers.py(currently only csv and xls)
# as the 'Content-Disposition' given in those renderers
# response is not applied(or maybe overriden by something else)
# we need to apply it here
class FileExportMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    @staticmethod
    def process_template_response(request, response):
        # So here we check if the view that we're dealing with
        # is actually an api view
        if request.resolver_match.app_name == 'api':
            if 'format' in request.GET:
                formatz = request.GET['format']

                if formatz in ['csv', 'xls', 'xml']:
                    current_url = resolve(request.path_info).url_name

                    if 'export_name' in request.GET:
                        file_name = request.GET['export_name']
                    else:
                        file_name = current_url \
                            if current_url is not None else 'export'

                    response['Content-Disposition'] = \
                        "attachment; filename={}.{}".format(file_name, formatz)

        return response
