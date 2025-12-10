from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.feedback.models import Feedback
from .services import AssignmentService

@receiver(post_save, sender=Feedback)
def trigger_auto_assignment(sender, instance, created, **kwargs):
    """Khi Feedback mới được tạo -> Tự động tạo Task và phân công"""
    if created:
        # Gọi Service phân công
        AssignmentService.auto_create_and_assign_task(instance)