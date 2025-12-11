from django.db.models import Count, Q
from django.utils import timezone
from .models import StaffProfile, StaffRoster, MaintenanceTask

class AssignmentService:
    @staticmethod
    def get_target_team(category):
        """
        Xác định Tổ đội dựa trên cấu hình trong Database.
        Không còn đoán mò bằng từ khóa nữa!
        """
        if category and hasattr(category, 'target_team'):
            return category.target_team
        
        # Fallback nếu không có category (hiếm gặp)
        return 'MAINTENANCE'

    @staticmethod
    def find_best_staff(team_code):
        """Thuật toán tìm nhân viên tối ưu"""
        now = timezone.localtime(timezone.now()) 
        current_time = now.time()
        today = now.date()

        print(f"--- AUTO ASSIGNMENT DEBUG ---")
        print(f"Team cần tìm: {team_code}")
        print(f"Thời gian: {today} {current_time}")

        # 1. Tìm nhân viên thuộc Tổ này và ĐANG CÓ CA TRỰC
        active_rosters = StaffRoster.objects.filter(
            date=today,
            shift__start_time__lte=current_time,
            shift__end_time__gte=current_time,
            staff__team=team_code,
            staff__status='ACTIVE'
        )
        
        if not active_rosters.exists():
            print("=> KHÔNG CÓ AI ĐANG TRỰC! (Sẽ tạo Task trạng thái Pending)")
            return None 

        candidate_ids = active_rosters.values_list('staff_id', flat=True)

        # 2. Load Balancing: Tìm người ít việc nhất
        best_candidate = StaffProfile.objects.filter(id__in=candidate_ids).annotate(
            active_task_count=Count('tasks', filter=Q(tasks__status__in=['PENDING', 'IN_PROGRESS']))
        ).order_by('active_task_count').first()
        
        if best_candidate:
             print(f"=> ĐÃ CHỌN: {best_candidate.user.username} (Đang làm {best_candidate.active_task_count} việc)")

        return best_candidate

    @staticmethod
    def auto_create_and_assign_task(feedback):
        """Hàm chính: Tạo Task và Gán việc"""
        # 1. Lấy tổ đội từ cấu hình Category
        target_team = AssignmentService.get_target_team(feedback.category)
        
        # 2. Tìm người phù hợp trong tổ đó
        assignee = AssignmentService.find_best_staff(target_team)
        
        # 3. Tạo Task
        task = MaintenanceTask.objects.create(
            feedback=feedback,
            staff=assignee,
            status='PENDING', # Luôn là Pending, nhân viên phải bấm "Nhận việc"
            assigned_at=timezone.now() if assignee else None
        )
        
        return task