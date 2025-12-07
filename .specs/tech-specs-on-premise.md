# Technical Specifications - Sentiment Analysis Credit Scoring System

## 1. System Architecture

### High-Level Architecture
```
┌─────────────────────────────────────────────────┐
│         Next.js Frontend (Port 3000)            │
│  - Company search form                          │
│  - Results dashboard with charts                │
│  - Risk score visualization                     │
└─────────────┬───────────────────────────────────┘
              │ HTTP REST API
┌─────────────▼───────────────────────────────────┐
│       FastAPI Backend (Port 8000)               │
├─────────────────────────────────────────────────┤
│  POST  /api/v1/company/analyze                  │
│  GET   /health                                  │
└─────────────┬───────────────────────────────────┘
              │
    ┌─────────┼─────────┐
    │         │         │
┌───▼──┐  ┌──▼──┐  ┌───▼────┐
│SQLite│  │Cache│  │Perplx  │
│ .db  │  │Opt  │  │API     │
└──────┘  └─────┘  └────────┘
```

### Deployment Topology (On-Premise)
```
┌─────────────────────────────────────────────────────┐
│            Single Linux Server                      │
│        (Ubuntu 20.04 LTS - Minimum Spec)           │
│          2GB RAM, 1 vCPU, 20GB Disk                │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────────┐         ┌──────────────┐        │
│  │   Nginx      │────────▶│  Docker      │        │
│  │  Port 80/443 │         │  Compose     │        │
│  └──────────────┘         └──────────────┘        │
│                                 │                  │
│         ┌───────────────────────┼───────────────┐  │
│         │                       │               │  │
│    ┌────▼────┐           ┌────▼────┐      ┌───▼──┐
│    │ Frontend │           │ Backend  │      │ Data │
│    │Container │           │Container │      │Dir   │
│    │Port 3000 │           │Port 8000 │      │Vol   │
│    └──────────┘           └──────────┘      └──────┘
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 2. Technology Stack (On-Premise)

### Server Requirements
- **OS**: Ubuntu 20.04 LTS (or compatible Linux)
- **RAM**: 2GB minimum (4GB recommended)
- **CPU**: 1 vCPU minimum (2 vCPU recommended)
- **Storage**: 20GB minimum (SSD preferred)
- **Network**: Internal LAN/VPN access only
- **Docker**: Version 20.10+
- **Docker Compose**: Version 1.29+

### Frontend Stack
- **Framework**: Next.js 15 (TypeScript)
- **Runtime**: Node.js 18+
- **Package Manager**: npm/yarn
- **UI**: React 18 + Tailwind CSS 3.4
- **HTTP Client**: Axios 1.6+
- **Charts**: Recharts 2.10
- **Port**: 3000 (internal, proxied via Nginx)

### Backend Stack
- **Framework**: FastAPI 0.104+
- **Language**: Python 3.10+
- **Server**: Uvicorn 0.24+
- **ORM**: SQLAlchemy 2.0+
- **Database**: SQLite 3 (stored on persistent volume)
- **Web Scraping**: BeautifulSoup4 4.12+, Requests 2.31+
- **NLP**: NLTK 3.8+, Transformers 4.35+, Torch (CPU version)
- **Port**: 8000 (internal, proxied via Nginx)

### Reverse Proxy
- **Software**: Nginx (Alpine image)
- **Configuration**: SSL/TLS termination (optional)
- **Port**: 80 (or 443 with SSL)

### External APIs (Required)
- **Perplexity API**: REST endpoint for company information retrieval
- **Mahkamah Agung**: Web scraping via HTTP (no API key required)

---

## 3. Database Schema

### SQLite Database (`credit_scoring.db`)

```sql
-- Companies table: tracks company lookups
CREATE TABLE IF NOT EXISTS companies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pt_name TEXT NOT NULL UNIQUE,
    perplexity_search_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Company data: raw extracted content
