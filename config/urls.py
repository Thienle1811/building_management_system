"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Trang quản trị mặc định của Django
    path('admin/', admin.site.urls),
    
    # 1. Đường dẫn cho API (Dành cho Mobile App)
    # Ví dụ: http://127.0.0.1:8000/api/v1/residents/
    path('api/v1/', include('apps.residents.urls')), 
    
    # 2. Đường dẫn cho WEB Giao diện (Dành cho BQL trên Desktop)
    # Ví dụ: http://127.0.0.1:8000/residents/
    path('residents/', include('apps.residents.urls_web')), 
    # Landing Page (Trang chủ)
    path('', include('apps.landing.urls')),
    path('contracts/', include('apps.contracts.urls')),
    path('api/v1/mobile/', include('apps.contracts.urls_api')),
    path('buildings/', include('apps.buildings.urls')),
]

# Cấu hình để xem được ảnh upload trong môi trường dev (Debug mode)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)