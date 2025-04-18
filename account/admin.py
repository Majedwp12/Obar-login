# users/admin.py

from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
    Admin panel configuration for the custom User model.
    """
    list_display = ('id', 'phone', 'last_name', 'email')  # Fields to display in the list view
    search_fields = ('phone', 'first_name', 'last_name', 'email')  # Fields to search by
    list_filter = ()  # No filters added; can be customized later
