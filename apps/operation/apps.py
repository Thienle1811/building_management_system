from django.apps import AppConfig

class OperationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.operation'
    verbose_name = 'Quản lý Vận hành & Nhân sự'

    def ready(self):
        import apps.operation.signals # <--- THÊM DÒNG NÀY