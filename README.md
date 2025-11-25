# 🏢 PMS Hồng Loan – Hệ Thống Quản Lý Chung Cư

## 1. Giới thiệu

**PMS Hồng Loan** là hệ thống quản lý tòa nhà tập trung chạy trên nền tảng **Django 5 (Python 3.13)**, được thiết kế theo kiến trúc **Modular Monolith** giúp:

- **Quản lý cư dân & căn hộ**: Lưu trữ hồ sơ định danh, phương tiện đi lại, và lịch sử cư trú.
- **Vận hành & Tra cứu**: Tìm kiếm nhanh theo tên, CCCD, số điện thoại; lọc dữ liệu theo tòa nhà trên giao diện Web Admin.
- **Tích hợp đa nền tảng**: Cung cấp API chuẩn RESTful cho Mobile App và giao diện Web (Bootstrap 5) cho Ban Quản Lý.
- **An toàn dữ liệu**: Cơ chế **Soft Delete** (xóa mềm) giúp truy vết dữ liệu và bảo vệ ràng buộc toàn vẹn (không xóa căn hộ khi còn người ở).

---

## 2. Cây thư mục

```text
building_management_system/
├─ manage.py                # Entrypoint Django
├─ README.md                # Tài liệu dự án
├─ requirements.txt         # Danh sách thư viện phụ thuộc
│
├─ config/                  # Cấu hình dự án (Project package)
│  ├─ asgi.py / wsgi.py
│  ├─ urls.py               # Router gốc
│  └─ settings.py           # Cấu hình chung (Modular apps config)
│
├─ apps/                    # Business Modules (Modular Monolith)
│  ├─ buildings/            # Core: Tòa nhà, Căn hộ
│  ├─ residents/            # Main: Cư dân, Phương tiện, Hồ sơ
│  └─ utils.py              # Tiện ích chung (BaseModel, SoftDelete)
│
├─ templates/               # Giao diện Web Admin (Bootstrap 5)
│  ├─ base.html             # Layout chung (Navbar, Footer)
│  └─ residents/            # Màn hình danh sách, form nhập liệu
│
└─ media/                   # Lưu trữ file upload (Ảnh CCCD, Hợp đồng...)
```

### Giải thích nhanh

| Thư mục / file | Vai trò |
|----------------|---------|
| `apps/` | Chứa các module nghiệp vụ độc lập. Ví dụ: `residents` quản lý dân, `buildings` quản lý hạ tầng. |
| `templates/` | Giao diện người dùng cho BQL (Web Admin), sử dụng Django Templates + Bootstrap 5. |
| `utils.py` | Chứa `BaseModel` giúp tự động thêm `created_at`, `updated_at` và logic `soft_delete`. |

---

## 3. Công nghệ & Cấu hình

| Thành phần | Công nghệ sử dụng | Mô tả |
|------------|-------------------|-------|
| **Backend** | Python 3.13, Django 5.x | Xử lý logic nghiệp vụ và ORM. |
| **API** | Django Rest Framework (DRF) | Cung cấp dữ liệu JSON cho Mobile App. |
| **Frontend** | Bootstrap 5, FontAwesome | Giao diện quản trị trên Desktop. |
| **Database** | SQLite (Dev) / PostgreSQL (Prod) | Lưu trữ dữ liệu quan hệ. |
| **Image Process** | Pillow | Xử lý upload ảnh thẻ cư dân. |

---

## 4. Các lệnh khởi tạo & chạy dự án

### 4.1 Cài đặt môi trường (Windows CMD/Terminal)

```bash
# 1. Clone dự án & vào thư mục
git clone https://github.com/wetech-thevan/building_management_system.git
cd building_management_system

# 2. Tạo & kích hoạt môi trường ảo (venv)
python -m venv venv
.\venv\Scripts\activate
# (Nếu dùng Mac/Linux: source venv/bin/activate)

# 3. Cài đặt thư viện
pip install django djangorestframework django-filter Pillow

# 4. Khởi tạo Database & Admin
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

# 5. Chạy Server
python manage.py runserver
```

### Truy cập hệ thống:

- **Web Admin (BQL)**: http://127.0.0.1:8000/residents/
- **Django Admin**: http://127.0.0.1:8000/admin/
- **API Endpoint**: http://127.0.0.1:8000/api/v1/residents/

---

## 5. Tài liệu API (Module Residents)

Hệ thống cung cấp các endpoints chính cho ứng dụng di động:

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| **GET** | `/api/v1/residents/` | Lấy danh sách cư dân (Hỗ trợ params `?q=` để tìm kiếm). |
| **POST** | `/api/v1/residents/` | Tạo mới cư dân kèm danh sách xe. |
| **GET** | `/api/v1/residents/{id}/` | Xem chi tiết thông tin cư dân. |
| **PUT** | `/api/v1/residents/{id}/` | Cập nhật thông tin. |
| **DELETE** | `/api/v1/residents/{id}/` | Xóa mềm (Soft Delete) - Dữ liệu vẫn còn trong DB để truy vết. |

### Mẫu JSON Tạo mới:

```json
{
    "full_name": "Nguyễn Văn A",
    "identity_card": "079099000123",
    "phone_number": "0909123456",
    "current_apartment": 1,
    "relationship_type": "OWNER",
    "vehicles": [
        { "license_plate": "59-X1 123.45", "vehicle_type": "Xe máy" }
    ]
}
```

---

## 6. Lộ trình phát triển (Roadmap)

### ✅ Phase 1 (Completed):
- Thiết kế Database Core (Buildings, Residents).
- Hoàn thiện API CRUD & Soft Delete.
- Xây dựng Web Admin: Danh sách, Tìm kiếm, Thêm/Sửa/Xóa cư dân.
- Viết Unit Test bảo vệ logic nghiệp vụ.

### ⏳ Phase 2 (Next Step):
- Module Sales: Quản lý khách tiềm năng & Quy trình nộp hồ sơ thuê/mua.
- Tích hợp quy trình duyệt hồ sơ tự động chuyển thành Cư dân.

### ⏳ Phase 3:
- Module Billing: Ghi chỉ số Điện/Nước & Tính toán hóa đơn tự động.
- Xuất báo cáo doanh thu & tích hợp thanh toán.

---

## 📝 Thông tin dự án

- **👨‍💻 Phát triển bởi**: Thienle1811 - WETECHX Team
- **📅 Cập nhật lần cuối**: 25/11/2025
- **🔗 Repository**: [GitHub]https://github.com/wetech-thevan/building_management_system.git