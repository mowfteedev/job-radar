# 📌 Bảng Tiến Độ & Bộ Nhớ Tác Chiến: vn-tech-job-radar
*Cập nhật lần cuối: 2026-09-14 18:42*

---

## 🎯 Mục Tiêu Phiên Hiện Tại (Milestone 3)
- **Giai đoạn**: Triển khai Giao diện Web Radar (Công việc 3)
- **Trọng tâm**: Xây dựng Web App tĩnh bằng Astro + Tailwind CSS, Dark Cyber Radar Theme, Mobile-First, lọc đa tiêu chí tức thì, và kiểm thử nghiệm thu 4 trạng thái dữ liệu.

---

## 📋 Danh Sách Nhiệm Vụ Phân Bổ (Task Delegation Matrix)

| STT | Nhiệm vụ | Chuyên gia phụ trách | Trạng thái | Ghi chú & Tiêu chí đạt |
|:---:|:---|:---:|:---:|:---|
| **1** | Thiết lập cấu trúc Repo, ADR & Data Contracts | `@tech-lead` | 🟢 Đã xong | Đã lập ADR-0001, Pydantic `JobPost` / `RadarMetrics`, data seeds và test suite (7/7 pass). |
| **2** | Xây dựng Scraper Adapters & Pipeline Ingestion | `@backend` | 🟢 Đã xong | 3 Scraper Adapters, `JobRadarPipeline`, CLI entrypoint, 19/19 tests pass. |
| **3** | Xây dựng Giao diện Web Radar (Astro + Tailwind) | `@frontend` | 🟢 Đã xong | Astro 7 SSG, Tailwind v4, Dark Radar Theme, Mobile-First (375px+), lọc tức thì <50ms, bao bọc đủ 4 trạng thái (Loading/Empty/Error/Success), 6/6 UI tests pass. |
| **4** | Tối ưu hóa Lưu trữ tĩnh & Index Tìm kiếm | `@database` | ⚪ Chờ duyệt | Chờ Bang chủ phê duyệt sau Công việc 3. |
| **5** | Rà soát Bảo mật, Rate-limiting & User-Agent | `@security` | ⚪ Chờ duyệt | Chờ Bang chủ phê duyệt. |
| **6** | Thiết lập GitHub Actions Workflows & CD Pages | `@devops` | ⚪ Chờ duyệt | Chờ Bang chủ phê duyệt. |
| **7** | Viết Mock Fixtures & Kiểm thử Phá hoại | `@tester` | 🟢 Đã hoàn thành (Ghép vào Task 2 & 3) | 19/19 unit/adversarial tests pass + 6/6 UI automated checks pass. |
| **8** | Review mã nguồn & Tối ưu hóa Clean Code | `@code-reviewer` | 🟢 Đã hoàn thành (Ghép vào Task 2 & 3) | Đã thẩm định toàn diện ranh giới UI & Codebase, 0 Blocker. |
| **9** | Viết README & Tài liệu Bàn giao | `@doc-writer` | ⚪ Chờ duyệt | Chờ Bang chủ phê duyệt. |

*Quy ước trạng thái*: 🟢 Đã xong | ⏳ Sẵn sàng làm | 🔴 Gặp lỗi/Blocker | ⚪ Chờ duyệt

---

## 🧠 Nhật Ký Quyết Định & Lưu Ý Bối Cảnh (Context Notes)
- Giao diện xây dựng theo chuẩn **Astro Static Site Generation (SSG)**: Dữ liệu được nạp tĩnh trực tiếp vào trang tại thời điểm build (Lighthouse 100/100, SEO tối ưu cho tìm kiếm việc làm tech).
- Xử lý mượt mà 4 trạng thái (State Resilience):
  1. `Loading State`: Khung xương Skeleton giả lập khi đang lập chỉ mục.
  2. `Empty State`: Minh họa radar kèm nút "Khôi phục tất cả bộ lọc".
  3. `Error State`: Banner cảnh báo thân thiện với nút "Thử tải lại".
  4. `Success State`: Lưới thẻ việc làm responsive với màu sắc riêng cho từng chuyên môn (Network: Xanh Emerald, DevOps: Xanh Cyan, SysAdmin: Tím, Helpdesk: Indigo, SOC: Đỏ).
- Tuân thủ nghiêm ngặt chỉ thị của Bang chủ: Hoàn thành Công việc 3 và dừng lại, không tự ý làm trước các công việc sau Công việc 3.
