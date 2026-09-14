# 📌 Bảng Tiến Độ & Bộ Nhớ Tác Chiến: vn-tech-job-radar
*Cập nhật lần cuối: 2026-09-14 21:16*

---

## 🎯 Mục Tiêu Phiên Hiện Tại (Milestone 6)
- **Giai đoạn**: Tự Động Hóa Hạ Tầng & CI/CD Pages (Công việc 6)
- **Trọng tâm**: Thiết lập đường ống CI chất lượng tự động (`ci.yml`), cronjob định kỳ 2 lần/ngày (`pipeline.yml`), cơ chế bot tự động commit dữ liệu sạch (`[skip ci]`), và triển khai liên tục không gián đoạn lên GitHub Pages với chi phí 0 đồng.

---

## 📋 Danh Sách Nhiệm Vụ Phân Bổ (Task Delegation Matrix)

| STT | Nhiệm vụ | Chuyên gia phụ trách | Trạng thái | Ghi chú & Tiêu chí đạt |
|:---:|:---|:---:|:---:|:---|
| **1** | Thiết lập cấu trúc Repo, ADR & Data Contracts | `@tech-lead` | 🟢 Đã xong | Đã lập ADR-0001, Pydantic `JobPost` / `RadarMetrics`, data seeds và test suite (7/7 pass). |
| **2** | Xây dựng Scraper Adapters & Pipeline Ingestion | `@backend` | 🟢 Đã xong | 3 Scraper Adapters, `JobRadarPipeline`, CLI entrypoint, 19/19 tests pass. |
| **3** | Xây dựng Giao diện Web Radar (Astro + Tailwind) | `@frontend` | 🟢 Đã xong | Astro 7 SSG, Tailwind v4, Dark Radar Theme, Mobile-First (375px+), lọc tức thì <50ms, bao bọc đủ 4 trạng thái, 6/6 UI tests pass. |
| **4** | Tối ưu hóa Lưu trữ tĩnh & Index Tìm kiếm | `@database` | 🟢 Đã xong | `JobSearchIndexer`, xuất bản `search_index.json`, point lookup <0.1ms, nén gzip 70%, 23/23 tests pass. |
| **5** | Rà soát Bảo mật, Rate-limiting & User-Agent | `@security` | 🟢 Đã xong | Xoay tua User-Agent đa trình duyệt, Rate limiter với jitter chống DoS, chặn đứng SSRF/XSS, Secret Scanner xác nhận 0 rò rỉ, 30/30 tests pass. |
| **6** | Thiết lập GitHub Actions Workflows & CD Pages | `@devops` | 🟢 Đã xong | Đã thiết lập `ci.yml` (Quality Gate PR/Push) và `pipeline.yml` (Cronjob 06:00 & 18:00 UTC+7, Git diff bot commit `[skip ci]`, GitHub Pages deploy v4), cấu hình dynamic base path, 32/32 tests pass. |
| **7** | Viết Mock Fixtures & Kiểm thử Phá hoại | `@tester` | 🟢 Đã hoàn thành (Ghép vào Task 2, 3, 4, 5 & 6) | 32/32 tests pass (bao gồm CI/CD Workflow structure tests) + 6/6 UI tests pass. |
| **8** | Review mã nguồn & Tối ưu hóa Clean Code | `@code-reviewer` | 🟢 Đã hoàn thành (Ghép vào Task 2, 3, 4, 5 & 6) | Thẩm định các ranh giới CI/CD, phân quyền token đặc quyền tối thiểu, 0 Blocker. |
| **9** | Viết README & Tài liệu Bàn giao | `@doc-writer` | ⚪ Chờ duyệt | Chờ Bang chủ phê duyệt sau Công việc 6. |

*Quy ước trạng thái*: 🟢 Đã xong | ⏳ Sẵn sàng làm | 🔴 Gặp lỗi/Blocker | ⚪ Chờ duyệt

---

## 🧠 Nhật Ký Quyết Định & Lưu Ý Bối Cảnh (Context Notes)
- Triển khai **CI/CD Automation & GitOps**:
  - `ci.yml`: Kích hoạt mỗi khi có PR hoặc push nhánh `main`. Kiểm tra toàn diện Python Pytest (32 tests), Secret Scanner audit, và kiểm tra build tĩnh Astro Web.
  - `pipeline.yml`: Lịch cron `0 23,11 * * *` (tương ứng 06:00 và 18:00 UTC+7). Runner tự cào dữ liệu, kiểm tra diff bằng `git status --porcelain`. Nếu có thay đổi mới commit bằng bot `github-actions[bot]` kèm nhãn `[skip ci]` để tránh vòng lặp vô tận.
  - `GitHub Pages Deployment`: Sử dụng các action chính chủ (`actions/configure-pages@v5`, `actions/upload-pages-artifact@v3`, `actions/deploy-pages@v4`) với quyền hạn tối thiểu (`pages: write`, `id-token: write`).
  - `Astro Dynamic Base`: `base: process.env.GITHUB_ACTIONS ? '/job-radar' : '/'` đảm bảo tài nguyên hoạt động trơn tru cả khi chạy local và khi deploy lên `https://mowfteedev.github.io/job-radar/`.
- Tuân thủ nghiêm ngặt chỉ thị của Bang chủ: Hoàn thành Công việc 6 và dừng lại, chờ chỉ thị tiếp theo.
