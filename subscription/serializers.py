from rest_framework import serializers
from .models import Subscription
from .models import Plan

class PlanSerializer(serializers.ModelSerializer):
    discounted_price = serializers.SerializerMethodField()

    class Meta:
        model = Plan
        fields = [
            'id', 'name', 'description', 'price', 'discount',
            'duration_days', 'discounted_price',
            'max_devices', 'max_firms'
        ]

    def get_discounted_price(self, obj):
        return obj.discounted_price


        
class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = '__all__'
