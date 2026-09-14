# 📡 job-radar

> **Automated GitHub Actions pipeline tracking Network, DevOps, SysAdmin, and IT Support roles in Vietnam.**  
> Kiến trúc Serverless 0 đồng — Tự động thu thập dữ liệu định kỳ qua GitHub Actions, chuẩn hóa dữ liệu, loại bỏ tin trùng lặp và phát hành giao diện tĩnh lên GitHub Pages.

---

## 🧭 Điều Hướng Nhanh (Navigation)

- 🌐 **Trải Nghiệm Trực Tiếp (Live Demo)**: [https://mowfteedev.github.io/job-radar/](https://mowfteedev.github.io/job-radar/)
- 📦 **Kho Mã Nguồn (GitHub Repository)**: [https://github.com/mowfteedev/job-radar](https://github.com/mowfteedev/job-radar)
- 📊 **Cơ Sở Dữ Liệu Tĩnh (Open JSON Data)**:
  - [data/jobs.json](data/jobs.json) — Danh sách tin tuyển dụng đang kích hoạt
  - [data/metrics.json](data/metrics.json) — Thống kê xu hướng kỹ năng và vị trí
  - [data/search_index.json](data/search_index.json) — Inverted Search Index phục vụ tìm kiếm tức thì

---

## 🎯 Giới Thiệu Codebase & Tính Năng

**job-radar** là nền tảng tự động hóa tìm kiếm và sàng lọc cơ hội việc làm dành cho Thực tập sinh / Fresher các ngành kỹ thuật hạ tầng tại Việt Nam:

1. **Thu thập dữ liệu đa nguồn (Scraper Adapters)**:
   - Tự động cào tin từ các cổng tuyển dụng công nghệ lớn (FPT Telecom, Viettel Careers, VN Tech Community).
   - Tích hợp User-Agent rotation, rate limiter kèm jitter ngẫu nhiên chống quá tải và bộ lọc mã độc chống SSRF / XSS.
2. **Sàng lọc & Chuẩn hóa (Rule Engine & Deduplication)**:
   - Chuẩn hóa dữ liệu theo Data Contract nghiêm ngặt với Pydantic v2.
   - Cơ chế lọc trùng đa nền tảng bằng hàm băm định danh canonical hash `SHA256(company:title:location)[:16]`.
   - Vòng đời TTL (Time-To-Live) tự động 30 ngày: các tin quá hạn tự động chuyển trạng thái `EXPIRED` để giữ kho dữ liệu luôn tinh gọn.
3. **Giao diện Web Radar (Astro + Tailwind CSS)**:
   - Thiết kế Dark Cyber Radar hiện đại, chuẩn Mobile-First (hỗ trợ màn hình từ 320px+).
   - Bộ lọc đa chiều (Khu vực chuyên môn, Địa điểm, Cấp độ) kết hợp tìm kiếm tức thì < 50ms nhờ Static Inverted Index.
   - Bao bọc đủ 4 trạng thái giao diện: *Loading*, *Empty*, *Error*, và *Success*.
4. **Vận hành tự động 0 đồng (GitOps & Pages CD)**:
   - GitHub Actions chạy định kỳ 2 lần/ngày (06:00 và 18:00 UTC+7).
   - Tự động kiểm tra diff, commit dữ liệu sạch bằng bot và deploy trực tiếp lên GitHub Pages.

---

## 🗂️ Cấu Trúc Mã Nguồn

```
job-radar/
├── .github/workflows/          # Kịch bản CI/CD GitHub Actions
│   ├── ci.yml                  # Quality Gate kiểm tra build & secret audit
│   └── pipeline.yml            # Pipeline thu thập dữ liệu định kỳ & CD Pages
├── data/                       # Cơ sở dữ liệu tĩnh (Git Flat-File Database)
│   ├── jobs.json               # Tin tuyển dụng đang kích hoạt
│   ├── metrics.json            # Thống kê phân bố kỹ năng và vị trí
│   ├── schema_jobs.json        # JSON Schema chuẩn hóa cho bên thứ ba
│   └── search_index.json       # Inverted index phục vụ tìm kiếm tĩnh
├── schemas/                    # Pydantic v2 Data Contracts
│   ├── __init__.py
│   └── job.py                  # Khai báo JobPost, CompanyInfo, SalaryInfo
├── src/                        # Ingestion Core Engine
│   ├── exceptions.py           # Phân cấp biệt lệ chuẩn
│   ├── main.py                 # CLI Runner chạy pipeline
│   ├── pipeline.py             # Điều phối cào, deduplicate và lưu trữ
│   ├── processors/             # Phân loại chuyên môn, băm hash & lập chỉ mục
│   ├── scrapers/               # Scraper Adapters cho từng nguồn tuyển dụng
│   └── security/               # User-Agent rotation, rate limiter, sanitizer
├── web/                        # Giao diện Web tĩnh (Astro v7 + Tailwind v4)
│   ├── src/                    # Components, Layouts và Pages
│   └── astro.config.mjs        # Cấu hình dynamic base path cho GitHub Pages
├── package.json                # Quản lý monorepo scripts cho phần web
├── pyproject.toml              # Cấu hình dự án Python
└── requirements.txt            # Thư viện phụ thuộc Python
```

---

## 🚀 Hướng Dẫn Sử Dụng Cơ Bản (HDSD)

### 1. Chạy Pipeline Thu Thập Dữ Liệu (Python)

**Yêu cầu**: Python 3.10 trở lên.

```bash
# 1. Khởi tạo và kích hoạt môi trường ảo
python3 -m venv .venv
source .venv/bin/activate

# 2. Cài đặt các thư viện phụ thuộc
pip install -r requirements.txt

# 3. Chạy pipeline thu thập và cập nhật dữ liệu
python -m src.main --data-dir data --ttl 30
```

Các tùy chọn dòng lệnh:
- `--data-dir`: Đường dẫn thư mục chứa dữ liệu JSON (mặc định: `data`).
- `--ttl`: Số ngày tối đa giữ tin tuyển dụng trước khi hết hạn (mặc định: `30`).
- `-v`, `--verbose`: Bật log chi tiết phục vụ gỡ lỗi.

---

### 2. Chạy Giao Diện Web Radar (Node.js)

**Yêu cầu**: Node.js 20 trở lên.

```bash
# 1. Cài đặt dependencies cho phần web
npm --prefix web install

# 2. Khởi chạy máy chủ phát triển (Local Dev Server)
npm run web:dev

# 3. Đóng gói giao diện tĩnh phục vụ xuất bản (Production Build)
npm run web:build
```

---

## 📄 Bản Quyền
Dự án được phát hành theo giấy phép [MIT](LICENSE).
