from django.apps import AppConfig


class CotractsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.contracts'  # <--- Quan trọng
    verbose_name = 'Quản lý Hợp đồng'
