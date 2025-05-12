from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmployerViewSet, CustomerViewSet, send_otp_view, verify_otp_view

router = DefaultRouter()
router.register(r'employers', EmployerViewSet)
router.register(r'customers', CustomerViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('send-otp/', send_otp_view, name='send-otp'),
    path('verify-otp/', verify_otp_view, name='verify-otp'),
]
