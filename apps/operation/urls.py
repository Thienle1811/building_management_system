from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, api_views

app_name = 'operation'

router = DefaultRouter()
router.register(r'rosters', api_views.RosterAPIViewSet, basename='api_rosters')
router.register(r'my-tasks', api_views.StaffTaskViewSet, basename='api_my_tasks')

urlpatterns = [
    # Giao diện Web
    path('roster/', views.roster_calendar_view, name='roster_view'),
    path('reports/', views.performance_dashboard, name='performance_report'),
    
    # APIs phục vụ cho Web
    path('api/', include(router.urls)),
    path('api/master-data/', api_views.OperationMasterDataViewSet.as_view({'get': 'list'}), name='api_master_data'),
]