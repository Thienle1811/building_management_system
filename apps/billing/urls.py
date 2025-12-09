from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import MeterReadingViewSet, InvoiceViewSet

router = DefaultRouter()
router.register(r'meter-readings', MeterReadingViewSet, basename='meter-readings')
# --- THÊM DÒNG NÀY ---
router.register(r'invoices', InvoiceViewSet, basename='invoices')

urlpatterns = [
    path('', include(router.urls)),
]