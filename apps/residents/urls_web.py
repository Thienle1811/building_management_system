from django.urls import path
from . import views

app_name = 'residents'  # Bắt buộc phải có dòng này

urlpatterns = [
    # Cư dân
    path('', views.resident_list_view, name='resident_list'),
    path('create/', views.resident_create_view, name='resident_create'),
    path('update/<int:pk>/', views.resident_update_view, name='resident_update'),
    path('delete/<int:pk>/', views.resident_delete_view, name='resident_delete'),

    # Phương tiện
    path('vehicles/', views.vehicle_list_view, name='vehicle_list'),
    path('vehicles/add/', views.vehicle_create_view, name='vehicle_create'),
    path('vehicles/<int:pk>/edit/', views.vehicle_update_view, name='vehicle_update'),
    path('vehicles/<int:pk>/delete/', views.vehicle_delete_view, name='vehicle_delete'),
]