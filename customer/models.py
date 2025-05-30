from django.db import models
from django.apps import apps
from datetime import date
from django.contrib.postgres.fields import ArrayField

def default_machine_ids():
    return []

class Customer(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, unique=True)
    email = models.EmailField(blank=True, null=True)
    sync_enabled = models.BooleanField(default=False)
    machine_ids = models.JSONField(default=default_machine_ids, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)  # ✅ account creation time

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
                defaults={'description': '7-day free access', 'price': 0, 'duration_days': 7}
            )
            Subscription.objects.create(
                customer=self,
                plan=plan,
                start_date=date.today()
            )

class SharedFirm(models.Model):
    firm = models.ForeignKey('sync.Firm', on_delete=models.SET_NULL,null=True,blank=True, related_name='shared_with')
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, related_name='shared_firms')
    role = models.CharField(max_length=50)
    shared_at = models.DateTimeField(auto_now_add=True)


