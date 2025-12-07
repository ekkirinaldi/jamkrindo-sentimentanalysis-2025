# Backend Services Documentation

## Overview

Backend menggunakan FastAPI dengan struktur modular. Semua service mendukung Bahasa Indonesia.

## Core Services

### 1. PerplexityService

**File:** `backend/app/services/perplexity_service.py`

**Purpose:** Integrasi dengan Perplexity AI API untuk pencarian informasi perusahaan dan berita.

**Methods:**

#### `async search_company(company_name: str) -> Dict[str, Any]`
Mencari informasi perusahaan menggunakan Perplexity API.

**Parameters:**
- `company_name` (str): Nama perusahaan (contoh: "PT Maju Jaya")

**Returns:**
```python
{
    "raw_response": {...},      # Raw response dari Perplexity
    "extracted_text": str,       # Teks yang diekstrak
    "sources": [urls],           # Daftar URL sumber
    "query": str,                # Query yang digunakan
    "timestamp": str             # ISO timestamp
}
```

**Features:**
- Query dioptimalkan untuk perusahaan Indonesia
- Ekstraksi semua sumber (citations, search_results, URLs dari content)
- Error handling dengan pesan Bahasa Indonesia

---

#### `async search_latest_news(company_name: str, limit: int = 10) -> Dict[str, Any]`
Mencari 10 berita terbaru tentang perusahaan.

**Parameters:**
- `company_name` (str): Nama perusahaan
- `limit` (int): Jumlah maksimal artikel (default: 10)

**Returns:**
```python
{
    "company_name": str,
    "news_articles": [
        {
            "title": str,        # Judul artikel (markdown stripped)
            "summary": str,      # Ringkasan artikel
            "source_url": str,   # URL sumber
            "date": str          # Tanggal (jika tersedia)
        }
    ],
    "total_found": int,
    "timestamp": str,
    "sources": [urls]           # Semua sumber Perplexity
}
```

**Features:**
- Parsing otomatis dari response Perplexity
- Stripping markdown dari judul
- Ekstraksi URL dari berbagai format
- Fallback strategies jika parsing gagal

---

#### `extract_sentiment_text(raw_text: str) -> str`
Membersihkan teks untuk analisis sentimen.

**Features:**
- Menghapus URL
- Normalisasi whitespace
- Preserve karakter Bahasa Indonesia

---

#### `_strip_markdown(text: str) -> str`
Menghapus formatting markdown dari teks.

**Removes:**
- `**bold**` dan `__bold__`
- `*italic*` dan `_italic_`
- `[links](url)`
- `# headers`
- Code blocks

---

#### `_parse_news_articles(content: str, sources: list, limit: int) -> list`
Parse artikel berita dari response Perplexity.

**Strategies:**
1. Split by numbered/bullet lists
2. Split by paragraphs dengan matching sources
3. Create from sources jika parsing gagal

**Features:**
- Deteksi duplikasi judul-ringkasan
- Similarity check untuk menghindari duplikasi
- Markdown stripping

---

### 2. SentimentAnalysisService

**File:** `backend/app/services/sentiment_service.py`

**Purpose:** Analisis sentimen menggunakan VADER dan Transformers.

**Initialization:**
- VADER: Loaded immediately
- Transformers: Lazy loaded (first use)

**Models:**
- Primary: `nlptown/bert-base-multilingual-uncased-sentiment`
- Fallback: `cardiffnlp/twitter-xlm-roberta-base-sentiment`

**Methods:**

#### `analyze_text(text: str) -> Dict`
Menganalisis sentimen satu teks.

**Returns:**
```python
{
    "vader_scores": {
        "compound": float,      # -1.0 to 1.0
        "positive": float,
        "negative": float,
        "neutral": float
    },
    "transformer_scores": {
        "label": str,           # Model label
        "score": float,          # 0.0-1.0
        "confidence": float
    },
    "consensus_score": float,   # 0.0-1.0 (average)
    "sentiment_label": str,      # POSITIF, NETRAL, NEGATIF
    "confidence": float,
    "text_length": int
}
```

**Features:**
- Kombinasi VADER + Transformers
- Normalisasi skor ke 0-1
- Label dalam Bahasa Indonesia
- Error handling untuk teks terlalu pendek

