"""
URL configuration for config project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Trang quản trị mặc định của Django
    path('admin/', admin.site.urls),
    
    # --- KHU VỰC API (Dành cho Mobile App) ---
    path('api/v1/', include('apps.residents.urls')), 
    path('api/v1/mobile/', include('apps.contracts.urls_api')),
    # ĐÃ SỬA: Thêm tiền tố api/v1/ để không trùng với Web
    path('api/v1/feedback/', include('apps.feedback.urls_api')), 
    
    # --- KHU VỰC WEB (Dành cho BQL trên Desktop) ---
    path('residents/', include('apps.residents.urls_web')), 
    path('', include('apps.landing.urls')),
    path('contracts/', include('apps.contracts.urls')),
    path('buildings/', include('apps.buildings.urls')),
    path('feedback/', include('apps.feedback.urls')),   
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)