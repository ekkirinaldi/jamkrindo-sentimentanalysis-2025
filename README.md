# Sistem Analisis Sentimen untuk Penilaian Kredit

Sistem on-premise untuk menganalisis sentimen dan menilai risiko kredit perusahaan menggunakan analisis sentimen, data hukum, dan berita terbaru.

## 📋 Deskripsi

Sistem ini mengintegrasikan berbagai sumber data untuk memberikan penilaian risiko kredit yang komprehensif:

- **Analisis Sentimen**: Menggunakan VADER dan Transformers untuk menganalisis sentimen teks dalam Bahasa Indonesia
- **Data Hukum**: Web scraping database Mahkamah Agung untuk mencari catatan hukum perusahaan
- **Analisis Berita**: Mencari dan menganalisis 10 berita terbaru tentang perusahaan
- **Risk Scoring**: Menghitung skor risiko berdasarkan sentimen, mentions, dan catatan hukum

## ✨ Fitur Utama

- ✅ **Pencarian Informasi Perusahaan** - Integrasi dengan Perplexity AI untuk mencari informasi lengkap
- ✅ **Analisis Sentimen Multi-Model** - Kombinasi VADER dan Transformers untuk akurasi maksimal
- ✅ **Web Scraping Hukum** - Crawling database Mahkamah Agung menggunakan Crawl4AI
- ✅ **Analisis Berita Terbaru** - Pencarian dan analisis sentimen berita terkini
- ✅ **Risk Scoring** - Perhitungan skor risiko dengan formula terstruktur
- ✅ **UI Lengkap** - Interface modern dengan Next.js dan Tailwind CSS
- ✅ **Database Persistence** - Penyimpanan hasil analisis ke SQLite
- ✅ **Docker Support** - Deployment mudah dengan Docker Compose
- ✅ **Bahasa Indonesia** - Full support untuk Bahasa Indonesia di semua komponen

## 🛠️ Teknologi

### Backend
- **Python 3.11+** dengan FastAPI
- **SQLAlchemy** untuk ORM
- **NLTK VADER** untuk analisis sentimen dasar
- **Hugging Face Transformers** untuk analisis sentimen advanced
- **Crawl4AI** untuk web scraping dengan JavaScript rendering
- **SQLite** untuk database on-premise

### Frontend
- **Next.js 15** dengan React 19
- **TypeScript** untuk type safety
- **Tailwind CSS** untuk styling
- **Recharts** untuk visualisasi data
- **Axios** untuk API calls

### Infrastructure
- **Docker** dan **Docker Compose** untuk containerization
- **Nginx** sebagai reverse proxy

## 📦 Prerequisites

