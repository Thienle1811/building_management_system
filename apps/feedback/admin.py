from django.contrib import admin
from .models import Feedback, FeedbackCategory, FeedbackAttachment, FeedbackStatusHistory

class AttachmentInline(admin.TabularInline):
    model = FeedbackAttachment
    extra = 0

class StatusHistoryInline(admin.TabularInline):
    model = FeedbackStatusHistory
    extra = 0
    readonly_fields = ('old_status', 'new_status', 'changed_by', 'created_at', 'note')
    can_delete = False

@admin.register(FeedbackCategory)
class FeedbackCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'description')

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('code', 'title', 'apartment', 'category', 'status', 'priority', 'created_at')
    list_filter = ('status', 'priority', 'category')
    search_fields = ('code', 'title', 'apartment__apartment_code')
    inlines = [AttachmentInline, StatusHistoryInline]
    readonly_fields = ('code', 'created_at')