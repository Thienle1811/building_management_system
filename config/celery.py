import os
from celery import Celery
from celery.schedules import crontab

# Thiết lập biến môi trường cho Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')

# Load config từ file settings.py, tìm các biến bắt đầu bằng CELERY_
app.config_from_object('django.conf:settings', namespace='CELERY')

# Tự động tìm tasks trong các app đã cài (apps.notifications, apps.residents...)
app.autodiscover_tasks()

# --- CẤU HÌNH LỊCH TRÌNH (BEAT SCHEDULE) ---
# Quét DB mỗi 1 phút để tìm các thông báo hẹn giờ cần gửi
app.conf.beat_schedule = {
    'check-scheduled-notifications-every-minute': {
        'task': 'apps.notifications.tasks.send_scheduled_notifications',
        'schedule': crontab(minute='*/1'), # Chạy mỗi phút
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')