# 📌 Bảng Tiến Độ & Bộ Nhớ Tác Chiến: vn-tech-job-radar
*Cập nhật lần cuối: 2026-09-14 21:12*

---

## 🎯 Mục Tiêu Phiên Hiện Tại (Milestone 5)
- **Giai đoạn**: Rà Soát Bảo Mật, Rate-Limiting & User-Agent (Công việc 5)
- **Trọng tâm**: Triển khai cơ chế xoay tua User-Agent (`UserAgentRotator`), bộ giới hạn tần suất lịch sự chống DoS (`AsyncPoliteRateLimiter`), phòng vệ SSRF & XSS URL Sanitizer, và quét sạch khóa bí mật (`SecretScanner`).

---

## 📋 Danh Sách Nhiệm Vụ Phân Bổ (Task Delegation Matrix)

| STT | Nhiệm vụ | Chuyên gia phụ trách | Trạng thái | Ghi chú & Tiêu chí đạt |
|:---:|:---|:---:|:---:|:---|
| **1** | Thiết lập cấu trúc Repo, ADR & Data Contracts | `@tech-lead` | 🟢 Đã xong | Đã lập ADR-0001, Pydantic `JobPost` / `RadarMetrics`, data seeds và test suite (7/7 pass). |
| **2** | Xây dựng Scraper Adapters & Pipeline Ingestion | `@backend` | 🟢 Đã xong | 3 Scraper Adapters, `JobRadarPipeline`, CLI entrypoint, 19/19 tests pass. |
| **3** | Xây dựng Giao diện Web Radar (Astro + Tailwind) | `@frontend` | 🟢 Đã xong | Astro 7 SSG, Tailwind v4, Dark Radar Theme, Mobile-First (375px+), lọc tức thì <50ms, bao bọc đủ 4 trạng thái, 6/6 UI tests pass. |
| **4** | Tối ưu hóa Lưu trữ tĩnh & Index Tìm kiếm | `@database` | 🟢 Đã xong | `JobSearchIndexer`, xuất bản `search_index.json`, point lookup <0.1ms, nén gzip 70%, 23/23 tests pass. |
| **5** | Rà soát Bảo mật, Rate-limiting & User-Agent | `@security` | 🟢 Đã xong | Xoay tua User-Agent đa trình duyệt, Rate limiter với jitter chống DoS, chặn đứng SSRF (IP nội bộ/metadata) và XSS (`javascript:`), Secret Scanner xác nhận 0 rò rỉ, 30/30 tests pass. |
| **6** | Thiết lập GitHub Actions Workflows & CD Pages | `@devops` | ⚪ Chờ duyệt | Chờ Bang chủ phê duyệt sau Công việc 5. |
| **7** | Viết Mock Fixtures & Kiểm thử Phá hoại | `@tester` | 🟢 Đã hoàn thành (Ghép vào Task 2, 3, 4 & 5) | 30/30 tests pass (bao gồm SSRF/XSS rejection, RateLimiter & Secret Scanner) + 6/6 UI tests pass. |
| **8** | Review mã nguồn & Tối ưu hóa Clean Code | `@code-reviewer` | 🟢 Đã hoàn thành (Ghép vào Task 2, 3, 4 & 5) | Thẩm định các ranh giới bảo mật đầu vào/đầu ra, 0 Blocker. |
| **9** | Viết README & Tài liệu Bàn giao | `@doc-writer` | ⚪ Chờ duyệt | Chờ Bang chủ phê duyệt. |

*Quy ước trạng thái*: 🟢 Đã xong | ⏳ Sẵn sàng làm | 🔴 Gặp lỗi/Blocker | ⚪ Chờ duyệt

---

## 🧠 Nhật Ký Quyết Định & Lưu Ý Bối Cảnh (Context Notes)
- Triển khai **AppSec Defense in Depth**:
  - `UserAgentRotator`: Giả lập đầy đủ Client Hints (`Sec-Ch-Ua`, `Sec-Ch-Ua-Mobile`, `Sec-Ch-Ua-Platform`) và gắn kèm tiêu đề trách nhiệm `X-Crawler-Contact`.
  - `AsyncPoliteRateLimiter`: Semaphore 3 kết nối đồng thời kèm jitter trễ 0.3s - 1.0s, chống việc crawler làm nghẽn hạ tầng của các cổng tuyển dụng.
  - `URL & Text Sanitizer`: Bịt hoàn toàn lỗ hổng SSRF (chặn dải IP private `127.0.0.1`, `10.0.0.0/8`, `192.168.0.0/16`, `169.254.169.254`) và lọc sạch scheme độc hại `javascript:`, `data:`.
  - `SecretScanner`: Đảm bảo 100% không có token Telegram, GitHub PAT hay khóa SSH nào bị commit vào kho lưu trữ.
- Tuân thủ nghiêm ngặt chỉ thị của Bang chủ: Hoàn thành Công việc 5 và dừng lại, tuyệt đối không tự ý làm Công việc 6 hay các công việc tiếp theo.
