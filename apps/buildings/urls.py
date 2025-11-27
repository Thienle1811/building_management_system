from django.urls import path
from . import views

urlpatterns = [
    path('apartments/', views.apartment_list, name='apartment_list'),
    path('apartments/import/', views.apartment_import, name='apartment_import'),
    path('apartments/template/', views.download_template, name='download_template'), # Mới
    path('apartments/floor-plan/', views.floor_plan, name='floor_plan'), # <--- Mới
    path('apartments/search/', views.apartment_search, name='apartment_search'), # <--- Mới
]