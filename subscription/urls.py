from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SubscriptionViewSet , PlanViewSet
from .views import CreatePaymentOrder, VerifyPaymentAndSubscribe
router = DefaultRouter()
router.register(r'subscriptions', SubscriptionViewSet)
router.register(r'plans', PlanViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('create-order/', CreatePaymentOrder.as_view(), name='create-order'),
    path('verify-payment/', VerifyPaymentAndSubscribe.as_view(), name='verify-payment'),

]
