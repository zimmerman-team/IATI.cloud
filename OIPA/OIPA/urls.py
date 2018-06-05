from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
from two_factor.urls import urlpatterns as tf_urls

from OIPA import views

admin.autodiscover()

urlpatterns = [
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/queue/', include('django_rq.urls')),
    url(r'^admin/task_queue/', include('task_queue.urls')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include('api.urls')),
    url(r'^home$', TemplateView.as_view(template_name='home/home.html')),
    url(r'^404$', views.error404),
    url(r'^500$', views.error500),
    url(r'^about$', TemplateView.as_view(template_name='home/about.html')),
    url(r'', include(tf_urls, 'two_factor')),
    url(r'^accounts/profile/', RedirectView.as_view(url='/admin')),
    url(r'^$', RedirectView.as_view(url='/home', permanent=True)),
]

handler404 = views.error404
handler500 = views.error500

if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT
    )
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )

    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
