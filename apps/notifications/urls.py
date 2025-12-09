from django.urls import path
from . import views

urlpatterns = [
    path('', views.notification_list, name='notification_list'),
    path('create/', views.notification_create, name='notification_create'),
    # --- THÊM DÒNG NÀY ---
    path('mark-read/', views.notification_mark_read, name='notification_mark_read'),
]