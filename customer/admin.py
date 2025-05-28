from django.contrib import admin
from .models import Customer
import csv
from django.http import HttpResponse

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone','created_at')
    search_fields = ('name', 'email', 'phone')
    actions = ['download_as_csv']

    def download_as_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=customers.csv'

        writer = csv.writer(response)
        writer.writerow(['Name', 'Email', 'Phone', 'Created At'])  # header

        for customer in queryset:
            writer.writerow([customer.name, customer.email, customer.phone, customer.created_at])

        return response

    download_as_csv.short_description = "Download selected customers as CSV"



