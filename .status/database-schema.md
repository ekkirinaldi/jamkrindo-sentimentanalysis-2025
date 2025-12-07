# Database Schema Documentation

## Overview

Database menggunakan SQLite dengan SQLAlchemy ORM. Semua tabel mendukung UTF-8 untuk teks Bahasa Indonesia.

## Tables

### 1. `companies`

Tabel utama untuk menyimpan informasi perusahaan.

**Columns:**
- `id` (Integer, Primary Key) - ID unik perusahaan
- `pt_name` (String(255), Unique, Indexed) - Nama perusahaan (contoh: "PT Maju Jaya")
- `perplexity_search_id` (String(255), Nullable) - ID pencarian dari Perplexity (jika ada)
- `created_at` (DateTime) - Waktu pembuatan record
- `updated_at` (DateTime) - Waktu update terakhir

**Relationships:**
- `company_data` - One-to-Many dengan `company_data`
- `sentiment_results` - One-to-Many dengan `sentiment_results`
- `legal_records` - One-to-Many dengan `legal_records`
- `analysis_summaries` - One-to-Many dengan `analysis_summary`

**File:** `backend/app/models/company.py`

---

### 2. `company_data`

Menyimpan data mentah dari Perplexity API.

**Columns:**
- `id` (Integer, Primary Key)
- `company_id` (Integer, Foreign Key → companies.id)
- `source` (String(255), Nullable) - Sumber data
- `raw_text` (Text, Nullable) - Teks mentah dari Perplexity
- `extracted_date` (DateTime) - Waktu ekstraksi data

**File:** `backend/app/models/company.py`

---

### 3. `sentiment_results`

Menyimpan hasil analisis sentimen untuk setiap teks.

**Columns:**
- `id` (Integer, Primary Key)
- `company_id` (Integer, Foreign Key → companies.id)
- `text_analyzed` (Text, Nullable) - Teks yang dianalisis (atau panjang teks)
- `positive_score` (Float, Nullable) - Skor positif VADER
- `negative_score` (Float, Nullable) - Skor negatif VADER
- `neutral_score` (Float, Nullable) - Skor netral VADER
- `compound_score` (Float, Nullable) - Skor compound VADER
- `sentiment_label` (String(50), Nullable) - Label sentimen: **POSITIF**, **NETRAL**, **NEGATIF**
- `analyzed_at` (DateTime) - Waktu analisis

**File:** `backend/app/models/sentiment.py`

---

### 4. `legal_records`

Menyimpan catatan hukum dari Mahkamah Agung.

**Columns:**
- `id` (Integer, Primary Key)
- `company_id` (Integer, Foreign Key → companies.id)
- `case_number` (String(255), Nullable) - Nomor kasus
- `case_date` (String(255), Nullable) - Tanggal putusan (format Indonesia)
- `case_title` (Text, Nullable) - Judul kasus
- `case_type` (String(100), Nullable) - Jenis kasus: **pidana**, **perdata**, **tata usaha negara**, **niaga**, **pajak**
- `verdict_summary` (Text, Nullable) - Ringkasan putusan
- `severity_level` (String(50), Nullable) - Tingkat keparahan: **tinggi**, **sedang**, **rendah**, **tidak ada**
- `source_url` (Text, Nullable) - URL dokumen kasus
- `crawled_at` (DateTime) - Waktu crawling

**File:** `backend/app/models/legal_record.py`

---

### 5. `analysis_summary`

Menyimpan ringkasan analisis akhir dan rekomendasi.

**Columns:**
- `id` (Integer, Primary Key)
- `company_id` (Integer, Foreign Key → companies.id)
- `sentiment_avg_score` (Float, Nullable) - Rata-rata skor sentimen
- `legal_records_count` (Integer, Nullable) - Jumlah kasus hukum ditemukan
- `risk_score` (Float, Nullable) - Skor risiko (0-100)
- `risk_level` (String(50), Nullable) - Tingkat risiko: **HIJAU**, **KUNING**, **MERAH**
- `recommendation` (Text, Nullable) - Rekomendasi dalam Bahasa Indonesia
- `analysis_date` (DateTime) - Tanggal analisis

**File:** `backend/app/models/analysis_summary.py`

## Database Initialization

Database diinisialisasi otomatis saat aplikasi startup melalui `app/database.py`:

```python
def init_db():
    from app.models import company, sentiment, legal_record, analysis_summary
    Base.metadata.create_all(bind=engine)
```

**File:** `backend/app/database.py`

## Connection String

Default: `sqlite:///./data/credit_scoring.db`

Dapat diubah melalui environment variable `DATABASE_URL`.

## Notes

- Semua teks disimpan dalam UTF-8 untuk mendukung karakter Bahasa Indonesia
- Timestamps menggunakan timezone-aware DateTime
- Cascade delete: menghapus perusahaan akan menghapus semua data terkait