- **Docker** dan **Docker Compose** (untuk deployment dengan Docker)
- **Python 3.11+** (untuk development manual)
- **Node.js 18+** dan **npm** (untuk development manual)
- **Perplexity API Key** - Daftar di [Perplexity AI](https://www.perplexity.ai/)

## 🚀 Quick Start

### Menggunakan Docker Compose (Recommended)

1. **Clone repository**
```bash
git clone https://github.com/ekkirinaldi/jamkrindo-sentimentanalysis-2025.git
cd jamkrindo-sentimentanalysis-2025
```

2. **Setup environment variables**
```bash
# Buat file .env di root directory
cat > .env << EOF
PERPLEXITY_API_KEY=your_perplexity_api_key_here
EOF
```

3. **Start services**
```bash
docker compose up -d
```

4. **Akses aplikasi**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Development Manual (Tanpa Docker)

#### Backend Setup

1. **Setup virtual environment**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# atau
venv\Scripts\activate  # Windows
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Setup environment variables**
```bash
# Buat file backend/.env
cat > backend/.env << EOF
PERPLEXITY_API_KEY=your_perplexity_api_key_here
DATABASE_URL=sqlite:///./data/credit_scoring.db
LOG_LEVEL=INFO
EOF
```

4. **Initialize database**
```bash
python -c "from app.database import init_db; init_db()"
```

5. **Run backend**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### Frontend Setup

1. **Install dependencies**
```bash
cd frontend
npm install
```

2. **Setup environment variables**
```bash
# Buat file frontend/.env.local
cat > frontend/.env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF
```

3. **Run frontend**
```bash
npm run dev
```

4. **Akses aplikasi**
- Frontend: http://localhost:3000

## 📖 Penggunaan

### 1. Analisis Perusahaan

1. Buka http://localhost:3000
2. Masukkan nama perusahaan (contoh: "PT Maju Jaya Sentosa" atau "Bank Mandiri")
3. Klik "Analisis Perusahaan"
4. Tunggu proses analisis (15-50 detik)
5. Lihat hasil:
   - **Skor Risiko** dengan badge warna (HIJAU/KUNING/MERAH)
   - **Ringkasan Bukti** - Overview semua data yang dikumpulkan
   - **Berita Terbaru** - 10 artikel dengan analisis sentimen
   - **Catatan Hukum** - Kasus hukum yang ditemukan
   - **Chart** - Visualisasi distribusi sentimen dan komponen risiko
   - **Sumber Referensi** - Semua URL sumber yang digunakan

### 2. Analisis Berita Standalone

Gunakan endpoint `/api/v1/news/analyze` untuk menganalisis berita terbaru:

```bash
curl -X POST "http://localhost:8000/api/v1/news/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Bank Mandiri",
    "limit": 10
  }'
```

## 📚 API Documentation

### Endpoints

#### Health Check
```
GET /health
```

#### Company Analysis
```
POST /api/v1/company/analyze
Body: {
  "pt_name": "PT Maju Jaya",
  "detailed": false
}
```

#### News Analysis
```
POST /api/v1/news/analyze
Body: {
  "company_name": "Bank Mandiri",
  "limit": 10
}
```

**Full API Documentation:** http://localhost:8000/docs (Swagger UI)

## 📁 Struktur Proyek

```
jamkrindo-sentimentanalysis-2025/
├── backend/                 # Backend FastAPI
│   ├── app/
│   │   ├── api/v1/         # API endpoints
│   │   ├── models/         # Database models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/      # Business logic services
│   │   ├── utils/          # Utilities
│   │   ├── config.py       # Configuration
│   │   └── database.py     # Database setup
│   ├── main.py             # FastAPI app
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile          # Backend Docker image
│
├── frontend/               # Frontend Next.js
│   ├── src/
│   │   ├── app/           # Next.js pages
│   │   ├── components/    # React components
│   │   ├── hooks/         # Custom hooks
│   │   └── lib/           # Utilities & types
│   ├── package.json       # Node dependencies
│   └── Dockerfile         # Frontend Docker image
│
├── .specs/                 # Technical specifications
├── .status/                # Project documentation
├── docker-compose.yml      # Docker Compose config
├── nginx.conf              # Nginx reverse proxy
└── README.md              # This file
```

## ⚙️ Konfigurasi

### Environment Variables

#### Backend
- `PERPLEXITY_API_KEY` (required) - API key untuk Perplexity AI
- `DATABASE_URL` (optional) - Default: `sqlite:///./data/credit_scoring.db`
- `LOG_LEVEL` (optional) - Default: `INFO`
- `TORCH_DEVICE` (optional) - Default: `cpu`

#### Frontend
- `NEXT_PUBLIC_API_URL` (required) - Backend API URL

Lihat [.status/configuration.md](.status/configuration.md) untuk detail lengkap.

## 🗄️ Database

Database menggunakan SQLite dengan struktur:

- `companies` - Data perusahaan
- `company_data` - Data mentah dari Perplexity
- `sentiment_results` - Hasil analisis sentimen
- `legal_records` - Catatan hukum dari Mahkamah Agung
- `analysis_summary` - Ringkasan analisis dan rekomendasi

Lihat [.status/database-schema.md](.status/database-schema.md) untuk detail schema.

## 📊 Risk Scoring

Skor risiko dihitung dengan formula:

```
risk_score = (sentiment_component × 30%) + 
             (mentions_component × 30%) + 
             (legal_component × 40%)
```

**Risk Levels:**
- 🟢 **HIJAU** (≤30): Disarankan untuk persetujuan
- 🟡 **KUNING** (31-65): Perlu ditinjau
- 🔴 **MERAH** (>65): Tidak disarankan

## 🔍 Dokumentasi Lengkap

Dokumentasi detail tersedia di folder [.status/](.status/):

- [README.md](.status/README.md) - Index dokumentasi
- [Database Schema](.status/database-schema.md) - Struktur database
- [Backend Services](.status/backend-services.md) - Dokumentasi services
- [API Endpoints](.status/api-endpoints.md) - Dokumentasi API
- [Frontend Components](.status/frontend-components.md) - Dokumentasi komponen UI
- [Features](.status/features.md) - Daftar fitur
- [Architecture](.status/architecture.md) - Arsitektur sistem
- [Configuration](.status/configuration.md) - Konfigurasi lengkap

## 🐛 Troubleshooting

### Backend tidak bisa start
- Pastikan `PERPLEXITY_API_KEY` sudah di-set
- Check port 8000 tidak digunakan aplikasi lain
- Lihat logs: `docker compose logs backend`

### Frontend tidak bisa connect ke backend
- Pastikan `NEXT_PUBLIC_API_URL` benar
- Check CORS configuration di backend
- Pastikan backend sudah running

### Model sentiment tidak bisa di-download
- Check koneksi internet (untuk download pertama)
- Pastikan disk space cukup
- Check logs untuk error detail

### Crawler timeout
- Crawler memiliki timeout 15 detik
- Jika timeout, sistem akan return empty results gracefully
- Check koneksi internet dan akses ke Mahkamah Agung website

## 🚧 Development

### Menjalankan Tests

```bash
# Backend tests (jika ada)
cd backend
pytest

# Frontend tests (jika ada)
cd frontend
npm test
```

### Code Style

- **Backend**: Mengikuti PEP 8
- **Frontend**: ESLint dan Prettier (jika dikonfigurasi)

## 📝 License

[Add your license here]

## 👥 Contributors

- [Your name/team]

## 🔗 Links

- **Repository**: https://github.com/ekkirinaldi/jamkrindo-sentimentanalysis-2025
- **Perplexity AI**: https://www.perplexity.ai/
- **Mahkamah Agung**: https://putusan3.mahkamahagung.go.id

## 📞 Support

Untuk pertanyaan atau issues, silakan buat issue di GitHub repository.

---

**Note**: Pastikan untuk tidak commit file `.env` yang berisi API keys. File tersebut sudah di-ignore oleh `.gitignore`.

