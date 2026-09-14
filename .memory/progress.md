# 📌 Bảng Tiến Độ & Bộ Nhớ Tác Chiến: vn-tech-job-radar
*Cập nhật lần cuối: 2026-09-14 21:16*

---

## 🎯 Mục Tiêu Phiên Hiện Tại (Milestone 7 & 8)
- **Giai đoạn**: Kiểm Thử Phá Hoại Cực Hạn (Task 7) & Review Mã Nguồn / Clean Code Tối Cao (Task 8)
- **Trọng tâm**: 
  - `@tester`: Triển khai mock fixtures độc hại, kiểm thử phá hoại Fuzzing 50k ký tự, Unicode/RTL, Chaos Pipeline khi 75% scraper sập mạng, Idempotency Stress Test 10 chu kỳ, và Client-side regex/XSS resilience (43/43 python tests pass, 11/11 UI tests pass).
  - `@code-reviewer`: Xây dựng cây phân cấp biệt lệ chuẩn `src/exceptions.py`, bất biến hóa state qua `model_copy`, chuẩn hóa regex word boundary cho địa điểm tránh false positives, và thiết lập AST Static Code Reviewer Audit chặn đứng silent error swallow / boolean traps (5/5 pass).

---

## 📋 Danh Sách Nhiệm Vụ Phân Bổ (Task Delegation Matrix)

| STT | Nhiệm vụ | Chuyên gia phụ trách | Trạng thái | Ghi chú & Tiêu chí đạt |
|:---:|:---|:---:|:---:|:---|
| **1** | Thiết lập cấu trúc Repo, ADR & Data Contracts | `@tech-lead` | 🟢 Đã xong | Đã lập ADR-0001, Pydantic `JobPost` / `RadarMetrics`, data seeds và test suite (7/7 pass). |
| **2** | Xây dựng Scraper Adapters & Pipeline Ingestion | `@backend` | 🟢 Đã xong | 3 Scraper Adapters, `JobRadarPipeline`, CLI entrypoint, 19/19 tests pass. |
| **3** | Xây dựng Giao diện Web Radar (Astro + Tailwind) | `@frontend` | 🟢 Đã xong | Astro 7 SSG, Tailwind v4, Dark Radar Theme, Mobile-First (375px+), lọc tức thì <50ms, bao bọc đủ 4 trạng thái, 6/6 UI tests pass. |
| **4** | Tối ưu hóa Lưu trữ tĩnh & Index Tìm kiếm | `@database` | 🟢 Đã xong | `JobSearchIndexer`, xuất bản `search_index.json`, point lookup <0.1ms, nén gzip 70%, 23/23 tests pass. |
| **5** | Rà soát Bảo mật, Rate-limiting & User-Agent | `@security` | 🟢 Đã xong | Xoay tua User-Agent đa trình duyệt, Rate limiter với jitter chống DoS, chặn đứng SSRF/XSS, Secret Scanner xác nhận 0 rò rỉ, 30/30 tests pass. |
| **6** | Thiết lập GitHub Actions Workflows & CD Pages | `@devops` | 🟢 Đã xong | Đã thiết lập `ci.yml` và `pipeline.yml` (Cronjob 06:00 & 18:00 UTC+7, Git diff bot commit `[skip ci]`, Pages deploy v4), dynamic base path, 32/32 tests pass. |
| **7** | Viết Mock Fixtures & Kiểm thử Phá hoại | `@tester` | 🟢 Đã xong | Đã lập `mock_responses.py`, `test_adversarial_deep.py`, `test-adversarial-ui.mjs`, kiểm thử chaos network, salary bounds, fuzzing, 43/43 tests pass. |
| **8** | Review mã nguồn & Tối ưu hóa Clean Code | `@code-reviewer` | 🟢 Đã xong | Đã tạo `src/exceptions.py`, audit AST tự động không nuốt lỗi/không boolean trap, bất biến `model_copy`, loại bỏ duplicate stop words, 0 Blocker. |
| **9** | Viết README & Tài liệu Bàn giao | `@doc-writer` | ⚪ Chờ duyệt | Chờ Bang chủ phê duyệt sau khi nghiệm thu Công việc 7 & 8. |

*Quy ước trạng thái*: 🟢 Đã xong | ⏳ Sẵn sàng làm | 🔴 Gặp lỗi/Blocker | ⚪ Chờ duyệt

---

## 🧠 Nhật Ký Quyết Định & Lưu Ý Bối Cảnh (Context Notes)
- Triển khai **Adversarial Hardening & Clean Code Audit (Task 7 & 8)**:
  - **Chặn đứng False Positives Địa Điểm**: Thay thế kiểm tra substring bằng regex word boundary `\b(hà nội|ha noi|hn)\b` để ngăn chặn các từ như "john" hay "dnase" bị gán nhầm địa điểm.
  - **Bảo Vệ Ranh Giới Lương**: Bổ sung `model_validator` trong `SalaryInfo` bắt buộc `min_amount >= 0`, `max_amount >= 0` và `min_amount <= max_amount`.
  - **Mở Rộng Blacklist Chức Danh Cao Cấp**: Thêm các từ khóa như `director`, `vice president`, `vp`, `head of`, `giám đốc` để lọc sạch các vị trí quản lý cấp cao khỏi radar Fresher.
  - **AST Automated Code Review**: Kiểm tra tự động bằng cây cú pháp trừu tượng đảm bảo không có bare except, không có silent pass, không có boolean traps, và 100% hàm có type annotation.
- Tuân thủ nghiêm ngặt chỉ thị của Bang chủ: Hoàn thành Công việc 7 & 8 và dừng lại, chờ chỉ thị tiếp theo.
