from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ResidentViewSet, ChangePasswordView

router = DefaultRouter()
router.register(r'', ResidentViewSet, basename='resident')

urlpatterns = [
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('', include(router.urls)),
]