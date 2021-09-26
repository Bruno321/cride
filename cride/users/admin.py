"""user models admin"""

# django
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# models
from cride.users.models import User,Profile

class CustomUserAdmin(UserAdmin):
    """User model admin"""
    list_display = ('email','username','is_staff','is_client')
    list_filter = ('is_client','is_staff','created','modified')

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Profile model admin"""
    list_display = ('user','reputation','rides_taken','rides_offered')
    search_fields = ('user__username','user__email','created','modified')
    list_filter = ('reputation',)

admin.site.register(User,CustomUserAdmin)