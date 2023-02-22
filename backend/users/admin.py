from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


class UserAdmin(UserAdmin):
    list_display = (
        'username', 'email', 'first_name', 'last_name', 'role'
    )
    list_display = ('username', 'email',
                    'first_name', 'last_name', 'role')
    fieldsets = (("User",
                 {"fields": (
                     'username', 'password', 'email',
                     'first_name', 'last_name',
                     'role', 'last_login', 'date_joined')}),)
    search_fields = ('first_name', 'email',)
    list_filter = ('email', 'first_name',)


admin.site.register(User, UserAdmin)