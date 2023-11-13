# banking_app/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'is_banker', 'is_client')
    list_filter = ('is_staff', 'is_active', 'is_banker', 'is_client')
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('is_banker', 'is_client')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)


