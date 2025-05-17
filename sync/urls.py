from .views import sync_data, fetch_data
from django.urls import path
urlpatterns = [
    path('sync/', sync_data),
    path('fetch/', fetch_data),  
]
