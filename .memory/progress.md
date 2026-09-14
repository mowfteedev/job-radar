# 📌 Bảng Tiến Độ & Bộ Nhớ Tác Chiến: vn-tech-job-radar
*Cập nhật lần cuối: 2026-09-14 18:05*

---

## 🎯 Mục Tiêu Phiên Hiện Tại (Milestone 1)
- **Giai đoạn**: Khởi tạo Kiến Trúc, ADR & Data Contracts (Công việc 1)
- **Trọng tâm**: Thiết lập nền móng chuẩn mực cho toàn bộ hệ thống pipeline và kho dữ liệu tĩnh.

---

## 📋 Danh Sách Nhiệm Vụ Phân Bổ (Task Delegation Matrix)

| STT | Nhiệm vụ | Chuyên gia phụ trách | Trạng thái | Ghi chú & Tiêu chí đạt |
|:---:|:---|:---:|:---:|:---|
| **1** | Thiết lập cấu trúc Repo, ADR & Data Contracts | `@tech-lead` | 🟢 Đã xong | Đã lập ADR-0001, Pydantic `JobPost` / `RadarMetrics`, data seeds và test suite (7/7 pass). |
| **2** | Xây dựng Scraper Adapters & Pipeline Ingestion | `@backend` | ⏳ Sẵn sàng làm | Triển khai `BaseScraper` cho các nguồn mục tiêu, crawl async httpx. |
| **3** | Xây dựng Giao diện Web Radar (Astro + Tailwind) | `@frontend` | ⚪ Chờ duyệt | Mobile-First, lọc tức thì theo City/Role/Skill, dark mode radar. |
| **4** | Tối ưu hóa Lưu trữ tĩnh & Index Tìm kiếm | `@database` | ⚪ Chờ duyệt | Giám sát kích thước `jobs.json`, benchmark tốc độ tìm kiếm. |
| **5** | Rà soát Bảo mật, Rate-limiting & User-Agent | `@security` | ⚪ Chờ duyệt | Chống DoS, xoay tua User-Agent, bảo mật secrets. |
| **6** | Thiết lập GitHub Actions Workflows & CD Pages | `@devops` | ⚪ Chờ duyệt | Cấu hình cronjob 2 lần/ngày, commit bot, deploy Pages. |
| **7** | Viết Mock Fixtures & Kiểm thử Phá hoại | `@tester` | ⚪ Chờ duyệt | Mở rộng test suites, mock response khi sàn tuyển dụng đổi HTML. |
| **8** | Review mã nguồn & Tối ưu hóa Clean Code | `@code-reviewer` | ⚪ Chờ duyệt | Kiểm tra quy chuẩn PEP8, type hints, triệt tiêu code rác. |
| **9** | Viết README & Tài liệu Bàn giao | `@doc-writer` | ⚪ Chờ duyệt | Viết hướng dẫn đóng góp nguồn tuyển dụng mới. |

*Quy ước trạng thái*: 🟢 Đã xong | ⏳ Sẵn sàng làm | 🔴 Gặp lỗi/Blocker | ⚪ Chờ duyệt

---

## 🧠 Nhật Ký Quyết Định & Lưu Ý Bối Cảnh (Context Notes)
- Đã xuất bản JSON Schema tại `data/schema_jobs.json` để Frontend hoặc bên thứ 3 có thể tự động validate dữ liệu.
- Đã triển khai bộ test ban đầu tại `tests/` đạt 100% tỷ lệ pass (7/7 tests).
- Giữ vững nguyên tắc chi phí 0 VNĐ và Serverless Architecture.
