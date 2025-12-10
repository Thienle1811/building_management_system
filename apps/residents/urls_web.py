from django.urls import path
from . import views  # Import toàn bộ module views để tránh lỗi import lắt nhắt

# [QUAN TRỌNG] Dòng này giúp Django hiểu namespace 'residents' là gì
app_name = 'residents'

urlpatterns = [
    # --- QUẢN LÝ CƯ DÂN ---
    # (Đảm bảo trong file views.py bạn đã đặt tên hàm đúng như bên dưới)
    path('', views.resident_list_view, name='resident_list'), 
    path('create/', views.resident_create_view, name='resident_create'),
    path('update/<int:pk>/', views.resident_update_view, name='resident_update'),
    path('delete/<int:pk>/', views.resident_delete_view, name='resident_delete'),

    # --- QUẢN LÝ PHƯƠNG TIỆN (XE CỘ) ---
    path('vehicles/', views.vehicle_list_view, name='vehicle_list'),
    path('vehicles/add/', views.vehicle_create_view, name='vehicle_create'),
    path('vehicles/<int:pk>/edit/', views.vehicle_update_view, name='vehicle_update'),
    path('vehicles/<int:pk>/delete/', views.vehicle_delete_view, name='vehicle_delete'),
]