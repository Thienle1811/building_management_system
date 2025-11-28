/* static/js/base.js */

document.addEventListener("DOMContentLoaded", function() {
    // Ví dụ: Tự động ẩn thông báo (Alert) sau 5 giây
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});