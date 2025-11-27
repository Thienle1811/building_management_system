from django.urls import path
from . import views

urlpatterns = [
    # Đường dẫn: /contracts/
    path('', views.contract_list, name='contract_list'),
    
    # Đường dẫn: /contracts/create/
    path('create/', views.contract_create, name='contract_create'),
    
    # Đường dẫn: /contracts/1/update/
    path('<int:pk>/update/', views.contract_update, name='contract_update'),
    
    # Đường dẫn: /contracts/1/delete/
    path('<int:pk>/delete/', views.contract_delete, name='contract_delete'),
    path('<int:pk>/', views.contract_detail, name='contract_detail'),
]