CREATE TABLE IF NOT EXISTS company_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    source TEXT,
    raw_text TEXT,
    extracted_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- Sentiment analysis results
CREATE TABLE IF NOT EXISTS sentiment_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    text_analyzed TEXT,
    positive_score REAL,
    negative_score REAL,
    neutral_score REAL,
    compound_score REAL,
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- Legal records from Mahkamah Agung
CREATE TABLE IF NOT EXISTS legal_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    case_number TEXT,
    case_date TEXT,
    case_type TEXT,
    verdict_text TEXT,
    severity_level TEXT,
    source_url TEXT,
    crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- Analysis summary: final risk scores
CREATE TABLE IF NOT EXISTS analysis_summary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    sentiment_avg_score REAL,
    legal_records_count INTEGER,
    risk_score REAL,
    risk_level TEXT,
    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX idx_companies_pt_name ON companies(pt_name);
CREATE INDEX idx_company_data_company_id ON company_data(company_id);
CREATE INDEX idx_sentiment_results_company_id ON sentiment_results(company_id);
CREATE INDEX idx_legal_records_company_id ON legal_records(company_id);
CREATE INDEX idx_analysis_summary_company_id ON analysis_summary(company_id);
```

**Storage**: `/app/data/credit_scoring.db` (Docker persistent volume)

---

## 4. API Specification

### Base URL
```
http://localhost:8000  (development)
http://nginx-proxy/api (production)
```

### Endpoints

#### POST `/api/v1/company/analyze`
**Request Body**:
```json
{
  "pt_name": "PT Maju Jaya Sentosa",
  "detailed": false
}
```

**Response** (200 OK):
```json
{
  "company_name": "PT Maju Jaya Sentosa",
  "status": "success",
  "analysis": {
    "risk_assessment": {
      "risk_score": 45.5,
      "risk_level": "YELLOW",
      "sentiment_component": 55.0,
      "mentions_component": 40.0,
      "legal_component": 42.0,
      "details": {
        "total_texts_analyzed": 12,
        "positive_texts": 5,
        "negative_texts": 3,
        "legal_cases_found": 1,
        "max_case_severity": "medium"
      },
      "recommendation": "⚠️ REVIEW REQUIRED: Company has legal issues..."
    },
    "sentiment_analysis": {
      "total_texts": 12,
      "valid_analyses": 12,
      "average_score": 0.55,
      "positive_count": 5,
      "neutral_count": 4,
      "negative_count": 3
    },
    "legal_records": {
      "company_name": "PT Maju Jaya Sentosa",
      "cases_found": 1,
      "cases": [
        {
          "case_number": "001/PDT/2023",
          "case_date": "2023-05-15",
          "case_type": "perdata",
          "severity": "medium",
          "verdict_summary": "Court decision summary..."
        }
      ]
    }
  },
  "timestamp": "2025-12-06T17:32:00"
}
```

**Error Response** (500):
```json
{
  "detail": "Analysis failed: [error message]"
}
```

#### GET `/health`
**Response** (200):
```json
{
  "status": "ok"
}
```

---

## 5. Risk Scoring Formula

### Calculation
```
Final Risk Score = (Sentiment × 0.30) + (Mentions × 0.30) + (Legal × 0.40)

Where:
  Sentiment = (1 - average_sentiment_score) × 100
  Mentions = (negative_count / total_count) × 100
  Legal = min(100, (case_count × 12) + (severity_bonus))

Severity Bonus:
  - high: 40 points
  - medium: 25 points
  - low: 10 points
  - none: 0 points
