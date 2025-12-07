# Architecture Documentation

## System Overview

Sistem analisis sentimen untuk penilaian kredit dengan arsitektur on-premise menggunakan Docker Compose.

## Architecture Diagram

```
┌─────────────────────────────────────────┐
│           User Browser                 │
│      (http://localhost:3000)          │
└──────────────┬────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│         Nginx Reverse Proxy             │
│      (Port 80/443)                      │
└──────────────┬────────────────────────┘
               │
       ┌───────┴───────┐
       │               │
       ▼               ▼
┌──────────────┐  ┌──────────────┐
│   Frontend   │  │   Backend    │
│  Next.js     │  │   FastAPI    │
│  Port 3000   │  │  Port 8000   │
└──────────────┘  └──────┬───────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   SQLite     │  │  Perplexity  │  │  Mahkamah    │
│   Database   │  │     API      │  │   Agung      │
└──────────────┘  └──────────────┘  └──────────────┘
```

## Component Architecture

### Backend Layer

```
backend/
├── app/
│   ├── api/v1/          # API endpoints
│   │   ├── company.py   # Company analysis
│   │   ├── news.py      # News analysis
│   │   └── health.py    # Health check
│   ├── models/          # Database models
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # Business logic
│   │   ├── perplexity_service.py
│   │   ├── sentiment_service.py
│   │   ├── mahkamah_crawler.py
│   │   └── risk_scoring.py
│   ├── utils/           # Utilities
│   ├── config.py        # Configuration
│   └── database.py      # Database setup
├── main.py              # FastAPI app
└── requirements.txt     # Dependencies
```

### Frontend Layer

```
frontend/
├── src/
│   ├── app/             # Next.js pages
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   └── globals.css
│   ├── components/      # React components
│   │   ├── CompanySearchForm.tsx
│   │   ├── RiskScoreBadge.tsx
│   │   ├── ResultsChart.tsx
│   │   ├── LegalRecordsTable.tsx
│   │   ├── NewsArticlesList.tsx
│   │   ├── EvidenceSummary.tsx
│   │   ├── SourceCitations.tsx
│   │   └── AnalysisLoader.tsx
│   ├── hooks/          # Custom hooks
│   │   └── useAnalysis.ts
│   └── lib/            # Utilities
│       ├── api.ts      # API client
│       └── types.ts    # TypeScript types
└── package.json
```

## Data Flow

### Company Analysis Flow

```
1. User Input (Company Name)
   │
   ▼
2. Frontend: CompanySearchForm
   │
   ▼
3. API Call: POST /api/v1/company/analyze
   │
   ├─► 4a. PerplexityService.search_company()
   │      └─► Perplexity API
   │
   ├─► 4b. SentimentAnalysisService.analyze_batch()
   │      └─► VADER + Transformers
   │
   ├─► 4c. MahkamahAgungCrawler.search_company()
   │      └─► Web Scraping (Crawl4AI)
   │
   ├─► 4d. PerplexityService.search_latest_news()
   │      └─► Perplexity API
   │      └─► SentimentAnalysisService (per article)
   │
   └─► 4e. RiskScoringService.calculate_risk_score()
   │
   ▼
5. Database: Save results
   │
   ▼
6. API Response
   │
   ▼
7. Frontend: Display results
   ├─► EvidenceSummary
   ├─► NewsArticlesList
   ├─► LegalRecordsTable
   ├─► ResultsChart
   └─► SourceCitations
```

## Service Dependencies

```
CompanyAnalysisEndpoint
├── PerplexityService
│   └── Perplexity API (external)
├── SentimentAnalysisService
│   ├── NLTK VADER
│   └── Hugging Face Transformers
├── MahkamahAgungCrawler
│   └── Crawl4AI / Requests
└── RiskScoringService
    └── (uses results from above)
```

## Database Schema Relationships

```
Company (1)
  ├── CompanyData (many)
  ├── SentimentResult (many)
  ├── LegalRecord (many)
  └── AnalysisSummary (many)
```

## API Request/Response Flow

### Request
```
Frontend → Axios → FastAPI → Services → External APIs/Database
```

### Response
```
External APIs/Database → Services → FastAPI → Axios → Frontend → React Components
```

## Error Handling Flow

```
Service Error
  │
  ├─► Custom Exception (Bahasa Indonesia)
  │
  ├─► Logger (log error)
  │
  └─► HTTPException (500)
      │
      └─► Frontend Error Display
```

## Performance Considerations

### Backend
- **Lazy Loading:** Sentiment model loaded on first use
- **Timeout Protection:** Crawler has 15s timeout
- **Async Operations:** All I/O operations are async
- **Error Recovery:** Graceful degradation if services fail

### Frontend
- **Loading States:** Show progress during analysis
- **Error Boundaries:** Catch and display errors
- **Optimistic UI:** Immediate feedback
- **Timeout:** 120s API timeout

## Security

### Implemented
- Input validation (Pydantic schemas)
- SQL injection protection (SQLAlchemy ORM)
- CORS configuration
- Environment variables for secrets

### Recommendations
- Add rate limiting
- Add authentication/authorization
- Add request validation middleware
- Add logging and monitoring

## Deployment Architecture

### Docker Compose Services

1. **backend**
   - Image: Built from `backend/Dockerfile`
   - Port: 8000 (internal)
   - Volumes: `backend_data` for database

2. **frontend**
   - Image: Built from `frontend/Dockerfile`
   - Port: 3000 (internal)
   - Environment: `NEXT_PUBLIC_API_URL`

3. **nginx**
   - Image: `nginx:alpine`
   - Ports: 80, 443 (external)
   - Reverse proxy untuk backend dan frontend

### Network

All services on `sa-network` bridge network.

## Configuration Management

### Environment Variables

**Backend:**
- `PERPLEXITY_API_KEY`
- `DATABASE_URL`
- `LOG_LEVEL`
- `TORCH_DEVICE`
- `MAHKAMAH_CRAWL_DELAY_SECONDS`

**Frontend:**
- `NEXT_PUBLIC_API_URL`

**Docker Compose:**
- `.env` file di root

## Monitoring & Logging

### Logging
- Python logging dengan configurable level
- Log messages dalam Bahasa Indonesia
- Error tracking dengan stack traces

### Health Checks
- `/health` endpoint untuk monitoring
- Returns status dan timestamp

## Scalability Considerations

### Current (On-Premise)
- Single instance per service
- SQLite database (file-based)
- No load balancing

### Future Scalability
- PostgreSQL untuk production
- Redis untuk caching
- Multiple backend instances
- Load balancer
- Message queue untuk async processing

