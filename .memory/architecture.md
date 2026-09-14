# 🏛️ Kiến Trúc Hệ Thống: vn-tech-job-radar (Automated Tech Recruitment & Internship Radar)

> *Tài liệu này là nguồn chân lý kỹ thuật (Single Source of Truth) do `@tech-lead` quản lý cho dự án `vn-tech-job-radar`. Mọi thay đổi kiến trúc lớn phải được thảo luận và cập nhật tại đây.*

---

## 1. Tổng Quan & Mục Tiêu Kỹ Thuật
- **Mục tiêu sản phẩm**: Cổng thông tin tự động thu thập, sàng lọc, phân loại và chuẩn hóa tin tuyển dụng Thực tập sinh / Fresher cho 4 mảng kỹ thuật cốt lõi: **Network Engineering, IT Helpdesk, SysAdmin (Linux/Windows) và Cloud/DevOps** tại Việt Nam.
- **Kiến trúc chủ đạo**: **Jamstack Serverless 0 đồng** — Kết hợp giữa Python Ingestion Pipeline chạy trên GitHub Actions định kỳ và Frontend tĩnh (Astro + Tailwind CSS) triển khai trên GitHub Pages.
- **Môi trường hoạt động**: Python 3.11+ / Node.js 20+ / GitHub Actions Runner / GitHub Pages CDN.

---

## 2. Công Nghệ Sử Dụng (Tech Stack)

| Tầng (Layer) | Công nghệ lựa chọn | Lý do & Ràng buộc |
| :--- | :--- | :--- |
| **Data Ingestion Engine** | Python 3, `httpx`, `BeautifulSoup4`, `lxml` | Xử lý mạng bất đồng bộ, tốc độ phân tích HTML cao, hỗ trợ giả lập header browser. |
| **Data Contracts & Validation** | `pydantic v2` | Đảm bảo tính toàn vẹn dữ liệu, tự động sinh JSON Schema, chặn đứng dữ liệu bẩn. |
| **State & Storage** | Git flat-file (`data/jobs.json`, `data/metrics.json`) | 0 đồng chi phí database, truy xuất qua CDN toàn cầu, lưu trữ lịch sử qua Git commit. |
| **Frontend Presentation** | Astro + Tailwind CSS + MiniSearch/Fuse.js | Hiệu năng Lighthouse 100/100, Island Architecture, tìm kiếm client-side < 50ms không reload. |
| **Automation & CI/CD** | GitHub Actions Workflows | Chạy cronjob 2 lần/ngày (06:00, 18:00 UTC+7), tự động build và deploy GitHub Pages. |
| **Quality & Security** | `pytest`, `ruff`, SHA256 Canonical Hashing | Kiểm thử tự động, loại bỏ trùng lặp đa nền tảng, an toàn không lộ token/secret. |

---

## 3. Ranh Giới Nghiệp Vụ & Cấu Trúc Module

```
vn-tech-job-radar/
├── .github/workflows/          # DevOps: Cronjob Ingestion & Deployment workflows
│   └── pipeline.yml
├── .memory/                    # Project Memory & ADRs (do @tech-lead quản lý)
│   ├── adr/
│   │   └── 0001-khoi-tao-du-an.md
│   ├── architecture.md
│   └── progress.md
├── schemas/                    # Data Contracts (Pydantic v2 Models)
│   ├── __init__.py
│   └── job.py                  # JobPost, RadarMetrics, CompanyInfo, SalaryInfo
├── src/                        # Ingestion Pipeline Core Engine
│   ├── scrapers/               # Scraper Adapters (BaseScraper, TopCV, FPT, Viettel...)
│   │   ├── __init__.py
│   │   └── base.py
│   └── processors/             # Data Cleaners, Classifiers & Deduplicators
│       ├── __init__.py
│       ├── classifier.py       # Rule-based taxonomy & seniority scoring
│       └── dedupe.py           # Canonical hash & TTL state manager
├── data/                       # Git Database (Public Static Storage)
│   ├── jobs.json               # Active job postings
│   ├── metrics.json            # Skill radar metrics & frequencies
│   └── schema_jobs.json        # JSON Schema for external integrations
├── tests/                      # Test suites (Unit & Integration tests)
│   ├── test_schemas.py
│   └── test_processors.py
├── pyproject.toml              # Python project configuration
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
```

---

## 4. Quy Chuẩn Kỹ Thuật Bắt Buộc (Guild Standards)

1. **Data Contract First**: Mọi dữ liệu thu thập từ bất kỳ nguồn nào đều phải thông qua `JobPost` Pydantic model trước khi được phép ghi vào `data/jobs.json`.
2. **Idempotency & Deduplication**: Sử dụng `canonical_hash = SHA256(company:title:location)[:16]`. Cùng một bài tuyển dụng đăng lại trên nhiều kênh chỉ tồn tại 1 bản ghi duy nhất, tự động cập nhật thời gian `scraped_at`.
3. **Graceful Degradation (Chống sập dây chuyền)**: Mỗi Scraper Adapter hoạt động độc lập. Nếu 1 sàn tuyển dụng đổi giao diện hoặc chặn bot, chỉ adapter đó ghi log cảnh báo; pipeline vẫn tiếp tục xử lý các nguồn còn lại mà không làm dừng workflow.
4. **Git Hygiene & Zero Commit Spam**: Runner chỉ thực hiện `git commit` khi `git diff --quiet data/jobs.json` phát hiện có tin mới hoặc có tin hết hạn bị thu hồi.
5. **Radar TTL Pruning**: Tin tuyển dụng có tuổi thọ tối đa 30 ngày (`ttl_days = 30`). Sau 30 ngày, trạng thái tự động chuyển thành `EXPIRED` để giữ kích thước file JSON luôn dưới ngưỡng 500KB.
