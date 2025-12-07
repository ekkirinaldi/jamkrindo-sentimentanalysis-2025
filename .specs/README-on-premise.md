# Technical Specs Summary - On-Premise Implementation

## Files Created

**1. tech-specs-on-premise.md** (18 sections)
- Complete system architecture (on-premise only)
- Technology stack for Linux servers
- Database schema (SQLite)
- API specifications
- Risk scoring formula
- Backend services architecture
- Frontend components architecture
- Docker Compose configuration (full stack)
- Deployment instructions
- Nginx configuration
- Performance specifications
- Backup & recovery procedures
- Troubleshooting guide
- Monitoring & logging
- Security considerations
- System requirements checklist
- Development vs production mode

**2. backend-technical-specs.md** (10 sections)
- Python package dependencies (CPU-only torch)
- Backend project structure
- Complete service implementations:
  - PerplexityService (API integration)
  - SentimentAnalysisService (VADER + Transformers)
  - MahkamahAgungCrawler (web scraper)
  - RiskScoringService (risk calculation)
- API endpoint implementation
- FastAPI main application
- Configuration module
- Database setup (SQLAlchemy + SQLite)
- requirements.txt file
- Runtime notes & deployment checklist

**3. frontend-technical-specs.md** (20 sections)
- Node.js & npm dependencies
- Frontend project structure
- TypeScript type definitions
- API client implementation (Axios)
- Custom React hook (useAnalysis)
- Component implementations (5 components)
- Main page layout (page.tsx)
- Global styles (Tailwind CSS)
- TypeScript configuration
- Next.js configuration
- Tailwind configuration
- Environment configuration
- Docker build instructions
- Build & run commands
- Component communication flow
- Data flow diagram
- Browser compatibility
- Performance targets
- Error handling patterns
- Production deployment notes

---

## Key On-Premise Specifications

### Server Requirements (Minimum)
- OS: Ubuntu 20.04 LTS
- RAM: 2GB
- CPU: 1 vCPU
- Disk: 20GB
- Network: Internal LAN (outbound to Perplexity API only)

### Server Requirements (Recommended)
- OS: Ubuntu 20.04 LTS
- RAM: 4GB
- CPU: 2 vCPU
- Disk: 50GB SSD
- Network: Behind firewall with IP whitelist

### Technology Stack (No Cloud)
- **Frontend**: Next.js 15 + React 18 + Tailwind CSS
- **Backend**: FastAPI + Python 3.10+
- **Database**: SQLite (file-based, no server)
- **Proxy**: Nginx (reverse proxy)
- **Containerization**: Docker + Docker Compose
- **NLP**: NLTK + Transformers (CPU-only)
- **Scraping**: BeautifulSoup4 + Requests

### All Services Run Locally
- ✅ Frontend container (port 3000)
- ✅ Backend container (port 8000)
- ✅ Nginx reverse proxy (port 80/443)
- ✅ SQLite database (persistent volume)
- ✅ External: Perplexity API + Mahkamah Agung website

### No Cloud Dependencies
- ❌ No AWS/Azure/GCP
- ❌ No serverless functions
- ❌ No managed databases
- ❌ No CDN
- ❌ No third-party storage

---

## Quick Start Summary

```bash
# 1. Prepare server
sudo apt-get install docker.io docker-compose

# 2. Clone/setup project structure
mkdir -p /opt/sa-credit-scoring
cd /opt/sa-credit-scoring

# 3. Create environment file
cat > .env <<EOF
PERPLEXITY_API_KEY=sk_pplx_xxxxxxxxxxxxx
EOF

# 4. Create directories
mkdir -p data certs

# 5. Start services
docker-compose up -d

# 6. Access web interface
# http://<server-ip>/

# 7. Verify health
curl http://localhost/health
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────┐
│     Single Linux Server (On-Premise)        │
├─────────────────────────────────────────────┤
│                                             │
│  ┌────────────────────────────────────┐    │
│  │  Nginx Reverse Proxy (80/443)      │    │
│  │  - SSL/TLS termination             │    │
│  │  - Request routing                 │    │
│  └────────┬───────────────────────────┘    │
│           │                                 │
│    ┌──────┴──────┐                         │
│    │             │                         │
│  ┌─▼──┐      ┌───▼─┐                      │
│  │Next │      │FastAPI                    │
│  │.js  │      │Python Backend             │
│  │Port │      │Port 8000                  │
│  │3000 │      │                           │
│  └─┬──┘      └───┬─┐                      │
│    │             │ │                      │
│    │       ┌─────┘ └──────┐               │
│    │       │               │               │
│    │   ┌───▼──┐    ┌──────▼──┐           │
│    │   │SQLite│    │Transformers          │
│    │   │.db   │    │Models (300MB)        │
│    │   │Vol   │    │(Downloaded once)    │
│    │   └──────┘    └──────────┘           │
│    │                                      │
│    │  External APIs (Outbound Only)       │
│    ├─ Perplexity API                      │
│    └─ Mahkamah Agung Website              │
│                                             │
└─────────────────────────────────────────────┘
```

---

## Data Persistence

### Database
- **File**: `/app/data/credit_scoring.db`
- **Type**: SQLite (transactional, ACID-compliant)
- **Backup**: Simple file copy (see backup section)
- **Retention**: Indefinite (audit trail)

