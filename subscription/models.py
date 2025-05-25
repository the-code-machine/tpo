from django.db import models
from datetime import timedelta, date
from customer.models import Customer

import os

import uuid

def exe_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join("executables", filename)

class ExecutableFile(models.Model):
    file = models.FileField(upload_to=exe_upload_path)

    def save(self, *args, **kwargs):
        # Delete old file if it exists
        try:
            old_instance = ExecutableFile.objects.get(pk=self.pk)
            if old_instance.file and old_instance.file != self.file:
                old_instance.file.delete(save=False)
        except ExecutableFile.DoesNotExist:
            pass
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Executable - {self.file.name}"
    
    
class Plan(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.PositiveIntegerField()
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, help_text="Discount in percentage (e.g. 10.00 for 10%)")

    def __str__(self):
        return f"{self.name} ({self.duration_days} days - ₹{self.price})"

    @property
    def discounted_price(self):
        return self.price * (1 - self.discount / 100)


class Subscription(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        # Auto-fill start_date with today's date if not set
        if not self.start_date:
            self.start_date = date.today()

        # Auto-fill end_date based on plan duration
        if self.plan and self.start_date and not self.end_date:
            self.end_date = self.start_date + timedelta(days=self.plan.duration_days)

        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return self.end_date and self.end_date < date.today()

    def __str__(self):
        return f"{self.plan.name} - {self.customer.name}"
