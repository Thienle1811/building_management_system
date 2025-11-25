from django.urls import path
from .views import resident_list, resident_create, resident_update, resident_delete # <--- Import thêm

urlpatterns = [
    path('', resident_list, name='resident_list_web'),
    path('create/', resident_create, name='resident_create_web'),
    
    # Đường dẫn Sửa (nhận ID cư dân)
    path('update/<int:pk>/', resident_update, name='resident_update_web'),
    
    # Đường dẫn Xóa (nhận ID cư dân)
    path('delete/<int:pk>/', resident_delete, name='resident_delete_web'),
]