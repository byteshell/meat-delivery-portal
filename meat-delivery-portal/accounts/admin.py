from django.contrib import admin
from .models import Profile

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'company_name', 'address', 'latitude', 'longitude')
    list_filter = ('role',)
    search_fields = ('user__username', 'company_name')

admin.site.register(Profile, ProfileAdmin)