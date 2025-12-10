from django.contrib import admin
from .models import StaffProfile, ShiftConfig, StaffRoster, MaintenanceTask

@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ('user_full_name', 'team', 'status', 'phone_number')
    list_filter = ('team', 'status')
    search_fields = ('user__username', 'user__first_name', 'phone_number')

    def user_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    user_full_name.short_description = 'Họ tên'

@admin.register(ShiftConfig)
class ShiftConfigAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_time', 'end_time', 'color_code', 'is_active')
    list_editable = ('color_code', 'is_active')

@admin.register(StaffRoster)
class StaffRosterAdmin(admin.ModelAdmin):
    list_display = ('date', 'staff', 'shift', 'created_at')
    list_filter = ('date', 'shift', 'staff__team')
    date_hierarchy = 'date'
    search_fields = ('staff__user__username',)

@admin.register(MaintenanceTask)
class MaintenanceTaskAdmin(admin.ModelAdmin):
    list_display = ('code', 'feedback_title', 'staff', 'status', 'assigned_at')
    list_filter = ('status', 'staff', 'assigned_at')
    readonly_fields = ('code', 'feedback')

    def feedback_title(self, obj):
        return f"{obj.feedback.title} ({obj.feedback.apartment.apartment_code})"
    feedback_title.short_description = "Yêu cầu từ Cư dân"