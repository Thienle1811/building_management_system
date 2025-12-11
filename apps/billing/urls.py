from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import MeterReadingViewSet, InvoiceViewSet

router = DefaultRouter()

# Đường dẫn cũ
router.register(r'meter-readings', MeterReadingViewSet, basename='meter-readings')

# Đường dẫn mới (Hóa đơn)
router.register(r'my-invoices', InvoiceViewSet, basename='my-invoices')

urlpatterns = [
    path('', include(router.urls)),
]