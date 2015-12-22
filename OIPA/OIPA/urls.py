from django.conf import settings
from django.conf.urls import include
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic.base import RedirectView
from django.views.generic import TemplateView

admin.autodiscover()

urlpatterns = [
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/queue/', include('django_rq.urls')),
    url(r'^admin/task_queue/', include('task_queue.urls')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include('api.urls')),
    url(r'^home$', TemplateView.as_view(template_name='home/home.html')),
    url(r'^about$', TemplateView.as_view(template_name='home/about.html')),
    url(r'', include('two_factor.urls', 'two_factor')),
    url(r'^$', RedirectView.as_view(url='/home', permanent=True))
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

