from .views import sync_data, fetch_data, toggle_customer_sync
from django.urls import path
urlpatterns = [
    path('sync/', sync_data),
    path('fetch/', fetch_data),  
    path('toggle-sync/', toggle_customer_sync), 
]
