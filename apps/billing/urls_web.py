from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    # Quản lý hóa đơn
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoices/create/', views.invoice_create, name='invoice_create'),
    path('invoices/<int:pk>/', views.invoice_detail, name='invoice_detail'),
    path('invoices/<int:pk>/confirm/', views.invoice_confirm_payment, name='invoice_confirm_payment'),
    
    # Ghi điện nước & Chốt sổ
    path('meter-reading/', views.meter_reading_view, name='meter_reading'),
    path('generate-invoices/', views.generate_invoices_view, name='generate_invoices'), # <--- Mới
    
    # Cấu hình giá
    path('price-config/', views.price_config_view, name='price_config'),
]