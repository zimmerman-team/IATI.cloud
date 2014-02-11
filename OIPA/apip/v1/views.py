# Django specific
from django.http import HttpResponse


def documentation_view(request):
    return HttpResponse('Deprecated...')