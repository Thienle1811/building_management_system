from django.contrib import admin
from .models import StaffProfile, ShiftConfig, StaffRoster, MaintenanceTask

@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'team', 'status', 'phone', 'created_at')
    list_filter = ('team', 'status')
    search_fields = ('user__username', 'user__first_name', 'phone')

@admin.register(ShiftConfig)
class ShiftConfigAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_time', 'end_time', 'is_active')
    list_editable = ('is_active',)
    search_fields = ('name',)

@admin.register(StaffRoster)
class StaffRosterAdmin(admin.ModelAdmin):
    list_display = ('date', 'staff', 'shift', 'created_at')
    list_filter = ('date', 'shift', 'staff__team')
    date_hierarchy = 'date'

@admin.register(MaintenanceTask)
class MaintenanceTaskAdmin(admin.ModelAdmin):
    list_display = ('code', 'feedback', 'staff', 'status', 'assigned_at')
    list_filter = ('status', 'staff__team')
    search_fields = ('code', 'feedback__title')