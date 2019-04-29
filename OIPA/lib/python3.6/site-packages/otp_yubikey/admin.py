from __future__ import absolute_import, division, print_function, unicode_literals

from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered

from .models import YubikeyDevice, ValidationService, RemoteYubikeyDevice


class YubikeyDeviceAdmin(admin.ModelAdmin):
    """
    :class:`~django.contrib.admin.ModelAdmin` for
    :class:`~otp_yubikey.models.YubikeyDevice`.
    """
    list_display = ['user', 'name', 'public_id']

    fieldsets = [
        ('Identity', {
            'fields': ['user', 'name', 'confirmed'],
        }),
        ('Configuration', {
            'fields': ['private_id', 'key'],
        }),
        ('State', {
            'fields': ['session', 'counter'],
        }),
    ]
    raw_id_fields = ['user']


class ValidationServiceAdmin(admin.ModelAdmin):
    """
    :class:`~django.contrib.admin.ModelAdmin` for
    :class:`~otp_yubikey.models.ValidationService`.
    """
    fieldsets = [
        ('Common Options', {
            'fields': ['name', 'api_id', 'api_key'],
        }),
        ('Other Options', {
            'fields': ['base_url', 'api_version', 'use_ssl', 'param_sl',
                       'param_timeout'],
        }),
    ]
    radio_fields = {'api_version': admin.HORIZONTAL}


class RemoteYubikeyDeviceAdmin(admin.ModelAdmin):
    """
    :class:`~django.contrib.admin.ModelAdmin` for
    :class:`~otp_yubikey.models.RemoteYubikeyDevice`.
    """
    fieldsets = [
        ('Identity', {
            'fields': ['user', 'name', 'confirmed'],
        }),
        ('Configuration', {
            'fields': ['service', 'public_id'],
        }),
    ]
    raw_id_fields = ['user']


try:
    admin.site.register(YubikeyDevice, YubikeyDeviceAdmin)
    admin.site.register(ValidationService, ValidationServiceAdmin)
    admin.site.register(RemoteYubikeyDevice, RemoteYubikeyDeviceAdmin)
except AlreadyRegistered:
    # Useless exception triggered by multiple imports.
    pass