```

### Risk Levels
- **GREEN** (0-30): Low risk → Recommended for approval
- **YELLOW** (31-65): Medium risk → Requires review
- **RED** (66-100): High risk → Not recommended

---

## 6. Backend Services Architecture

### Service 1: PerplexityService
**Purpose**: Query Perplexity API for company information
**Input**: Company PT name
**Output**: Raw text content + extracted metadata
**Timeout**: 60 seconds
**Rate Limit**: 100 requests/day (configurable)

**Key Methods**:
- `search_company(pt_name)` → Dict with raw_response, extracted_text, sources
- `extract_sentiment_text(raw_text)` → Cleaned text for analysis

### Service 2: SentimentAnalysisService
**Purpose**: Perform sentiment analysis on extracted text
**Models**: 
  - VADER (NLTK) - Fast, no GPU needed
  - Transformers (distilbert-base-multilingual-uncased-sentiment) - Accurate
**Input**: Text strings
**Output**: Sentiment scores and labels

**Key Methods**:
- `analyze_text(text)` → Dict with vader_scores, transformer_scores, consensus_score
- `analyze_batch(texts)` → Aggregated statistics

### Service 3: MahkamahAgungCrawler
**Purpose**: Web scrape legal records from Mahkamah Agung
**Target**: https://putusan.mahkamahagung.go.id
**Scraping Method**: BeautifulSoup4 + requests
**Rate Limiting**: 0.5 second delay between requests
**Input**: Company PT name
**Output**: List of legal cases with metadata

**Key Methods**:
- `search_company(pt_name)` → Dict with cases_found, cases[], max_severity
- `_parse_case_element(element)` → Individual case data
- `_determine_case_type(title)` → Case type classification

### Service 4: RiskScoringService
**Purpose**: Calculate final risk score from components
**Input**: Sentiment analysis results + Legal records
**Output**: Risk score (0-100), risk level (GREEN/YELLOW/RED), recommendation

**Key Methods**:
- `calculate_risk_score(sentiment_data, legal_data)` → Dict with risk_score, risk_level, recommendation
- `_calculate_sentiment_component()` → Sentiment risk (0-100)
- `_calculate_mentions_component()` → Negative mentions risk (0-100)
- `_calculate_legal_component()` → Legal record risk (0-100)

---

## 7. Frontend Components Architecture

### Component Hierarchy
```
Home (page.tsx)
├── CompanySearchForm
│   └── Input + Submit button
├── AnalysisLoader
│   └── Spinner animation
├── RiskScoreBadge
│   ├── Risk score display (0-100)
│   ├── Risk level badge (GREEN/YELLOW/RED)
│   ├── Recommendation text
│   └── Component breakdown (3 boxes)
├── ResultsChart
│   ├── Sentiment pie chart
│   └── Risk components bar chart
├── LegalRecordsTable
│   ├── Cases table
│   └── Case details expansion
└── Action Buttons
    ├── New Search
    └── Export Results (JSON)
```

### State Management
**Hook**: `useAnalysis()` (React Hooks + Context)
**State Shape**:
```typescript
{
  isLoading: boolean,
  result: CompanyAnalysisResult | null,
  error: string | null,
  history: CompanyAnalysisResult[]
}
```

### HTTP Communication
**Client**: Axios instance with 2-minute timeout
**Base URL**: From `NEXT_PUBLIC_API_URL` env variable
**Methods**:
- `POST /api/v1/company/analyze` - Main analysis
- `GET /health` - Health check

---

## 8. Configuration & Environment

### Backend `.env`
```bash
# API Keys
PERPLEXITY_API_KEY=sk_pplx_xxxxxxxxxxxxx

# Database
DATABASE_URL=sqlite:///./data/credit_scoring.db

# Server
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000

# Rate Limiting
PERPLEXITY_MAX_REQUESTS_PER_DAY=100
MAHKAMAH_CRAWL_DELAY_SECONDS=0.5

# NLP Model
SENTIMENT_MODEL=distilbert-base-multilingual-uncased-sentiment
TORCH_DEVICE=cpu  # Use 'cpu' for on-premise, no GPU
```

### Frontend `.env.local`
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Docker `.env` (root directory)
```bash
PERPLEXITY_API_KEY=sk_pplx_xxxxxxxxxxxxx
COMPOSE_PROJECT_NAME=sa-credit-scoring
```

---

## 9. Docker Compose Configuration

### `docker-compose.yml` (On-Premise)
```yaml
version: '3.8'

