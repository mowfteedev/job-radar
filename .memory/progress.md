# 📌 Bảng Tiến Độ & Bộ Nhớ Tác Chiến: vn-tech-job-radar
*Cập nhật lần cuối: 2026-09-14 19:18*

---

## 🎯 Mục Tiêu Phiên Hiện Tại (Milestone 4)
- **Giai đoạn**: Tối ưu hóa Lưu trữ Tĩnh & Static Inverted Index (Công việc 4)
- **Trọng tâm**: Xây dựng bộ lập chỉ mục ngược (`JobSearchIndexer`), xuất bản `data/search_index.json`, đo lường độ trễ truy vấn (<5ms), kiểm tra tỉ lệ nén payload (>65%) và đảm bảo tính toàn vẹn dữ liệu.

---

## 📋 Danh Sách Nhiệm Vụ Phân Bổ (Task Delegation Matrix)

| STT | Nhiệm vụ | Chuyên gia phụ trách | Trạng thái | Ghi chú & Tiêu chí đạt |
|:---:|:---|:---:|:---:|:---|
| **1** | Thiết lập cấu trúc Repo, ADR & Data Contracts | `@tech-lead` | 🟢 Đã xong | Đã lập ADR-0001, Pydantic `JobPost` / `RadarMetrics`, data seeds và test suite (7/7 pass). |
| **2** | Xây dựng Scraper Adapters & Pipeline Ingestion | `@backend` | 🟢 Đã xong | 3 Scraper Adapters, `JobRadarPipeline`, CLI entrypoint, 19/19 tests pass. |
| **3** | Xây dựng Giao diện Web Radar (Astro + Tailwind) | `@frontend` | 🟢 Đã xong | Astro 7 SSG, Tailwind v4, Dark Radar Theme, Mobile-First (375px+), lọc tức thì <50ms, bao bọc đủ 4 trạng thái, 6/6 UI tests pass. |
| **4** | Tối ưu hóa Lưu trữ tĩnh & Index Tìm kiếm | `@database` | 🟢 Đã xong | Đã hoàn thành `JobSearchIndexer`, xuất bản `data/search_index.json`, độ trễ tra cứu point lookup <1ms, lọc tổ hợp <2ms, nén gzip giảm 70%, 23/23 tests pass. |
| **5** | Rà soát Bảo mật, Rate-limiting & User-Agent | `@security` | ⚪ Chờ duyệt | Chờ Bang chủ phê duyệt sau Công việc 4. |
| **6** | Thiết lập GitHub Actions Workflows & CD Pages | `@devops` | ⚪ Chờ duyệt | Chờ Bang chủ phê duyệt. |
| **7** | Viết Mock Fixtures & Kiểm thử Phá hoại | `@tester` | 🟢 Đã hoàn thành (Ghép vào Task 2, 3 & 4) | 23/23 tests pass (bao gồm Storage Latency & Compression Benchmarks) + 6/6 UI tests pass. |
| **8** | Review mã nguồn & Tối ưu hóa Clean Code | `@code-reviewer` | 🟢 Đã hoàn thành (Ghép vào Task 2, 3 & 4) | Thẩm định cấu trúc dữ liệu, độ phức tạp $O(1)$ query, 0 Blocker. |
| **9** | Viết README & Tài liệu Bàn giao | `@doc-writer` | ⚪ Chờ duyệt | Chờ Bang chủ phê duyệt. |

*Quy ước trạng thái*: 🟢 Đã xong | ⏳ Sẵn sàng làm | 🔴 Gặp lỗi/Blocker | ⚪ Chờ duyệt

---

## 🧠 Nhật Ký Quyết Định & Lưu Ý Bối Cảnh (Context Notes)
- Triển khai mô hình **Static Inverted Index**: Tự động phân tách và nhóm chỉ mục theo `by_role`, `by_location`, `by_level`, `by_skill` và `by_keyword` (loại bỏ từ nối stop-words).
- Hiệu năng dữ liệu:
  - Tra cứu theo ID (Point lookup): **< 0.1ms** (độ phức tạp $O(1)$).
  - Lọc giao tập (Set intersection cho Role + Location): **< 1.5ms** trên tập 500 bản ghi giả lập (đáp ứng xuất sắc quy chuẩn < 20ms của `@database`).
  - Tỉ lệ nén Gzip/Brotli đạt **70.2%**, giữ payload 300-500 tin luôn ở mức dưới 70KB tải mạng.
- Tuyệt đối tuân thủ chỉ thị của Bang chủ: Hoàn thành Công việc 4 và dừng lại, không tự ý làm trước các công việc sau Công việc 4.
