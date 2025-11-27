import logging
import pandas as pd
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponse
from .models import Building, Apartment
from .forms import ApartmentImportForm

# Tạo logger để ghi nhật ký hệ thống
logger = logging.getLogger(__name__)

def apartment_import(request):
    """
    Import danh sách căn hộ từ Excel (PMS-03-02)
    Có bổ sung Logging (PMS-03-05)
    """
    if request.method == 'POST':
        form = ApartmentImportForm(request.POST, request.FILES)
        if form.is_valid():
            building = form.cleaned_data['building']
            excel_file = request.FILES['excel_file']
            
            try:
                # --- LOGGING BẮT ĐẦU ---
                logger.info(f"PMS-03: User {request.user} bắt đầu import cho tòa {building.code} từ file {excel_file.name}")
                # -----------------------

                # 1. Đọc file Excel
                df = pd.read_excel(excel_file)
                # Chuẩn hóa tên cột về chữ thường, bỏ khoảng trắng thừa
                df.columns = [c.strip().lower() for c in df.columns]
                
                success_count = 0
                update_count = 0
                
                with transaction.atomic():
                    for index, row in df.iterrows():
                        # Lấy dữ liệu chấp nhận cả tiếng Anh và Tiếng Việt
                        floor = row.get('floor') or row.get('tầng')
                        unit = row.get('unit') or row.get('số căn')
                        code = row.get('code') or row.get('mã căn')
                        
                        if not code:
                            continue # Bỏ qua nếu không có mã căn
                            
                        # Các thông tin phụ
                        net_area = row.get('net_area') or row.get('diện tích') or 0
                        gross_area = row.get('gross_area') or 0
                        room_type = row.get('type') or row.get('loại phòng') or '2PN'
                        direction = row.get('direction') or row.get('hướng') or ''
                        price = row.get('price') or row.get('giá') or 0
                        status = row.get('status') or 'VACANT'
                        note = row.get('note') or ''
                        
                        # 3. Tạo hoặc Cập nhật
                        obj, created = Apartment.objects.update_or_create(
                            apartment_code=code,
                            defaults={
                                'building': building,
                                'floor_number': int(floor) if floor else 0,
                                'unit_number': str(unit) if unit else '',
                                'net_area': float(net_area) if net_area else 0,
                                'gross_area': float(gross_area) if gross_area else 0,
                                'room_type': room_type,
                                'direction': direction,
                                'price': price,
                                'status': status,
                                'note': note
                            }
                        )
                        
                        if created:
                            success_count += 1
                        else:
                            update_count += 1
                
                # --- LOGGING KẾT QUẢ ---
                logger.info(f"PMS-03: Import hoàn tất. Thêm mới: {success_count}, Cập nhật: {update_count}")
                # -----------------------

                messages.success(request, f"Đã Import thành công! (Thêm mới: {success_count}, Cập nhật: {update_count})")
                return redirect('apartment_list')
                
            except Exception as e:
                # --- LOGGING LỖI ---
                logger.error(f"PMS-03: Lỗi Import Excel: {str(e)}", exc_info=True)
                # -------------------
                messages.error(request, f"Lỗi khi đọc file: {str(e)}")
    else:
        form = ApartmentImportForm()

    return render(request, 'buildings/apartment_import.html', {
        'form': form,
        'title': 'Import Căn hộ từ Excel'
    })

def download_template(request):
    """
    API: Tải file Excel mẫu. Nếu có building_id, điền sẵn dữ liệu (PMS-03-02).
    """
    building_id = request.GET.get('building')
    columns = ['code', 'floor', 'unit', 'net_area', 'gross_area', 'type', 'price', 'direction', 'status', 'note']
    data = []

    building_code = "All"
    if building_id:
        building = get_object_or_404(Building, pk=building_id)
        building_code = building.code
        apartments = building.apartments.all().order_by('floor_number', 'unit_number')
        
        if apartments.exists():
            for apt in apartments:
                data.append({
                    'code': apt.apartment_code,
                    'floor': apt.floor_number,
                    'unit': apt.unit_number,
                    'net_area': apt.net_area,
                    'gross_area': apt.gross_area,
                    'type': apt.room_type,
                    'price': apt.price,
                    'direction': apt.direction,
                    'status': apt.status,
                    'note': apt.note
                })
        else:
            # Dữ liệu mẫu nếu chưa có căn nào
            data.append({
                'code': f"{building.code}-01.01", 'floor': 1, 'unit': '01', 
                'net_area': 70, 'gross_area': 75, 'type': '2PN', 
                'price': 2500000000, 'direction': 'SE', 'status': 'VACANT', 'note': ''
            })

    # Xuất Excel
    df = pd.DataFrame(data, columns=columns)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="Template_CanHo_{building_code}.xlsx"'
    df.to_excel(response, index=False)
    return response

