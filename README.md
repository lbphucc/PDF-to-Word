# Hệ thống chuyển đổi PDF sang Word Thông minh

## 1. Tổng quan dự án

Trong môi trường học tập và làm việc, nhu cầu chỉnh sửa lại nội dung từ các file PDF (tài liệu tham khảo, báo cáo cũ, giáo trình scan) là rất lớn. Tuy nhiên, các công cụ hiện có thường gặp vấn đề: vỡ font tiếng Việt, mất cấu trúc bảng biểu, hoặc không xử lý được file scan (dạng ảnh).

**Hệ thống** là giải pháp nền tảng web giúp người dùng chuyển đổi tài liệu PDF sang định dạng DOC với mục tiêu:
* **Chính xác:** Ưu tiên giữ nguyên layout, bảng biểu và công thức toán học.
* **Thông minh:** Tích hợp OCR để xử lý tài liệu dạng ảnh/scan.
* **Tiện lợi:** Cho phép xem trước và chỉnh sửa nhanh kết quả ngay trên trình duyệt.

---

## 2. Yêu cầu chức năng

Hệ thống cung cấp các nhóm chức năng chính:

* **Quản lý tệp tin (File Management):**
    * Upload file PDF (Hỗ trợ kéo thả, giới hạn dung lượng 50MB).
    * Kiểm tra định dạng và quét virus cơ bản.
* **Chuyển đổi (Conversion Core):**
    * Mode 1 (Standard): Chuyển đổi PDF văn bản thông thường (giữ format).
    * Mode 2 (OCR): Chuyển đổi PDF dạng scan/ảnh sang văn bản có thể chỉnh sửa.
* **Hậu xử lý (Post-Processing):**
    * Xem trước (Preview) tài liệu sau chuyển đổi dạng *Flow Document*.
    * Trình soạn thảo Online (WYSIWYG Editor) để sửa lỗi chính tả/bố cục nhanh.
* **Xuất dữ liệu:** Tải xuống file `.docx` hoàn chỉnh.

---

## 3. Yêu cầu phi chức năng

Để đảm bảo trải nghiệm người dùng và tính ổn định của hệ thống:

* **Hiệu năng (Performance):**
    * Thời gian chuyển đổi trung bình < 30s cho file văn bản (dưới 10 trang).
    * Hỗ trợ xử lý bất đồng bộ (Background processing) để không gây treo trình duyệt với file lớn.
* **Độ chính xác (Accuracy):**
    * Giữ nguyên > 90% bố cục bảng biểu (Tables).
    * Nhận diện chính xác > 95% ký tự tiếng Việt (với file chất lượng tốt).
* **Bảo mật & Riêng tư (Security & Privacy):**
    * File người dùng upload sẽ tự động bị xóa khỏi server sau 24h.
    * Không chia sẻ dữ liệu người dùng với bên thứ 3.
* **Khả năng mở rộng (Scalability):**
    * Kiến trúc có thể mở rộng thêm nhiều Worker để xử lý song song khi lượng request tăng cao.

---

## 4. Ngôn ngữ và Công cụ

Nhóm sử dụng các công nghệ hiện đại, mã nguồn mở phù hợp với tiêu chuẩn công nghiệp:

| Thành phần | Công nghệ / Công cụ |
| :--- | :--- |
| **Backend** | Python (FastAPI)|
| **Frontend** | HTML |
| **AI/Core** |  |
| **Database** |  |
| **Infrastructure**|  |
| **Quản lý dự án**| Git/Github (Source Control). |

---

## 5. Giải pháp kỹ thuật và Thuật toán chính

Để giải quyết bài toán "giữ nguyên định dạng", nhóm áp dụng các giải pháp sau:

### 5.1. Kiến trúc hệ thống: Asynchronous Queue
Sử dụng mô hình **Producer-Consumer** với **Celery** và **Redis**:
1.  **Web Server** nhận file -> Đẩy task vào hàng đợi (Queue) -> Trả về `TaskID`.
2.  **Worker Server** chạy ngầm -> Lấy task -> Thực hiện convert nặng.
3.  Client sử dụng cơ chế **Polling** (hoặc WebSocket) để kiểm tra trạng thái và nhận link tải khi hoàn tất.

### 5.2. Thuật toán xử lý Layout (Core Logic)
Thay vì convert dòng-sang-dòng, hệ thống phân tích cấu trúc trang (Document Layout Analysis):
1.  **Detect Block:** Xác định vùng nào là Văn bản, vùng nào là Bảng biểu, vùng nào là Hình ảnh.
2.  **Table Extraction:** Sử dụng thuật toán phát hiện đường kẻ (Line detection) để tái tạo lại cấu trúc Cell/Row của bảng trong Word.
3.  **OCR Fallback:** Nếu mật độ văn bản thấp (file ảnh), tự động kích hoạt engine OCR để nhận diện chữ.

---

## 6. Kế hoạch dự kiến

Dự án được thực hiện trong 8 tuần theo mô hình **Agile/Scrum** (2 tuần/sprint):

* **Tuần 1-2 (Analysis & Design):** Phân tích yêu cầu, viết SRS, thiết kế DB & API.
* **Tuần 3-4 (Dev Phase 1):** Xây dựng Core Module PDF Parser & Converter.
* **Tuần 5-6 (Dev Phase 2):** Frontend, OCR Integration.
* **Tuần 7 (Testing):** Unit Test, Fix bugs.
* **Tuần 8 (Release):** Documentation, Deploy Demo.

---
