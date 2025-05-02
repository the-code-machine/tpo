from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmployerViewSet, CustomerViewSet

router = DefaultRouter()
router.register(r'employers', EmployerViewSet)
router.register(r'customers', CustomerViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
