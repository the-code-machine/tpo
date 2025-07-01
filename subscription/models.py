from django.db import models
from datetime import timedelta, date
from customer.models import Customer
from django.core.exceptions import ValidationError
import os

import uuid

def exe_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join("executables", filename)

class ExecutableFile(models.Model):
    PLATFORM_CHOICES = [
        ('windows', 'Windows'),
        ('mac', 'macOS'),
    ]

    file = models.FileField(upload_to=exe_upload_path)
    version = models.CharField(max_length=50)
    platform = models.CharField(max_length=10, choices=PLATFORM_CHOICES)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        # Ensure only one file per platform
        if not self.pk and ExecutableFile.objects.filter(platform=self.platform).exists():
            raise ValidationError(f"Executable for {self.platform} already exists.")

    def save(self, *args, **kwargs):
        self.full_clean()
        try:
            old_instance = ExecutableFile.objects.get(pk=self.pk)
            if old_instance.file and old_instance.file != self.file:
                old_instance.file.delete(save=False)
        except ExecutableFile.DoesNotExist:
            pass
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.platform.upper()} v{self.version}"
 
    
class Plan(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.PositiveIntegerField()
    discount = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text="Discount in percentage (e.g. 10.00 for 10%)"
    )
    max_devices = models.PositiveIntegerField(
        default=1,
        help_text="Number of devices allowed per user for this plan"
    )
    max_firms = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Number of firms allowed (leave empty for unlimited)"
    )

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
