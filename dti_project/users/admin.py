from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Notification, User


class UserAdmin(BaseUserAdmin):
    list_display = ('first_name', 'last_name', 'role', 'email', 'is_staff')
    list_filter = ('is_staff', 'role')
    search_fields = ('first_name', 'last_name', 'email')

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Profile', {
            'fields': (
                'role',
                'profile_picture',
                'is_verified',
                'verification_code',
                'verification_code_expiration_date'
            ),
        }),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (None, {
            'classes': ('wide',),
            'fields': (
                'role',
                'profile_picture',
                'is_verified',
                'verification_code',
                'verification_code_expiration_date'
            ),
        }),
    )

    def save_model(self, request, obj, form, change):
        # If superuser → force role to admin
        if obj.is_superuser:
            obj.role = 'admin'
        # If admin role → always staff
        if obj.role == "admin":
            obj.is_staff = True
        super().save_model(request, obj, form, change)

# register AFTER defining the class
admin.site.register(User, UserAdmin)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'date')
    search_fields = ('user',)
