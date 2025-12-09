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
    # Lưu ý: Các dòng này ánh xạ đến urls_api.py hoặc urls.py của từng app
    path('api/v1/residents/', include('apps.residents.urls')), # Router residents thường nằm trong này
    path('api/v1/feedback/', include('apps.feedback.urls_api')),
    path('api/v1/notifications/', include('apps.notifications.urls_api')),
    path('api/v1/contracts/', include('apps.contracts.urls_api')),
    
    # ===> THÊM DÒNG NÀY CHO BILLING <===
    path('api/v1/billing/', include('apps.billing.urls')),

    # --- Web Views (Ban Quản Lý) ---
    path('', include('apps.landing.urls')),
    path('residents/', include('apps.residents.urls_web')), # Tách riêng web và api nếu cần
    path('contracts/', include('apps.contracts.urls')),
    path('buildings/', include('apps.buildings.urls')),
    path('feedback/', include('apps.feedback.urls')),
    path('notifications/', include('apps.notifications.urls')),

]

# Cấu hình để phục vụ file media (ảnh/pdf) trong môi trường DEV
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)