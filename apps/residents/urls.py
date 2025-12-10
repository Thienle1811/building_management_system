from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ResidentViewSet

# Tạo router cho API
router = DefaultRouter()
router.register(r'', ResidentViewSet, basename='resident')

urlpatterns = [
    path('', include(router.urls)),
]