services:
  # FastAPI Backend
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: sa-backend
    restart: unless-stopped
    environment:
      - PERPLEXITY_API_KEY=${PERPLEXITY_API_KEY}
      - DATABASE_URL=sqlite:///./data/credit_scoring.db
      - LOG_LEVEL=INFO
      - TORCH_DEVICE=cpu
    volumes:
      - backend_data:/app/data
      - ./backend:/app
    networks:
      - sa-network
    expose:
      - "8000"

  # Next.js Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: sa-frontend
    restart: unless-stopped
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
    networks:
      - sa-network
    expose:
      - "3000"

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    container_name: sa-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/etc/nginx/certs:ro
    depends_on:
      - backend
      - frontend
    networks:
      - sa-network

volumes:
  backend_data:
    driver: local

networks:
  sa-network:
    driver: bridge
```

### `Dockerfile` (Backend)
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies (CPU torch only)
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data
RUN python -m nltk.downloader vader_lexicon punkt -d /usr/local/share/nltk_data

# Copy app
COPY . .

# Expose port
EXPOSE 8000

# Run
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### `Dockerfile` (Frontend)
```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
```

---

## 10. Deployment Instructions

### Prerequisites
- Linux server (Ubuntu 20.04+ recommended)
- Docker & Docker Compose installed
- Perplexity API key
- Network access to external APIs (Perplexity + Mahkamah Agung)

### Steps

```bash
# 1. Clone/download project to server
mkdir -p /opt/sa-credit-scoring
cd /opt/sa-credit-scoring

# 2. Create .env file with API key
cat > .env <<EOF
PERPLEXITY_API_KEY=sk_pplx_xxxxxxxxxxxxx
COMPOSE_PROJECT_NAME=sa-credit-scoring
EOF

# 3. Create data directory
mkdir -p data

# 4. Configure Nginx (see next section)
# Copy nginx.conf to project root

# 5. Build and run containers
docker-compose up -d

# 6. Verify health
curl http://localhost/health

# 7. Access web interface
# Open browser to http://<server-ip>/
```

### System Startup Command
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Backup database
cp data/credit_scoring.db data/credit_scoring.db.backup
```

---

## 11. Nginx Configuration

### `nginx.conf`
```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:3000;
    }

    # HTTP redirect to HTTPS (optional)
    server {
        listen 80;
        server_name _;
        return 301 https://$host$request_uri;
    }

    # HTTPS server block
    server {
        listen 443 ssl;
        server_name _;

        # SSL certificates (optional)
        ssl_certificate /etc/nginx/certs/cert.pem;
        ssl_certificate_key /etc/nginx/certs/key.pem;

        # API proxy
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_read_timeout 120s;
        }

        # Health check endpoint
        location /health {
            proxy_pass http://backend;
        }

        # Frontend
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }

    # HTTP-only version (no SSL)
    server {
        listen 80 default_server;
        server_name _;

        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_read_timeout 120s;
        }

        location /health {
            proxy_pass http://backend;
        }

        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
        }
    }
}
```

---

## 12. Performance Specifications

| Parameter | Specification |
|-----------|---------------|
| **Analysis Duration** | 15-30 seconds (typical) |
| **API Response Time** | < 100ms (excluding external API calls) |
| **Memory Usage** | 1.5-2GB (both containers combined) |
| **Database Size** | ~1MB per 100 analyses |
| **Concurrent Requests** | 5-10 (depends on server specs) |
| **Perplexity API Latency** | 5-15 seconds (external) |
| **Web Scraping Duration** | 5-10 seconds (Mahkamah Agung) |

---

## 13. Backup & Recovery

### Database Backup
```bash
# Manual backup
docker exec sa-backend cp data/credit_scoring.db data/credit_scoring.db.$(date +%Y%m%d)

# Automated daily backup (crontab)
0 2 * * * docker exec sa-backend cp data/credit_scoring.db data/credit_scoring.db.$(date +\%Y\%m\%d)
```

