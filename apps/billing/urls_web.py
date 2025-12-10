from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    # Danh sách hóa đơn
    path('invoices/', views.invoice_list, name='invoice_list'),
    
    # Chi tiết hóa đơn
    path('invoices/<int:pk>/', views.invoice_detail, name='invoice_detail'),
    
    # Action xác nhận thanh toán (Xử lý POST)
    path('invoices/<int:pk>/confirm/', views.invoice_confirm_payment, name='invoice_confirm_payment'),
]