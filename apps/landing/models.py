from django.db import models
from apps.utils import BaseModel

class LandingConfig(BaseModel):
    """Cấu hình chung cho Landing Page (Logo, Màu sắc, SEO)"""
    project_name = models.CharField(max_length=255, verbose_name="Tên dự án NOXH")
    logo = models.ImageField(upload_to='landing/logos/', verbose_name="Logo dự án")
    
    # Cấu hình màu sắc (Theme)
    primary_color = models.CharField(max_length=7, default="#1da1f2", verbose_name="Màu chủ đạo (HEX)")
    secondary_color = models.CharField(max_length=7, default="#f70", verbose_name="Màu phụ (HEX)")
    
    # Thông tin liên hệ Footer
    hotline = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.TextField(verbose_name="Địa chỉ văn phòng")
    
    is_active = models.BooleanField(default=True, verbose_name="Đang sử dụng")

    def __str__(self):
        return self.project_name

    class Meta:
        verbose_name = "Cấu hình Landing Page"
        verbose_name_plural = "Cấu hình Landing Page"

class HeroSlide(BaseModel):
    """Banner chạy slide ở đầu trang"""
    landing = models.ForeignKey(LandingConfig, on_delete=models.CASCADE, related_name='hero_slides')
    image = models.ImageField(upload_to='landing/hero/', verbose_name="Ảnh Banner (Desktop)")
    image_mobile = models.ImageField(upload_to='landing/hero/', verbose_name="Ảnh Banner (Mobile)", null=True, blank=True)
    title = models.CharField(max_length=255, blank=True, verbose_name="Tiêu đề lớn")
    description = models.TextField(blank=True, verbose_name="Mô tả ngắn")
    cta_text = models.CharField(max_length=50, default="Đăng ký ngay", verbose_name="Chữ trên nút")
    cta_link = models.CharField(max_length=255, default="#register", verbose_name="Link khi bấm nút")
    order = models.IntegerField(default=0, verbose_name="Thứ tự hiển thị")

    class Meta:
        ordering = ['order']
        verbose_name = "Banner Slide"

class Benefit(BaseModel):
    """Section: Lợi ích / Vì sao chọn dự án"""
    landing = models.ForeignKey(LandingConfig, on_delete=models.CASCADE, related_name='benefits')
    icon_class = models.CharField(max_length=50, help_text="VD: fas fa-home (FontAwesome)", verbose_name="Class Icon")
    title = models.CharField(max_length=100, verbose_name="Tiêu đề lợi ích")
    description = models.TextField(verbose_name="Mô tả chi tiết")
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = "Lợi ích dự án"

class FAQ(BaseModel):
    """Section: Câu hỏi thường gặp"""
    landing = models.ForeignKey(LandingConfig, on_delete=models.CASCADE, related_name='faqs')
    question = models.CharField(max_length=255, verbose_name="Câu hỏi")
    answer = models.TextField(verbose_name="Câu trả lời")
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = "Hỏi đáp (FAQ)"