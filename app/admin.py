from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from app.models import User, PasswordResetToken


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Admin configuration for the custom User model registered with decorator.
    """
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'phone_number',
        'is_staff',
        'is_active',
        'date_joined',
    )
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone_number')


    
@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    """
    Admin configuration for PasswordResetToken registered with decorator.
    """
    list_display = ('user', 'token', 'created_at', 'expires_at', 'is_used')
    list_filter = ('is_used', 'created_at', 'expires_at')
    search_fields = ('user__username', 'user__email', 'token')
    readonly_fields = ('token', 'created_at')
