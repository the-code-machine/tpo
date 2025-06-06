from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('customer.urls')),
    path('api/', include('sync.urls')),
    path('api/subscription/', include('subscription.urls')),
]
