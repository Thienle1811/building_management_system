import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from django.utils.dateparse import parse_date
from django.utils import timezone  # Import timezone
from .models import Feedback, FeedbackStatusHistory, FeedbackCategory
from .forms import FeedbackCategoryForm
from apps.notifications.services import NotificationService  # <--- Import Service

# Logger
logger = logging.getLogger(__name__)

# --- PHẦN 1: QUẢN LÝ PHẢN HỒI ---

def feedback_list(request):
    """
    Màn hình danh sách phản hồi cho BQL
    """
    feedbacks = Feedback.objects.select_related('resident', 'apartment', 'category').order_by('-created_at')
    
    # Lấy tham số Filter
    status = request.GET.get('status')
    category_id = request.GET.get('category')
    q = request.GET.get('q')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    # Áp dụng Filter
    if status:
        feedbacks = feedbacks.filter(status=status)
    if category_id:
        feedbacks = feedbacks.filter(category_id=category_id)
    if q:
        feedbacks = feedbacks.filter(
            Q(title__icontains=q) | 
            Q(code__icontains=q) |
            Q(resident__full_name__icontains=q) |
            Q(apartment__apartment_code__icontains=q)
        )
    if date_from:
        d_from = parse_date(date_from)
        if d_from:
            feedbacks = feedbacks.filter(created_at__date__gte=d_from)
    if date_to:
        d_to = parse_date(date_to)
        if d_to:
            feedbacks = feedbacks.filter(created_at__date__lte=d_to)

    context = {
        'feedbacks': feedbacks,
        'categories': FeedbackCategory.objects.all(),
        'status_choices': Feedback.STATUS_CHOICES,
        'request_data': request.GET
    }
    return render(request, 'feedback/feedback_list.html', context)

def feedback_detail(request, pk):
    """
    Chi tiết phản hồi & Cập nhật trạng thái
    """
    feedback = get_object_or_404(Feedback, pk=pk)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        note = request.POST.get('note')
        
        if new_status and new_status != feedback.status:
            try:
                print(f"🔄 [UPDATE] Đang cập nhật Feedback {feedback.code} từ {feedback.status} -> {new_status}")
                
                # 1. Lưu lịch sử
                FeedbackStatusHistory.objects.create(
                    feedback=feedback,
                    old_status=feedback.status,
                    new_status=new_status,
                    changed_by=request.user,
                    note=note
                )
                
                # Lưu trạng thái cũ để so sánh (nếu cần logic phức tạp hơn)
                old_status = feedback.status
                
                # 2. Cập nhật trạng thái mới
                feedback.status = new_status
                feedback.internal_note = note
                if new_status == 'DONE':
                    feedback.resolved_at = timezone.now()
                
                feedback.save()
                
                # --- GỌI NOTIFICATION SERVICE ---
                # Gửi thông báo cho cư dân
                print("🚀 [NOTIFY] Đang gọi service gửi thông báo...")
                NotificationService.send_feedback_notification(feedback, old_status, new_status)
                # --------------------------------------------

                messages.success(request, f"Cập nhật thành công: {feedback.get_status_display()}")
                
            except Exception as e:
                logger.error(f"Lỗi update feedback: {e}")
                print(f"❌ Lỗi update feedback: {e}")
                messages.error(request, "Có lỗi xảy ra khi cập nhật.")
            
            return redirect('feedback_detail', pk=pk)

    return render(request, 'feedback/feedback_detail.html', {'feedback': feedback})


# --- PHẦN 2: QUẢN LÝ DANH MỤC ---

def category_list(request):
    """Danh sách danh mục & Form tạo mới/Sửa"""
    categories = FeedbackCategory.objects.all().order_by('created_at')
    
    if request.method == 'POST':
        cat_id = request.POST.get('cat_id')
        if cat_id:
            cat_instance = get_object_or_404(FeedbackCategory, pk=cat_id)
            form = FeedbackCategoryForm(request.POST, instance=cat_instance)
            action_msg = "Cập nhật"
        else:
            form = FeedbackCategoryForm(request.POST)
            action_msg = "Tạo mới"
            
        if form.is_valid():
            form.save()
            messages.success(request, f"{action_msg} danh mục thành công!")
            return redirect('category_list')
        else:
            messages.error(request, "Vui lòng kiểm tra lại thông tin.")
    else:
        form = FeedbackCategoryForm()

    return render(request, 'feedback/category_list.html', {
        'categories': categories,
        'form': form
    })

def category_delete(request, pk):
    """Xóa danh mục & Chuyển dữ liệu cũ sang 'Khác'"""
    category = get_object_or_404(FeedbackCategory, pk=pk)
    
    if not category.is_deletable:
        messages.error(request, "Danh mục này là mặc định hệ thống, không thể xóa!")
        return redirect('category_list')

    if request.method == 'POST':
        try:
            other_cat = FeedbackCategory.objects.get(code='OTHER')
            count = category.feedbacks.count()
            
            if count > 0:
                category.feedbacks.update(category=other_cat)
                messages.warning(request, f"Đã chuyển {count} phản hồi cũ sang danh mục 'Khác'.")
            
            category.delete()
            messages.success(request, f"Đã xóa danh mục {category.name}.")
            
        except FeedbackCategory.DoesNotExist:
            messages.error(request, "Lỗi: Không tìm thấy danh mục 'Khác' để chuyển dữ liệu.")
            
    return redirect('category_list')    