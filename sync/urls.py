from .views import sync_data, fetch_data, toggle_firm_sync_enabled,delete_firm_with_shared
from django.urls import path
urlpatterns = [
    path('sync/', sync_data),
    path('fetch/', fetch_data),  
    path('delete-with-shared/', delete_firm_with_shared, name='delete_with_shared'),  # Assuming this is for deleting with shared firms
    path('toggle-sync/', toggle_firm_sync_enabled), 
]
