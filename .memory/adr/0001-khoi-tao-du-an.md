# ADR-0001: Lựa Chọn Kiến Trúc Serverless 0 Đồng & Data Contract Cho VN Tech Job Radar
- **Ngày quyết định**: 2026-09-14
- **Người đề xuất**: `@tech-lead`
- **Trạng thái**: Đã phê duyệt (Approved)

---

## 1. Bối Cảnh & Thách Thức (Context)
Dự án **vn-tech-job-radar** cần giải quyết bài toán thu thập, chuẩn hóa và hiển thị tin tuyển dụng Thực tập sinh / Fresher các ngành Network, IT Helpdesk, SysAdmin và DevOps tại Việt Nam.

Hệ thống đối mặt với các thách thức:
1. **Ràng buộc chi phí**: Chi phí vận hành máy chủ = 0 VNĐ. Không phụ thuộc vào VPS có phí duy trì hàng tháng.
2. **Khả năng duy trì lâu dài**: Phải hoạt động tự động không cần người can thiệp thủ công (Zero Ops).
3. **Độ tin cậy dữ liệu**: Tránh rác dữ liệu, tin hết hạn và tin trùng lặp khi cào từ nhiều nguồn khác nhau.
4. **Tránh bị chặn bởi Anti-bot**: Dải IP của GitHub Actions runner thường xuyên bị WAF/Cloudflare gắn cờ chặn.

---

## 2. Quyết Định Kiến Trúc (Decision)

Chúng tôi quyết định áp dụng mô hình **Jamstack Serverless Data Pipeline**:

1. **Automation Engine**: Sử dụng GitHub Actions làm orchestration scheduler định kỳ (chạy 2 lần/ngày: 06:00 và 18:00 UTC+7).
2. **Data Pipeline**: Xây dựng bằng **Python 3** với mô hình Adapter Pattern (`BaseScraper`). Khai thác internal API endpoints, RSS và các cổng tuyển dụng trực tiếp của các tập đoàn viễn thông (FPT, Viettel, VNPT) kết hợp giả lập header trình duyệt.
3. **Data Contracts**: Sử dụng **Pydantic v2** (`schemas/job.py`) làm hợp đồng dữ liệu chuẩn hóa bắt buộc. Tự động xuất `data/schema_jobs.json`.
4. **Deduplication**: Áp dụng thuật toán băm chuẩn hóa `CanonicalHash = SHA256(normalized_company + normalized_title + location)[:16]`.
5. **Persistence**: Lưu trữ file tĩnh có cấu trúc trong Git (`data/jobs.json`, `data/metrics.json`). Chỉ tạo commit khi có dữ liệu mới.
6. **Frontend Presentation**: Sử dụng **Astro + Tailwind CSS** triển khai qua **GitHub Pages**, tích hợp tìm kiếm client-side bằng MiniSearch/Fuse.js.

---

## 3. Các Phương Án Đã Bị Loại Bỏ (Alternatives Considered)

- **Phương án 1: Fullstack Web App (FastAPI + PostgreSQL + React trên VPS/Railway/Render)**:
  - *Lý do loại bỏ*: Tốn chi phí máy chủ hàng tháng ($5 - $15/tháng), cơ sở dữ liệu miễn phí thường bị sleep sau 15 phút không hoạt động (gây trễ cold-start 30-50s), rủi ro sập hệ thống khi hết hạn thẻ ngân hàng.
- **Phương án 2: Vanilla JS thuần không qua build step**:
  - *Lý do loại bỏ*: Khó hỗ trợ OpenGraph preview khi chia sẻ link mạng xã hội, không tối ưu được SEO cho từng việc làm, không hỗ trợ sinh RSS feed tĩnh, giá trị portfolio kỹ thuật ở mức thấp.

---

## 4. Đánh Đổi & Hệ Quả (Trade-offs & Consequences)

- **Điểm lợi (Ưu điểm)**:
  - Chi phí 0 VNĐ trọn đời.
  - Tốc độ tải trang siêu tốc qua mạng lưới CDN toàn cầu của GitHub Pages.
  - Tính nhất quán dữ liệu cao nhờ Pydantic Schema.
  - Lịch sử dữ liệu được lưu vết đầy đủ trong Git tree (Git as a Database).
- **Điểm thiệt (Nhược điểm & Ràng buộc)**:
  - Cronjob GitHub Actions có thể bị trễ từ 15-30 phút trong giờ cao điểm của GitHub (chấp nhận được vì tin tuyển dụng không đòi hỏi độ trễ theo giây).
  - Không phù hợp với dữ liệu hàng triệu dòng (được kiểm soát bởi cơ chế TTL 30 ngày, giữ tập active jobs luôn dưới 500 tin tuyển dụng chất lượng cao).
