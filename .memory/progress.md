# 📌 Bảng Tiến Độ & Bộ Nhớ Tác Chiến: vn-tech-job-radar
*Cập nhật lần cuối: 2026-09-14 18:25*

---

## 🎯 Mục Tiêu Phiên Hiện Tại (Milestone 2)
- **Giai đoạn**: Triển khai Scraper Adapters & Pipeline Ingestion (Công việc 2)
- **Trọng tâm**: Xây dựng bộ cào bất đồng bộ đa nguồn, bộ điều phối pipeline, cơ chế chống sập (fault isolation), và kiểm thử thực chiến đạt chuẩn.

---

## 📋 Danh Sách Nhiệm Vụ Phân Bổ (Task Delegation Matrix)

| STT | Nhiệm vụ | Chuyên gia phụ trách | Trạng thái | Ghi chú & Tiêu chí đạt |
|:---:|:---|:---:|:---:|:---|
| **1** | Thiết lập cấu trúc Repo, ADR & Data Contracts | `@tech-lead` | 🟢 Đã xong | Đã lập ADR-0001, Pydantic `JobPost` / `RadarMetrics`, data seeds và test suite (7/7 pass). |
| **2** | Xây dựng Scraper Adapters & Pipeline Ingestion | `@backend` | 🟢 Đã xong | Đã hoàn thành 3 Scraper Adapters (FPT, Viettel, Community), `JobRadarPipeline`, CLI entrypoint, đạt 19/19 tests pass. Đã được `@code-reviewer` và `@tester` nghiệm thu. |
| **3** | Xây dựng Giao diện Web Radar (Astro + Tailwind) | `@frontend` | ⚪ Chờ duyệt | Chờ Bang chủ phê duyệt sau Công việc 2. |
| **4** | Tối ưu hóa Lưu trữ tĩnh & Index Tìm kiếm | `@database` | ⚪ Chờ duyệt | Chờ Bang chủ phê duyệt. |
| **5** | Rà soát Bảo mật, Rate-limiting & User-Agent | `@security` | ⚪ Chờ duyệt | Chờ Bang chủ phê duyệt. |
| **6** | Thiết lập GitHub Actions Workflows & CD Pages | `@devops` | ⚪ Chờ duyệt | Chờ Bang chủ phê duyệt. |
| **7** | Viết Mock Fixtures & Kiểm thử Phá hoại | `@tester` | 🟢 Đã hoàn thành (Ghép vào Task 2) | Đã hoàn thành 19 test cases bao gồm kiểm thử cô lập lỗi và tấn công biên (Adversarial Tests). |
| **8** | Review mã nguồn & Tối ưu hóa Clean Code | `@code-reviewer` | 🟢 Đã hoàn thành (Ghép vào Task 2) | Đã rà soát 5 trụ cột, 0 Blocker, phê duyệt cho phép hòa nhập mã nguồn. |
| **9** | Viết README & Tài liệu Bàn giao | `@doc-writer` | ⚪ Chờ duyệt | Chờ Bang chủ phê duyệt. |

*Quy ước trạng thái*: 🟢 Đã xong | ⏳ Sẵn sàng làm | 🔴 Gặp lỗi/Blocker | ⚪ Chờ duyệt

---

## 🧠 Nhật Ký Quyết Định & Lưu Ý Bối Cảnh (Context Notes)
- Đã triển khai cơ chế Graceful Degradation trong `JobRadarPipeline`: Lỗi từ 1 sàn tuyển dụng (WAF 403, 404, hoặc mạng timeout) không làm gián đoạn các nguồn khác; tự động kích hoạt verified domain fallback.
- Ghi dữ liệu nguyên tử (Atomic Write): File `jobs.json` và `metrics.json` được ghi qua file tạm `.tmp` trước khi `replace` để chống hỏng file khi runner bị hủy ngang.
- Tuyệt đối tuân thủ chỉ thị của Bang chủ: Chỉ dừng lại ở Công việc 2, không tự ý làm trước các công việc sau Công việc 2.
