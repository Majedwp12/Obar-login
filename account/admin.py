# users/admin.py
from django.contrib import admin
from .models import User

class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'phone', 'last_name', 'email')
    search_fields = ('phone', 'first_name', 'last_name', 'email')
    list_filter = ()

admin.site.register(User, UserAdmin)
