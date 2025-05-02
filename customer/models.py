from django.db import models
from django.apps import apps
from datetime import date
EMPLOYER_ROLES = (
    ('admin', 'Admin'),
    ('manager', 'Manager'),
    ('sales', 'Sales'),
    ('support', 'Support'),
)
class Customer(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, unique=True)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)

        if is_new:
            Plan = apps.get_model('subscription', 'Plan')
            Subscription = apps.get_model('subscription', 'Subscription')

            plan, _ = Plan.objects.get_or_create(
                name="Free Trial",
                defaults={
                    'description': '7-day free access',
                    'price': 0,
                    'duration_days': 7
                }
            )
            Subscription.objects.create(
                customer=self,
                plan=plan,
                start_date=date.today()
            )


class Employer(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='employers')
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=EMPLOYER_ROLES)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.role})"


# customer/models.py
