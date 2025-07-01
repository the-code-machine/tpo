from django.contrib import admin
from .models import Plan, Subscription, ExecutableFile
from django.utils.html import format_html
@admin.register(ExecutableFile)
class ExecutableFileAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'platform', 'uploaded_at', 'file_link']

    def file_link(self, obj):
        if obj.file:
            return format_html(f'<a href="{obj.file.url}" target="_blank">Download</a>')
        return "-"
    file_link.short_description = 'File Link'

    def has_add_permission(self, request):
        # Allow adding if platform-specific file doesn't exist
        count = ExecutableFile.objects.count()
        if count >= 2:  # One for windows and one for mac
            return False
        return super().has_add_permission(request)

    
@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'duration_days')

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('customer_display', 'plan', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active', 'plan')
    exclude = ('end_date',)

    def customer_display(self, obj):
        return f"{obj.customer.name} ({obj.customer.phone})"
    customer_display.short_description = 'Customer'

