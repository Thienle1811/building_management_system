from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import MobileContractViewSet

router = DefaultRouter()
router.register(r'contracts', MobileContractViewSet, basename='mobile-contracts')

urlpatterns = [
    path('', include(router.urls)),
]