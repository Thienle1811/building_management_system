from django.db.models import Count, Q
from django.utils import timezone
from .models import StaffProfile, StaffRoster, MaintenanceTask

class AssignmentService:
    @staticmethod
    def get_target_team(category_name):
        """Xác định Tổ đội chính xác hơn"""
        cat_lower = category_name.lower()
        
        # 1. Nhóm Kỹ Thuật (Điện, Nước, Thang máy...) -> Trả về MAINTENANCE
        if any(x in cat_lower for x in ['điện', 'nước', 'kỹ thuật', 'bảo trì', 'thang máy', 'đèn', 'ống']):
            return 'MAINTENANCE' 
            
        # 2. Nhóm Vệ Sinh (Rác, Cây cảnh...) -> Trả về CLEANING
        if any(x in cat_lower for x in ['rác', 'vệ sinh', 'bẩn', 'cây', 'hành lang']):
            return 'CLEANING'
            
        # 3. Nhóm An Ninh -> Trả về SECURITY
        if any(x in cat_lower for x in ['an ninh', 'ồn ào', 'đỗ xe', 'trộm', 'người lạ']):
            return 'SECURITY'
            
        return 'MAINTENANCE' # Mặc định giao cho kỹ thuật nếu không rõ

    @staticmethod
    def find_best_staff(team_code):
        """Thuật toán tìm nhân viên tối ưu"""
        # --- SỬA ĐỔI QUAN TRỌNG: Lấy giờ theo múi giờ Việt Nam ---
        now = timezone.localtime(timezone.now()) 
        current_time = now.time()
        today = now.date()

        # In log ra màn hình đen (Terminal) để debug
        print(f"--- DEBUG ASSIGNMENT ---")
        print(f"Team cần tìm: {team_code}")
        print(f"Thời gian hệ thống (VN): {today} {current_time}")

        # 1. Tìm nhân viên thuộc Tổ này và ĐANG CÓ CA TRỰC
        active_rosters = StaffRoster.objects.filter(
            date=today,
            shift__start_time__lte=current_time,
            shift__end_time__gte=current_time,
            staff__team=team_code,
            staff__status='ACTIVE'
        )
        
        print(f"Số người đang trực tìm thấy: {active_rosters.count()}")

        if not active_rosters.exists():
            print("=> KHÔNG CÓ AI ĐANG TRỰC!")
            return None # Không có ai đang trực

        # Lấy danh sách ID nhân viên đang trực
        candidate_ids = active_rosters.values_list('staff_id', flat=True)

        # 2. Load Balancing: Tìm người ít việc nhất
        best_candidate = StaffProfile.objects.filter(id__in=candidate_ids).annotate(
            active_task_count=Count('tasks', filter=Q(tasks__status__in=['PENDING', 'IN_PROGRESS']))
        ).order_by('active_task_count').first()
        
        if best_candidate:
             print(f"=> ỨNG VIÊN TỐT NHẤT: {best_candidate.user.username}")

        return best_candidate

    @staticmethod
    def auto_create_and_assign_task(feedback):
        """Hàm chính: Tạo Task và Gán việc"""
        # 1. Xác định tổ đội cần xử lý
        target_team = AssignmentService.get_target_team(feedback.category.name if feedback.category else "")
        
        # 2. Tìm người
        assignee = AssignmentService.find_best_staff(target_team)
        
        # 3. Tạo Task
        task = MaintenanceTask.objects.create(
            feedback=feedback,
            staff=assignee,
            status='PENDING', # Nếu có người thì vẫn là Pending chờ họ bấm "Nhận"
            assigned_at=timezone.now() if assignee else None
        )
        
        return task