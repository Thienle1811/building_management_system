from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import FeedbackViewSet, FeedbackCategoryViewSet

router = DefaultRouter()
router.register(r'categories', FeedbackCategoryViewSet, basename='feedback-categories')
router.register(r'list', FeedbackViewSet, basename='feedbacks')

urlpatterns = [
    path('', include(router.urls)),
]