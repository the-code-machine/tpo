from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import  CustomerViewSet, send_otp_view, verify_otp_view ,get_user_info_view ,toggle_customer_sync

router = DefaultRouter()
router.register(r'customers', CustomerViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('send-otp/', send_otp_view, name='send-otp'),
    path('verify-otp/', verify_otp_view, name='verify-otp'),
    path('user-info/', get_user_info_view),
    path('toggle-sync/', toggle_customer_sync)  # POST /api/syncloud/toggle-sync/
]
