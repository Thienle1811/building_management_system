from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # --- JWT Authentication ---
    path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # --- API Endpoints (Mobile App) ---
    path('api/v1/residents/', include('apps.residents.urls')), 
    path('api/v1/feedback/', include('apps.feedback.urls_api')),
    path('api/v1/notifications/', include('apps.notifications.urls_api')),
    path('api/v1/contracts/', include('apps.contracts.urls_api')),
    path('api/v1/billing/', include('apps.billing.urls')),

    # --- Web Views (Ban Quản Lý) ---
    path('', include('apps.landing.urls')),
    
    # [QUAN TRỌNG] Dòng này kết nối với file urls_web.py ở trên
    path('residents/', include('apps.residents.urls_web')), 
    
    path('contracts/', include('apps.contracts.urls')),
    path('buildings/', include('apps.buildings.urls')),
    path('feedback/', include('apps.feedback.urls')),
    path('notifications/', include('apps.notifications.urls')),
    path('billing/', include('apps.billing.urls_web')),
    path('operation/', include('apps.operation.urls')),
]

# Cấu hình media
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)