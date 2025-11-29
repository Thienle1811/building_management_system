"""
URL configuration for config project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# --- BỔ SUNG IMPORT NÀY ---
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # Trang quản trị mặc định của Django
    path('admin/', admin.site.urls),
    
    # --- KHU VỰC API (Dành cho Mobile App) ---
    
    # 1. API Xác thực (Login - Lấy Token) <--- PHẦN BẠN ĐANG THIẾU
    path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # 2. Các API Nghiệp vụ
    path('api/v1/', include('apps.residents.urls')), 
    path('api/v1/mobile/', include('apps.contracts.urls_api')),
    path('api/v1/feedback/', include('apps.feedback.urls_api')), 
    
    # --- KHU VỰC WEB (Dành cho BQL trên Desktop) ---
    path('residents/', include('apps.residents.urls_web')), 
    path('', include('apps.landing.urls')),
    path('contracts/', include('apps.contracts.urls')),
    path('buildings/', include('apps.buildings.urls')),
    path('feedback/', include('apps.feedback.urls')),   
    path('notifications/', include('apps.notifications.urls')),
    path('api/v1/notifications/', include('apps.notifications.urls_api')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)