from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import Contract
from .forms import ContractForm

# 1. Danh sách Hợp đồng (Read)
def contract_list(request):
    contracts = Contract.objects.all().select_related('apartment', 'resident').order_by('-created_at')
    
    # Tìm kiếm (Search)
    search_query = request.GET.get('q', '')
    if search_query:
        contracts = contracts.filter(
            Q(code__icontains=search_query) |
            Q(resident__full_name__icontains=search_query) |
            Q(apartment__apartment_code__icontains=search_query)
        )

    # Lọc theo trạng thái (Filter)
    status_filter = request.GET.get('status', '')
    if status_filter:
        contracts = contracts.filter(status=status_filter)

    context = {
        'contracts': contracts,
        'search_query': search_query,
        'status_filter': status_filter
    }
    return render(request, 'contracts/contract_list.html', context)

# 2. Tạo mới Hợp đồng (Create)
def contract_create(request):
    if request.method == 'POST':
        form = ContractForm(request.POST, request.FILES)
        if form.is_valid():
            contract = form.save()
            messages.success(request, f"Đã tạo hợp đồng {contract.code} thành công!")
            return redirect('contract_list')
        else:
            messages.error(request, "Vui lòng kiểm tra lại thông tin nhập liệu.")
    else:
        form = ContractForm()
    
    context = {
        'form': form,
        'title': 'Tạo Hợp đồng Mới'
    }
    return render(request, 'contracts/contract_form.html', context)

# 3. Cập nhật Hợp đồng (Update)
def contract_update(request, pk):
    contract = get_object_or_404(Contract, pk=pk)
    
    if request.method == 'POST':
        form = ContractForm(request.POST, request.FILES, instance=contract)
        if form.is_valid():
            form.save()
            messages.success(request, "Cập nhật hợp đồng thành công!")
            return redirect('contract_list')
    else:
        form = ContractForm(instance=contract)
        
    context = {
        'form': form,
        'title': f'Cập nhật Hợp đồng {contract.code}'
    }
    return render(request, 'contracts/contract_form.html', context)

# 4. Xóa Hợp đồng (Delete)
def contract_delete(request, pk):
    contract = get_object_or_404(Contract, pk=pk)
    
    if request.method == 'POST':
        # Nếu model có hỗ trợ soft_delete thì dùng, không thì delete thường
        if hasattr(contract, 'soft_delete'):
            contract.soft_delete()
            messages.success(request, "Đã xóa hợp đồng (Soft Delete).")
        else:
            contract.delete()
            messages.success(request, "Đã xóa vĩnh viễn hợp đồng.")
        return redirect('contract_list')
        
    return render(request, 'contracts/contract_confirm_delete.html', {'contract': contract})

def contract_detail(request, pk):
    """Xem chi tiết hợp đồng (Read-only)"""
    contract = get_object_or_404(Contract, pk=pk)
    context = {
        'contract': contract
    }
    return render(request, 'contracts/contract_detail.html', context)