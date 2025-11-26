from django.shortcuts import render
from .models import LandingConfig, HeroSlide, Benefit, FAQ, ProcessStep

def landing_page(request):
    # 1. Lấy cấu hình Landing Page đang active
    config = LandingConfig.objects.filter(is_active=True).first()
    
    # 2. Lấy dữ liệu các khối nội dung
    slides = HeroSlide.objects.all()
    benefits = Benefit.objects.all()
    faqs = FAQ.objects.all()
    
    # 3. Lấy dữ liệu Quy trình (QUAN TRỌNG: Sắp xếp theo thứ tự nhập)
    process_steps = ProcessStep.objects.all().order_by('order')

    context = {
        'config': config,
        'slides': slides,
        'benefits': benefits,
        'faqs': faqs,
        'process_steps': process_steps, # <-- Gửi biến này sang HTML
    }
    return render(request, 'landing/index.html', context)