def apartment_list(request):
    """Xem danh sách căn hộ dạng bảng (Basic List)"""
    apartments = Apartment.objects.select_related('building', 'owner').all().order_by('building', 'floor_number', 'unit_number')
    
    building_id = request.GET.get('building')
    if building_id:
        apartments = apartments.filter(building_id=building_id)
        
    buildings = Building.objects.all()
    
    context = {
        'apartments': apartments,
        'buildings': buildings,
        'selected_building': int(building_id) if building_id else ''
    }
    return render(request, 'buildings/apartment_list.html', context)

def floor_plan(request):
    """Hiển thị sơ đồ tầng dạng lưới (PMS-03-03)"""
    buildings = Building.objects.all()
    
    selected_building_id = request.GET.get('building')
    selected_floor = request.GET.get('floor')
    search_query = request.GET.get('q', '')

    apartments = []
    floors = []
    selected_building = None

    if selected_building_id:
        selected_building = get_object_or_404(Building, pk=selected_building_id)
        # Tạo danh sách tầng từ 1 đến tổng số tầng
        floors = range(1, selected_building.total_floors + 1)
        
        # Mặc định chọn tầng 1 nếu chưa chọn
        if not selected_floor:
            selected_floor = 1
        
        # Lấy căn hộ theo Tòa và Tầng
        apartments = Apartment.objects.filter(
            building=selected_building,
            floor_number=selected_floor
        ).select_related('owner')

        if search_query:
            apartments = apartments.filter(apartment_code__icontains=search_query)
            
        apartments = apartments.order_by('unit_number')

    context = {
        'buildings': buildings,
        'selected_building': selected_building,
        'floors': floors,
        'selected_floor': int(selected_floor) if selected_floor else None,
        'apartments': apartments,
        'search_query': search_query,
        'title': 'Sơ đồ Tòa nhà'
    }
    return render(request, 'buildings/floor_plan.html', context)

def apartment_search(request):
    """Tìm kiếm căn hộ nâng cao (PMS-03-04)"""
    apartments = Apartment.objects.select_related('building', 'owner').all().order_by('building', 'floor_number', 'unit_number')
    
    # Hứng tham số
    building_id = request.GET.get('building')
    status = request.GET.get('status')
    direction = request.GET.get('direction')
    room_type = request.GET.get('room_type')
    min_area = request.GET.get('min_area')
    max_area = request.GET.get('max_area')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    q = request.GET.get('q')

    # Lọc dữ liệu
    if building_id:
        apartments = apartments.filter(building_id=building_id)
    if status:
        apartments = apartments.filter(status=status)
    if direction:
        apartments = apartments.filter(direction=direction)
    if room_type:
        apartments = apartments.filter(room_type=room_type)
        
    # Lọc khoảng diện tích
    if min_area:
        apartments = apartments.filter(net_area__gte=min_area)
    if max_area:
        apartments = apartments.filter(net_area__lte=max_area)
        
    # Lọc khoảng giá (xử lý bỏ dấu phẩy/chấm)
    if min_price:
        clean_min = min_price.replace(',', '').replace('.', '')
        apartments = apartments.filter(price__gte=clean_min)
    if max_price:
        clean_max = max_price.replace(',', '').replace('.', '')
        apartments = apartments.filter(price__lte=clean_max)
        
    # Tìm theo mã
    if q:
        apartments = apartments.filter(apartment_code__icontains=q)

    context = {
        'apartments': apartments,
        'buildings': Building.objects.all(),
        'status_choices': Apartment.STATUS_CHOICES,
        'direction_choices': Apartment.DIRECTION_CHOICES,
        'room_type_choices': Apartment.ROOM_TYPE_CHOICES,
        'request_data': request.GET 
    }
    return render(request, 'buildings/apartment_search.html', context)