from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
from two_factor.admin import AdminSiteOTPRequired, AdminSiteOTPRequiredMixin
from two_factor.urls import urlpatterns as tf_urls
from django.urls import reverse
from django.utils.http import is_safe_url
from django.http import HttpResponseRedirect
from django.shortcuts import resolve_url
from django.contrib.auth.views import redirect_to_login


from OIPA import views

admin.autodiscover()


class AdminSiteOTPRequiredMixinRedirSetup(AdminSiteOTPRequired):
    def login(self, request, extra_context=None):
        redirect_to = request.POST.get(
            REDIRECT_FIELD_NAME, request.GET.get(REDIRECT_FIELD_NAME)
        )
        # For users not yet verified the AdminSiteOTPRequired.has_permission
        # will fail. So use the standard admin has_permission check:
        # (is_active and is_staff) and then check for verification.
        # Go to index if they pass, otherwise make them setup OTP device.
        if request.method == "GET" and super(
            AdminSiteOTPRequiredMixin, self
        ).has_permission(request):
            # Already logged-in and verified by OTP
            if request.user.is_verified():
                # User has permission
                index_path = reverse("admin:index", current_app=self.name)
            else:
                # User has permission but no OTP set:
                index_path = reverse("two_factor:setup", current_app=self.name)
            return HttpResponseRedirect(index_path)

        if not redirect_to or not is_safe_url(
            url=redirect_to, allowed_hosts=[request.get_host()]
        ):
            redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)

        return redirect_to_login(redirect_to)


admin.site.__class__ = AdminSiteOTPRequiredMixinRedirSetup
urlpatterns = [
    # url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/queue/', include('django_rq.urls')),
    url(r'^admin/task_queue/', include('task_queue.urls')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include('api.urls')),
    url(r'^home$', view=views.home),
    url(r'^404$', views.error404),
    url(r'^500$', views.error500),
    url(r'^about$', TemplateView.as_view(template_name='home/about.html')),
    url(r'^accounts/profile/', RedirectView.as_view(url='/admin')),
    url(r'^$', RedirectView.as_view(url='/home', permanent=True)),
    url(r'', include(tf_urls, "two_factor")),
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
