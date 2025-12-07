# API Endpoints Documentation

## Base URL

- Development: `http://localhost:8000`
- Production: (configure via Nginx)

## API Version

All endpoints are under `/api/v1/`

## Endpoints

### Health Check

**GET** `/health`

**Description:** Health check endpoint untuk memastikan service berjalan.

**Response:**
```json
{
  "status": "ok",
  "message": "Layanan berjalan dengan baik"
}
```

**File:** `backend/app/api/v1/health.py`

---

### Company Analysis

**POST** `/api/v1/company/analyze`

**Description:** Endpoint utama untuk menganalisis perusahaan. Mengorchestrasi semua service.

**Request Body:**
```json
{
  "pt_name": "PT Maju Jaya Sentosa",
  "detailed": false
}
```

**Parameters:**
- `pt_name` (string, required): Nama perusahaan
- `detailed` (boolean, optional): Jika true, return detail lengkap catatan hukum

**Response:**
```json
{
  "company_name": "PT Maju Jaya Sentosa",
  "status": "success",
  "analysis": {
    "risk_assessment": {
      "risk_score": 52.5,
      "risk_level": "KUNING",
      "sentiment_component": 57.5,
      "mentions_component": 0.0,
      "legal_component": 0.0,
      "details": {
        "total_texts_analyzed": 1,
        "positive_texts": 0,
        "negative_texts": 0,
        "legal_cases_found": 0,
        "max_case_severity": "tidak ada"
      },
      "recommendation": "⚠️ PERLU DITINJAU: ..."
    },
    "sentiment_analysis": {
      "total_texts": 1,
      "valid_analyses": 1,
      "average_score": 0.42,
      "positive_count": 0,
      "neutral_count": 1,
      "negative_count": 0,
      "details": [...]
    },
    "legal_records": {
      "company_name": "PT Maju Jaya Sentosa",
      "cases_found": 0,
      "max_severity": "tidak ada"
    },
    "news_analysis": {
      "company_name": "PT Maju Jaya Sentosa",
      "total_articles": 10,
      "positive_count": 7,
      "neutral_count": 0,
      "negative_count": 3,
      "articles": [...]
    },
    "perplexity_sources": ["url1", "url2", ...],
    "perplexity_news_sources": ["url1", "url2", ...]
  },
  "timestamp": "2025-12-07T12:00:00"
}
```

**Workflow:**
1. Validasi input
2. Cari data perusahaan dari Perplexity
3. Analisis sentimen
4. Crawl catatan hukum (dengan timeout protection)
5. Analisis berita terbaru
6. Hitung skor risiko
7. Return hasil lengkap

**Duration:** 30-50 detik (typical)

**Error Handling:**
- 400: Input tidak valid
- 500: Error internal dengan detail dalam Bahasa Indonesia

**File:** `backend/app/api/v1/company.py`

---

### News Analysis

**POST** `/api/v1/news/analyze`

**Description:** Mencari dan menganalisis sentimen berita terbaru tentang perusahaan.

**Request Body:**
```json
{
  "company_name": "Bank Mandiri",
  "limit": 10
}
```

**Parameters:**
- `company_name` (string, required): Nama perusahaan
- `limit` (int, optional): Jumlah artikel (1-20, default: 10)

**Response:**
```json
{
  "company_name": "Bank Mandiri",
  "total_articles": 10,
  "positive_count": 7,
  "neutral_count": 0,
  "negative_count": 3,
  "articles": [
    {
      "title": "Judul Artikel",
      "summary": "Ringkasan artikel...",
      "source_url": "https://...",
      "date": "2025-12-07",
      "sentiment_label": "POSITIF",
      "sentiment_score": 0.75,
      "confidence": 0.95
    }
  ],
  "timestamp": "2025-12-07T12:00:00",
  "status": "sukses"
}
```

**Workflow:**
1. Cari berita terbaru menggunakan Perplexity
2. Parse artikel dari response
3. Analisis sentimen untuk setiap artikel
4. Return hasil dengan statistik

**Duration:** 20-40 detik

**File:** `backend/app/api/v1/news.py`

---

## Error Responses

Semua error mengembalikan format:

```json
{
  "detail": "Pesan error dalam Bahasa Indonesia"
}
```

**Status Codes:**
- 200: Success
- 400: Bad Request (input tidak valid)
- 500: Internal Server Error

---

## CORS Configuration

Allowed origins:
- `http://localhost:3000`
- `http://localhost:8000`
- `http://frontend:3000`
- `http://backend:8000`

**File:** `backend/main.py`

---

## API Documentation

Swagger UI tersedia di: `http://localhost:8000/docs`

Redoc tersedia di: `http://localhost:8000/redoc`

