from django.contrib.admin.models import LogEntry
from django.contrib import admin


class LogAdmin(admin.ModelAdmin):
    """Create an admin view of the history/log table"""
    list_display = ('action_time','user','content_type','change_message','is_addition','is_change','is_deletion')
    list_filter = ['action_time','user','content_type']
    ordering = ('-action_time',)
    #We don't want people changing this historical record:
    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        #returning false causes table to not show up in admin page :-(
        #I guess we have to allow changing for now
        return True
    def has_delete_permission(self, request, obj=None):
        return False



    admin.site.register(LogEntry, LogAdmin)
