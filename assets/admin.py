from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, Asset, AssetAssignment

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ['serial_number', 'display_name', 'model_category', 'status', 'assigned_user', 'department']
    list_filter = ['status', 'model_category', 'department']
    search_fields = ['serial_number', 'display_name', 'assigned_user__username']
    list_editable = ['status']

@admin.register(AssetAssignment)
class AssetAssignmentAdmin(admin.ModelAdmin):
    list_display = ['asset', 'assigned_to', 'assigned_by', 'assigned_date', 'returned_date']
    list_filter = ['assigned_date', 'returned_date']
    search_fields = ['asset__serial_number', 'assigned_to__username']
