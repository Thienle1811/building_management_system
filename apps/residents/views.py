from django.shortcuts import render, redirect
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q 
from django.forms import formset_factory  # <--- ĐÂY LÀ DÒNG BẠN THIẾU
from .models import Resident
from .serializers import ResidentSerializer
from .forms import ResidentForm, VehicleForm
from apps.buildings.models import Building
from django.shortcuts import get_object_or_404

# --- PHẦN 1: API (Dành cho Mobile App) ---
class ResidentViewSet(viewsets.ModelViewSet):
    """
    API CRUD Cư dân:
    - GET /api/v1/residents/: Lấy danh sách
    - POST /api/v1/residents/: Tạo mới
    - GET /api/v1/residents/{id}/: Xem chi tiết
    - DELETE /api/v1/residents/{id}/: Xóa mềm
    """
    queryset = Resident.objects.all().select_related('current_apartment')
    serializer_class = ResidentSerializer
    
    # Cấu hình bộ lọc và tìm kiếm
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['current_apartment', 'relationship_type']
    search_fields = ['full_name', 'identity_card', 'phone_number']

    def destroy(self, request, *args, **kwargs):
        """Ghi đè hàm xóa để thực hiện Soft Delete"""
        instance = self.get_object()
        instance.soft_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# --- PHẦN 2: WEB VIEW (Giao diện Admin Desktop) ---
def resident_list(request):
    """
    Hàm này xử lý giao diện Web: hiển thị danh sách, tìm kiếm, lọc
    """
    search_query = request.GET.get('q', '')
    building_id = request.GET.get('building', '')

    residents = Resident.objects.all().select_related('current_apartment').order_by('-created_at')

    if search_query:
        residents = residents.filter(
            Q(full_name__icontains=search_query) | 
            Q(phone_number__icontains=search_query) | 
            Q(identity_card__icontains=search_query)
        )
    
    if building_id:
        residents = residents.filter(current_apartment__building_id=building_id)

    buildings = Building.objects.all()

    context = {
        'residents': residents,
        'buildings': buildings,
        'search_query': search_query,
        'selected_building': int(building_id) if building_id else '' 
    }
    
    return render(request, 'residents/resident_list.html', context)

def resident_create(request):
    """
    Hàm xử lý tạo mới cư dân:
    1. GET: Hiển thị form trống
    2. POST: Nhận dữ liệu -> Validate -> Lưu vào DB
    """
    # Tạo Formset cho xe (Mặc định cho nhập 1 xe)
    VehicleFormSet = formset_factory(VehicleForm, extra=1)

    if request.method == 'POST':
        form = ResidentForm(request.POST, request.FILES)
        vehicle_formset = VehicleFormSet(request.POST, prefix='vehicles')
        
        if form.is_valid() and vehicle_formset.is_valid():
            # 1. Lưu cư dân trước
            resident = form.save()
            
            # 2. Lưu danh sách xe (gắn vào cư dân vừa tạo)
            for v_form in vehicle_formset:
                if v_form.cleaned_data: # Chỉ lưu dòng có dữ liệu
                    vehicle = v_form.save(commit=False)
                    vehicle.resident = resident
                    vehicle.save()
            
            # 3. Lưu xong thì quay về trang danh sách
            return redirect('resident_list_web')
    else:
        form = ResidentForm()
        vehicle_formset = VehicleFormSet(prefix='vehicles')

    context = {
        'form': form,
        'vehicle_formset': vehicle_formset
    }
    return render(request, 'residents/resident_form.html', context)

def resident_update(request, pk):
    """
    Hàm xử lý Sửa thông tin cư dân:
    1. Lấy thông tin cư dân theo ID (pk)
    2. Hiển thị form với dữ liệu cũ
    3. Lưu lại khi bấm Save
    """
    resident = get_object_or_404(Resident, pk=pk)
    VehicleFormSet = formset_factory(VehicleForm, extra=0) # extra=0 để không hiện thêm dòng trống thừa

    if request.method == 'POST':
        form = ResidentForm(request.POST, request.FILES, instance=resident)
        vehicle_formset = VehicleFormSet(request.POST, prefix='vehicles')
        
        # Logic update xe hơi phức tạp một chút (tạm thời ta chỉ update thông tin cư dân trước)
        # Để đơn giản cho bài học hôm nay, ta sẽ chỉ cho phép sửa thông tin Cư dân.
        if form.is_valid():
            form.save()
            return redirect('resident_list_web')
    else:
        form = ResidentForm(instance=resident)
        # Load dữ liệu xe hiện có (chưa xử lý formset xe ở bước này để tránh lỗi phức tạp)
        vehicle_formset = VehicleFormSet(prefix='vehicles') 

    context = {
        'form': form,
        'vehicle_formset': vehicle_formset,
        'title': 'Cập nhật thông tin' # Đổi tiêu đề form
    }
    return render(request, 'residents/resident_form.html', context)

def resident_delete(request, pk):
    """
    Hàm xử lý Xóa cư dân:
    1. GET: Hỏi xác nhận "Bạn có chắc không?"
    2. POST: Thực hiện xóa mềm
    """
    resident = get_object_or_404(Resident, pk=pk)
    
    if request.method == 'POST':
        resident.soft_delete() # Gọi hàm xóa mềm
        return redirect('resident_list_web')
    
    return render(request, 'residents/resident_confirm_delete.html', {'resident': resident})