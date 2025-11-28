from django.urls import path
from . import views

urlpatterns = [
    # Đường dẫn: /feedback/
    path('', views.feedback_list, name='feedback_list'),
    
    # Đường dẫn: /feedback/1/
    path('<int:pk>/', views.feedback_detail, name='feedback_detail'),

    # --- QUẢN LÝ DANH MỤC (PMS-04-04) ---
    # Bạn đang thiếu 2 dòng này:
    path('categories/', views.category_list, name='category_list'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
]