---

#### `analyze_batch(texts: List[str]) -> Dict`
Menganalisis multiple teks dan return statistik.

**Returns:**
```python
{
    "total_texts": int,
    "valid_analyses": int,
    "average_score": float,
    "std_dev": float,
    "min_score": float,
    "max_score": float,
    "positive_count": int,
    "neutral_count": int,
    "negative_count": int,
    "details": [Dict]           # Detail untuk setiap teks
}
```

---

### 3. MahkamahAgungCrawler

**File:** `backend/app/services/mahkamah_crawler.py`

**Purpose:** Web scraping database hukum Mahkamah Agung.

**Base URL:** `https://putusan3.mahkamahagung.go.id`

**Methods:**

#### `async search_company(company_name: str) -> Dict[str, Any]`
Mencari kasus hukum untuk perusahaan.

**Returns:**
```python
{
    "company_name": str,
    "cases_found": int,
    "cases": [
        {
            "case_number": str,
            "case_date": str,           # Format Indonesia
            "case_title": str,
            "case_type": str,           # pidana, perdata, niaga, etc.
            "verdict_summary": str,
            "severity": str,            # tinggi, sedang, rendah
            "source_url": str
        }
    ],
    "max_severity": str,                # tinggi, sedang, rendah, tidak ada
    "timestamp": str,
    "source": "mahkamah_agung"
}
```

**Features:**
- Menggunakan Crawl4AI untuk JavaScript rendering
- Fallback ke requests jika Crawl4AI tidak tersedia
- Timeout protection (15 detik)
- Error handling dengan graceful degradation

**Case Type Mapping:**
- `pidana` → severity: `tinggi`
- `niaga` → severity: `tinggi`
- `perdata` → severity: `sedang`
- `tata usaha negara` → severity: `sedang`
- `pajak` → severity: `sedang`

---

### 4. RiskScoringService

**File:** `backend/app/services/risk_scoring.py`

**Purpose:** Menghitung skor risiko kredit berdasarkan sentimen dan catatan hukum.

**Weights:**
- Sentiment: 30%
- Mentions: 30%
- Legal: 40%

**Methods:**

#### `calculate_risk_score(sentiment_data: Dict, legal_data: Dict) -> Dict`
Menghitung skor risiko keseluruhan.

**Returns:**
```python
{
    "risk_score": float,                # 0-100
    "risk_level": str,                  # HIJAU, KUNING, MERAH
    "sentiment_component": float,       # 0-100
    "mentions_component": float,        # 0-100
    "legal_component": float,           # 0-100
    "details": {
        "total_texts_analyzed": int,
        "positive_texts": int,
        "negative_texts": int,
        "legal_cases_found": int,
        "max_case_severity": str
    },
    "recommendation": str               # Bahasa Indonesia
}
```

**Risk Level Thresholds:**
- `HIJAU`: risk_score ≤ 30
- `KUNING`: 30 < risk_score ≤ 65
- `MERAH`: risk_score > 65

**Recommendations:**
- HIJAU: "✅ DISARANKAN: Catatan positif. Aman untuk persetujuan kredit."
- KUNING: "⚠️ PERLU DITINJAU: ..." (dengan detail)
- MERAH: "❌ TIDAK DISARANKAN: ..." (dengan detail)

---

## Utility Services

### Logger

**File:** `backend/app/utils/logger.py`

Standard Python logging dengan konfigurasi dari `LOG_LEVEL` environment variable.

---

### Exceptions

**File:** `backend/app/utils/exceptions.py`

Custom exceptions dengan pesan Bahasa Indonesia:
- `PerplexityAPIError`
- `SentimentAnalysisError`
- `CrawlerError`
- `RiskScoringError`
- `DatabaseError`

---

## Configuration

**File:** `backend/app/config.py`

Environment variables:
- `PERPLEXITY_API_KEY` - API key untuk Perplexity
- `DATABASE_URL` - Connection string database
- `LOG_LEVEL` - Level logging (INFO, DEBUG, etc.)
- `TORCH_DEVICE` - Device untuk PyTorch (cpu/cuda)
- `MAHKAMAH_CRAWL_DELAY_SECONDS` - Delay untuk crawling

