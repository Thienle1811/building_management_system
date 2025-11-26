from django.shortcuts import render, redirect
from django.contrib import messages
from .models import LandingConfig, HeroSlide, Benefit, FAQ, ProcessStep, CustomerLead, NewsItem

def landing_page(request):
    # --- XỬ LÝ FORM ĐĂNG KÝ (POST) ---
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        demand = request.POST.get('demand')
        
        if not full_name or not phone:
            messages.error(request, "Vui lòng nhập Họ tên và Số điện thoại!")
        else:
            try:
                CustomerLead.objects.create(
                    full_name=full_name,
                    phone=phone,
                    email=email,
                    demand=demand
                )
                messages.success(request, "Đăng ký thành công! Chúng tôi sẽ liên hệ sớm.")
                return redirect('/#lien-he')
            except Exception as e:
                messages.error(request, f"Đã xảy ra lỗi: {str(e)}")

    # --- LẤY DỮ LIỆU HIỂN THỊ (GET) ---
    config = LandingConfig.objects.filter(is_active=True).first()
    slides = HeroSlide.objects.all()
    benefits = Benefit.objects.all()
    faqs = FAQ.objects.all()
    process_steps = ProcessStep.objects.all().order_by('order')
    
    # Lấy 3 tin tức mới nhất (MỚI)
    news_list = NewsItem.objects.all()[:3]

    context = {
        'config': config,
        'slides': slides,
        'benefits': benefits,
        'faqs': faqs,
        'process_steps': process_steps,
        'news_list': news_list, # Truyền biến này sang HTML
    }
    return render(request, 'landing/index.html', context)