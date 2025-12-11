from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.models import User # <--- Import thêm User để tạo tài khoản

# Import cho API
from rest_framework import viewsets, permissions, filters, status, views
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import ResidentSerializer, VehicleSerializer, ChangePasswordSerializer

# Import cho Web
from .models import Resident, Vehicle
from .forms import ResidentForm, VehicleForm

# ==================== 1. API (MOBILE APP) ====================

class ChangePasswordView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Mật khẩu cũ không đúng."]}, status=status.HTTP_400_BAD_REQUEST)
            
            user.set_password(serializer.data.get("new_password"))
            user.save()
            return Response({"detail": "Đổi mật khẩu thành công."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResidentViewSet(viewsets.ModelViewSet):
    """API quản lý cư dân"""
    queryset = Resident.objects.select_related('current_apartment').all().order_by('-created_at')
    serializer_class = ResidentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['full_name', 'phone_number', 'identity_card', 'current_apartment__apartment_code']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return super().get_queryset()
        if hasattr(user, 'resident'):
            return Resident.objects.filter(pk=user.resident.pk)
        return Resident.objects.none()

    @action(detail=False, methods=['get'])
    def me(self, request):
        """API lấy thông tin profile ĐẦY ĐỦ (Cá nhân + Xe + Thành viên)"""
        if hasattr(request.user, 'resident'):
            resident = request.user.resident
            
            # 1. Thông tin cá nhân
            profile_data = ResidentSerializer(resident).data
            
            # 2. Danh sách xe
            vehicles = Vehicle.objects.filter(resident=resident)
            profile_data['vehicles'] = VehicleSerializer(vehicles, many=True).data
            
            # 3. Thành viên cùng căn hộ (trừ bản thân mình ra)
            members = Resident.objects.filter(
                current_apartment=resident.current_apartment
            ).exclude(pk=resident.pk)
            profile_data['members'] = ResidentSerializer(members, many=True).data
            
            return Response(profile_data)
        
        return Response({"detail": "User chưa liên kết hồ sơ cư dân"}, status=404)

# ==================== 2. WEB VIEW (QUẢN LÝ CƯ DÂN) ====================

@login_required
def resident_list_view(request):
    residents = Resident.objects.select_related('current_apartment').all().order_by('-created_at')
    query = request.GET.get('q', '')
    if query:
        residents = residents.filter(
            Q(full_name__icontains=query) | 
            Q(phone_number__icontains=query) |
            Q(current_apartment__apartment_code__icontains=query)
        )
    return render(request, 'residents/resident_list.html', {'residents': residents, 'query': query})

@login_required
def resident_create_view(request):
    """Thêm cư dân mới & TỰ ĐỘNG TẠO TÀI KHOẢN"""
    if request.method == 'POST':
        form = ResidentForm(request.POST, request.FILES)
        if form.is_valid():
            # 1. Lấy đối tượng nhưng chưa lưu vào DB
            resident = form.save(commit=False)
            phone = form.cleaned_data.get('phone_number')

            # 2. Logic tự tạo/lấy User theo Số điện thoại
            if phone:
                # Tìm user có username = số điện thoại
                user, created = User.objects.get_or_create(username=phone)
                if created:
                    # Nếu mới tạo -> Set mật khẩu mặc định
                    user.set_password('123456')
                    user.save()
                    messages.info(request, f"Đã tạo tài khoản mới: {phone} / 123456")
                else:
                    messages.info(request, f"Đã liên kết với tài khoản cũ: {phone}")
                
                # Gán user vào cư dân
                resident.user = user

            # 3. Lưu chính thức
            resident.save()
            messages.success(request, "Thêm cư dân thành công!")
            return redirect('residents:resident_list')
    else:
        form = ResidentForm()
    return render(request, 'residents/resident_form.html', {'form': form, 'title': 'Thêm Cư dân'})

@login_required
def resident_update_view(request, pk):
    resident = get_object_or_404(Resident, pk=pk)
    if request.method == 'POST':
        form = ResidentForm(request.POST, request.FILES, instance=resident)
        if form.is_valid():
            form.save()
            messages.success(request, "Cập nhật thành công!")
            return redirect('residents:resident_list')
    else:
        form = ResidentForm(instance=resident)
    return render(request, 'residents/resident_form.html', {'form': form, 'title': 'Sửa Cư dân'})

@login_required
def resident_delete_view(request, pk):
    resident = get_object_or_404(Resident, pk=pk)
    if request.method == 'POST':
        resident.delete()
        messages.success(request, "Đã xóa cư dân.")
        return redirect('residents:resident_list')
    return render(request, 'residents/resident_confirm_delete.html', {'resident': resident})

# ==================== 3. WEB VIEW (QUẢN LÝ XE) ====================

@login_required
def vehicle_list_view(request):
    query = request.GET.get('q', '')
    vehicles = Vehicle.objects.select_related('resident', 'resident__current_apartment').all().order_by('resident__current_apartment__apartment_code')
    if query:
        vehicles = vehicles.filter(
            Q(license_plate__icontains=query) |
            Q(resident__full_name__icontains=query) |
            Q(resident__current_apartment__apartment_code__icontains=query)
        )
    return render(request, 'residents/vehicle_list.html', {'vehicles': vehicles, 'query': query})

@login_required
def vehicle_create_view(request):
    if request.method == 'POST':
        form = VehicleForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Thêm xe thành công!")
            return redirect('residents:vehicle_list')
    else:
        form = VehicleForm()
    return render(request, 'residents/vehicle_form.html', {'form': form, 'title': 'Đăng ký Xe'})

@login_required
def vehicle_update_view(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    if request.method == 'POST':
        form = VehicleForm(request.POST, request.FILES, instance=vehicle)
        if form.is_valid():
            form.save()
            messages.success(request, "Cập nhật xe thành công!")
            return redirect('residents:vehicle_list')
    else:
        form = VehicleForm(instance=vehicle)
    return render(request, 'residents/vehicle_form.html', {'form': form, 'title': 'Cập nhật Xe'})

@login_required
def vehicle_delete_view(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    if request.method == 'POST':
        vehicle.delete()
        messages.success(request, "Đã xóa xe.")
        return redirect('residents:vehicle_list')
    return render(request, 'residents/vehicle_confirm_delete.html', {'vehicle': vehicle})