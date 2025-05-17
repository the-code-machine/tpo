# customer/serializers.py

from rest_framework import serializers
from .models import  Customer
from subscription.models import Subscription, Plan
from datetime import date, timedelta



class CustomerSerializer(serializers.ModelSerializer):
    otp = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Customer
        fields = ['id', 'name', 'phone', 'email', 'otp',]  # ✅ explicitly list model fields + otp

    def validate_phone(self, value):
        if not value.isdigit() or len(value) != 10:
            raise serializers.ValidationError("Enter a valid 10-digit mobile number.")
        return value

    def create(self, validated_data):
        validated_data.pop('otp')  # remove OTP before model save
        customer = super().create(validated_data)

        # Assign free 7-day plan
        plan, _ = Plan.objects.get_or_create(
            name="Free Trial",
            defaults={
                'description': '7-day free access',
                'price': 0,
                'duration_days': 7
            }
        )
        Subscription.objects.create(
            customer=customer,
            plan=plan,
            start_date=date.today()
        )

        return customer


class CustomerSyncToggleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['sync_enabled']