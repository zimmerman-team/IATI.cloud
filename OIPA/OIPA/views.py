# Imports
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import loader


##
# Handle 404 Errors
# @param request WSGIRequest list with all HTTP Request
def error404(request):

    # Generate Content for this view
    template = loader.get_template('404.html')

    context = {
        'referrer': request.META.get('HTTP_REFERER', '/'),
    }

    # 3. Return Template for this view + Data
    return HttpResponse(content=template.render(context),
                        content_type='text/html; charset=utf-8', status=404)


def error500(request):

    # Generate Content for this view
    template = loader.get_template('500.html')

    context = {
        'referrer': request.META.get('HTTP_REFERER', '/'),
    }

    # Return Template for this view + Data
    return HttpResponse(content=template.render(context),
                        content_type='text/html; charset=utf-8', status=500)


def home(request):
    return redirect('/api')
