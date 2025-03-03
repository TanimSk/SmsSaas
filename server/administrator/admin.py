from django.contrib import admin
from administrator.models import User, AdminInfo

admin.site.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_admin', 'is_customer')
    search_fields = ('username', 'email')
    readonly_fields = ('date_joined', 'last_login')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_admin', 'is_customer')}
         ),
    )

    ordering = ('username',)

admin.site.register(AdminInfo)
class AdminInfoAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_sms_quota')
    search_fields = ('user', 'total_sms_quota')
    readonly_fields = ()
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('user', 'total_sms_quota')}
         ),
    )

    ordering = ('user',)