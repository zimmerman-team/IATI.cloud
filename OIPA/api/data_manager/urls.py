from django.conf.urls import url

import api.data_manager.views

app_name = 'api'
urlpatterns = [
    url(r'^dataset_update',
        api.data_manager.views.dataset_update,
        name="dataset_update"),
    url(r'^auth_registration',
        api.data_manager.views.auth_registration,
        name="auth_registration"),
]