### Restore from Backup
```bash
# Stop containers
docker-compose down

# Restore file
cp data/credit_scoring.db.backup data/credit_scoring.db

# Start containers
docker-compose up -d
```

### Data Retention Policy
- Keep all analysis records indefinitely (audit trail)
- SQLite database automatically maintains ACID compliance
- Backup database before major updates

---

## 14. Troubleshooting

### Backend Container Won't Start
```bash
# Check logs
docker-compose logs backend

# Verify Python dependencies installed
docker exec sa-backend pip list

# Rebuild container
docker-compose down
docker-compose build --no-cache backend
docker-compose up -d
```

### Frontend Can't Connect to Backend
```bash
# Check backend health
curl http://localhost:8000/health

# Verify network
docker network ls
docker network inspect sa-network

# Check Nginx logs
docker-compose logs nginx
```

### Perplexity API Errors
```
Error: 401 Unauthorized
→ Verify PERPLEXITY_API_KEY in .env

Error: Rate limit exceeded
→ Check PERPLEXITY_MAX_REQUESTS_PER_DAY setting

Error: Connection timeout
→ Verify outbound internet connectivity
```

### Web Scraping Failures
```
Error: 403 Forbidden from Mahkamah Agung
→ May be IP-blocked; try VPN or proxy
→ Reduce crawl frequency (increase MAHKAMAH_CRAWL_DELAY_SECONDS)

Error: HTML parsing errors
→ Website structure may have changed
→ Update BeautifulSoup selectors in mahkamah_crawler.py
```

---

## 15. Monitoring & Logs

### Container Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Log Files (Inside Containers)
```bash
# Backend logs (stdout in uvicorn)
docker-compose logs backend

# Database logs
ls -la /app/data/  # Inside backend container
```

### Health Monitoring
```bash
# Manual health check
curl http://localhost/health

# Automated monitoring (cron)
*/5 * * * * curl -f http://localhost/health || echo "Service down" | mail -s "Alert" admin@example.com
```

---

## 16. Security Considerations

### On-Premise Only
- No cloud services required
- All data stored locally on server
- Internal network only (no public internet exposure recommended)

### API Key Management
- Store `PERPLEXITY_API_KEY` in `.env` file (not in Git)
- Limit Perplexity API key rate and usage
- Rotate API key periodically

### Network Security
- Place server behind firewall
- Restrict access to port 80/443 (use VPN or whitelist IPs)
- Disable external routing for Nginx if not needed

### Database Security
- SQLite file stored in persistent Docker volume
- Regular backups (see Backup & Recovery section)
- No default credentials (SQLite is file-based)

---

## 17. System Requirements Checklist

### Minimum (MVP)
- [ ] Linux server (Ubuntu 20.04+)
- [ ] 2GB RAM
- [ ] 1 vCPU
- [ ] 20GB disk space
- [ ] Docker 20.10+
- [ ] Docker Compose 1.29+
- [ ] Outbound internet (Perplexity API + Mahkamah Agung)

### Recommended (Production)
- [ ] Linux server (Ubuntu 20.04+ LTS)
- [ ] 4GB RAM
- [ ] 2 vCPU
- [ ] 50GB SSD disk
- [ ] Docker 24.0+
- [ ] Docker Compose 2.0+
- [ ] SSL/TLS certificates
- [ ] Network monitoring
- [ ] Automated backups

---

## 18. Development vs Production Mode

### Development
```bash
docker-compose up -d

# Services run with hot reload
# Logs visible in console
# No SSL
# Frontend at http://localhost:3000
```

### Production
```bash
# Edit docker-compose.yml:
# - Remove volume mounts for code
# - Set restart: always
# - Configure Nginx with SSL
# - Add logging driver

docker-compose -f docker-compose.prod.yml up -d
```
