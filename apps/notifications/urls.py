from django.urls import path
from . import views

urlpatterns = [
    path('', views.notification_list, name='notification_list'),
    path('mark-read/', views.mark_all_read, name='notification_mark_read'),
    path('create/', views.notification_create, name='notification_create'),
]