### ML Models
- **Location**: `~/.cache/huggingface/` inside backend container
- **Size**: ~300MB (transformers)
- **Downloaded**: On first analysis request
- **Cached**: Persists across container restarts

### Configuration
- **Location**: `.env` file in project root
- **Sensitive**: Contains PERPLEXITY_API_KEY
- **Backup**: Not required (easily regenerated)

---

## Analysis Workflow

```
1. User Input (PT Name)
   └─ Frontend sends POST /api/v1/company/analyze

2. Perplexity API Call (5-15 sec)
   └─ Fetch company information + news

3. Sentiment Analysis (2-3 sec)
   ├─ VADER sentiment (fast)
   └─ Transformers sentiment (accurate)

4. Web Scraping (5-10 sec)
   └─ Mahkamah Agung legal database

5. Risk Calculation (<1 sec)
   └─ Weighted formula (30/30/40)

6. Response (100ms)
   └─ Return full analysis to frontend

Total Duration: 15-30 seconds
```

---

## Configuration Reference

### Environment Variables (`.env`)
```
PERPLEXITY_API_KEY=sk_pplx_xxxxxxxxxxxxx   # Required
PERPLEXITY_MAX_REQUESTS_PER_DAY=100        # Optional
MAHKAMAH_CRAWL_DELAY_SECONDS=0.5           # Optional
LOG_LEVEL=INFO                             # Optional
```

### Docker Compose Overrides (Production)
- Set `restart: always` for services
- Remove volume mounts for code (use COPY instead)
- Configure logging driver for centralized logs
- Use external Nginx container with SSL certs

---

## Performance Characteristics

| Metric | Value |
|--------|-------|
| Single Analysis | 15-30 seconds |
| API Response Time | <100ms |
| Memory Usage (Idle) | ~600MB |
| Memory Usage (Active) | ~1.5GB peak |
| Database Growth | ~1MB per 100 analyses |
| Sentiment Model Size | ~300MB |
| Concurrent Requests | 5-10 |
| Uptime Target | >95% |

---

## Security Checklist

- [ ] `.env` file excluded from Git
- [ ] PERPLEXITY_API_KEY kept confidential
- [ ] Server behind firewall
- [ ] SSH key-based authentication only
- [ ] Nginx with HTTPS (optional for internal use)
- [ ] Database backups stored securely
- [ ] Access logs reviewed regularly
- [ ] API rate limiting configured
- [ ] Input validation enabled

---

## Monitoring & Maintenance

### Daily
- Check `/health` endpoint
- Review error logs in `docker-compose logs backend`

### Weekly
- Verify database size: `ls -lh data/credit_scoring.db`
- Check disk space: `df -h /`

### Monthly
- Backup database: `cp data/credit_scoring.db data/credit_scoring.db.backup`
- Review analysis statistics
- Test recovery procedures

### Quarterly
- Update Docker images
- Review security settings
- Performance optimization review

---

## Troubleshooting Quick Reference

### Backend won't start
```bash
docker-compose logs backend
docker-compose down
docker-compose build --no-cache backend
docker-compose up -d
```

### Can't connect to frontend
```bash
curl http://localhost:3000
docker-compose logs frontend
docker-compose logs nginx
```

### API errors
```bash
curl http://localhost:8000/health
cat .env  # Verify PERPLEXITY_API_KEY
docker exec sa-backend python -c "from transformers import pipeline; print('OK')"
```

### Database locked
```bash
# Stop all containers
docker-compose down

# Verify file
ls -la data/credit_scoring.db

# Restart
docker-compose up -d
```

---

## Files to Implement

### Backend
```
backend/
├── main.py
├── requirements.txt
├── .env.example
├── Dockerfile
└── app/
    ├── config.py
    ├── database.py
    ├── models/ (4 files)
    ├── schemas/ (4 files)
    ├── services/ (4 services)
    └── api/v1/ (endpoints)
```

### Frontend
```
frontend/
├── package.json
├── tsconfig.json
├── next.config.js
├── .env.local.example
├── Dockerfile
└── src/
    ├── app/ (2 files)
    ├── components/ (5 components)
    ├── hooks/ (1 hook)
    └── lib/ (2 files)
```

### Infrastructure
```
├── docker-compose.yml
├── nginx.conf
├── .env (fill in API key)
├── data/ (auto-created)
└── certs/ (for HTTPS, optional)
```

---

## Validation Checklist

- [ ] All services start with `docker-compose up -d`
- [ ] Frontend accessible at `http://localhost/`
- [ ] Backend health check responds: `curl http://localhost/health`
- [ ] Database initializes on first API call
- [ ] Sentiment model downloads on first analysis (<5 minutes)
- [ ] Perplexity API returns results (not errors)
- [ ] Mahkamah Agung scraping works (finds cases or returns 0)
- [ ] Risk score calculated and displayed
- [ ] Analysis completes in <30 seconds
- [ ] Export JSON functionality works
- [ ] No hardcoded secrets in code
- [ ] Logs show successful operations

---

## Notes

- **No Cloud**: 100% on-premise, all data local
- **Simple Deployment**: Single `docker-compose up -d`
- **No Additional Services**: No managed databases, no serverless
- **Scalable Later**: Easy to add Redis, PostgreSQL post-MVP
- **Open Source**: All tech stacks are open source
- **CPU Only**: No GPU required (NLTK + transformers on CPU)
- **Low Maintenance**: Minimal ops overhead
- **Audit Ready**: All analyses logged to SQLite
