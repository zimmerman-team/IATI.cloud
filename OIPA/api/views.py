from django.http import *
from django.core.urlresolvers import resolve

def html_decorator(func):
    def _decorated(*args, **kwargs):
	response = HttpResponse()
	response = func(*args, **kwargs)
 
        wrapped = ("<html><body>",response.content,"</body></html>")
 
	return HttpResponse(wrapped)
 
    return _decorated
 
 
@html_decorator
def debug(request):
    path = request.META.get("PATH_INFO")
    api_url = path.replace("debug/", "")
  
    view = resolve(api_url)
 
    accept = request.META.get("HTTP_ACCEPT")
    accept += ",application/json"
    request.META["HTTP_ACCEPT"] = accept
 
    res = view.func(request, **view.kwargs)
    return HttpResponse(res._container)
