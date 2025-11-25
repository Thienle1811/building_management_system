from rest_framework.routers import DefaultRouter
from .views import ResidentViewSet

router = DefaultRouter()
router.register(r'residents', ResidentViewSet, basename='residents')

urlpatterns = router.urls