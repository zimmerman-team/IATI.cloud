from django.urls import resolve
from django.utils.datastructures import MultiValueDictKeyError


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
            try:
                formatz = request.GET['format']

                if formatz == 'csv' or formatz == 'xls':
                    current_url = resolve(request.path_info).url_name

                    try:
                        file_name = request.GET['export_name']
                    except MultiValueDictKeyError:
                        file_name = current_url \
                            if current_url is not None else 'export'

                    response['Content-Disposition'] = \
                        "attachment; filename={}.{}".format(file_name, formatz)

            except MultiValueDictKeyError:
                pass

        return response
