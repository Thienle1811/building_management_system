from django.shortcuts import render
from .models import LandingConfig, HeroSlide, Benefit, FAQ

def landing_page(request):
    # Lấy cấu hình Landing Page đang active
    config = LandingConfig.objects.filter(is_active=True).first()
    
    # Lấy dữ liệu các khối
    slides = HeroSlide.objects.all()
    benefits = Benefit.objects.all()
    faqs = FAQ.objects.all()

    context = {
        'config': config,
        'slides': slides,
        'benefits': benefits,
        'faqs': faqs,
    }
    return render(request, 'landing/index.html', context)