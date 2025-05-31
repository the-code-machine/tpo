from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
CustomerViewSet,
send_otp_view,
verify_otp_view,
get_user_info_view,
get_firm_users,
share_firm_to_customer,
change_shared_role,
remove_shared_firm,
get_shared_firms_by_phone,
)

router = DefaultRouter()
router.register(r'customers', CustomerViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('send-otp/', send_otp_view, name='send-otp'),
    path('verify-otp/', verify_otp_view, name='verify-otp'),
    path('user-info/', get_user_info_view),
    path('get-firm-users/', get_firm_users), 
    path('share-firm/', share_firm_to_customer),
    path('change-role/', change_shared_role, name='change_shared_role'),
    path('remove-shared-firm/', remove_shared_firm, name='remove_shared_firm'),
    path('get-shared-firms/', get_shared_firms_by_phone, name='get_shared_firms_by_phone')

]
