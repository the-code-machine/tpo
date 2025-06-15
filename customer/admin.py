from datetime import date
from django.utils.translation import gettext_lazy as _
from django.contrib.admin import SimpleListFilter
from .models import Customer
from subscription.models import Subscription  # adjust if your app name is different
from django.contrib import admin
from django.http import HttpResponse

class PlanTypeFilter(SimpleListFilter):
    title = _('Plan Type')
    parameter_name = 'plan_type'

    def lookups(self, request, model_admin):
        plans = set(Subscription.objects.select_related('plan').values_list('plan__name', flat=True))
        return [(plan, plan) for plan in plans]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(subscriptions__plan__name=self.value())
        return queryset


class SubscriptionEndDateFilter(SimpleListFilter):
    title = _('Subscription End Date')
    parameter_name = 'subscription_end'

    def lookups(self, request, model_admin):
        return [
            ('expired', _('Expired')),
            ('today', _('Ends Today')),
            ('future', _('Ends in Future')),
        ]

    def queryset(self, request, queryset):
        today = date.today()
        if self.value() == 'expired':
            return queryset.filter(subscriptions__end_date__lt=today)
        elif self.value() == 'today':
            return queryset.filter(subscriptions__end_date=today)
        elif self.value() == 'future':
            return queryset.filter(subscriptions__end_date__gt=today)
        return queryset


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'created_at')
    search_fields = ('name', 'email', 'phone')
    actions = ['download_as_csv']
    list_filter = [PlanTypeFilter, SubscriptionEndDateFilter]

    def download_as_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=customers.csv'

        writer = csv.writer(response)
        writer.writerow(['Name', 'Email', 'Phone', 'Created At'])

        for customer in queryset:
            writer.writerow([customer.name, customer.email, customer.phone, customer.created_at])

        return response

    download_as_csv.short_description = "Download selected customers as CSV"

