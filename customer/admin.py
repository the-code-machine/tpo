from django.contrib import admin
from .models import Customer, Employer

class EmployerInline(admin.TabularInline):
    model = Employer
    extra = 0
    show_change_link = True

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone')
    search_fields = ('name', 'email', 'phone')
    inlines = [EmployerInline]

@admin.register(Employer)
class EmployerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'role', 'is_active', 'customer')
    list_filter = ('role', 'is_active')
    search_fields = ('name', 'email')
