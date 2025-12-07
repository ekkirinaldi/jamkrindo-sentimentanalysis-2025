# Configuration Documentation

## Environment Variables

### Backend Configuration

**File:** `backend/.env` atau environment variables

#### Required Variables

**PERPLEXITY_API_KEY**
- **Description:** API key untuk Perplexity AI
- **Example:** `sk_pplx_xxxxxxxxxxxxx`
- **Required:** Yes
- **Location:** `backend/app/config.py`

**DATABASE_URL**
- **Description:** Connection string untuk database
- **Default:** `sqlite:///./data/credit_scoring.db`
- **Format:** SQLAlchemy connection string
- **Required:** No (has default)

#### Optional Variables

**LOG_LEVEL**
- **Description:** Level logging
- **Default:** `INFO`
- **Options:** `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- **Location:** `backend/app/utils/logger.py`

**HOST**
- **Description:** Host untuk FastAPI server
- **Default:** `0.0.0.0`
- **Required:** No

**PORT**
- **Description:** Port untuk FastAPI server
- **Default:** `8000`
- **Required:** No

**MAHKAMAH_CRAWL_DELAY_SECONDS**
- **Description:** Delay antara request saat crawling
- **Default:** `0.5`
- **Purpose:** Rate limiting untuk menghindari blocking

**SENTIMENT_MODEL**
- **Description:** Model untuk sentiment analysis
- **Default:** `distilbert-base-multilingual-uncased-sentiment`
- **Note:** Model sebenarnya menggunakan `nlptown/bert-base-multilingual-uncased-sentiment`

**TORCH_DEVICE**
- **Description:** Device untuk PyTorch
- **Default:** `cpu`
- **Options:** `cpu`, `cuda`, `cuda:0`
- **Purpose:** On-premise biasanya menggunakan CPU

---

### Frontend Configuration

**File:** `frontend/.env.local`

#### Required Variables

**NEXT_PUBLIC_API_URL**
- **Description:** Base URL untuk backend API
- **Development:** `http://localhost:8000`
- **Production:** `http://backend:8000` (Docker) atau URL production
- **Required:** Yes (untuk API calls)

---

### Docker Compose Configuration

**File:** `.env` (root directory)

#### Variables

**PERPLEXITY_API_KEY**
- **Description:** API key untuk Perplexity (dipass ke backend container)
- **Required:** Yes

**COMPOSE_PROJECT_NAME**
- **Description:** Nama project untuk Docker Compose
- **Default:** `sa-credit-scoring`
- **Required:** No

---

## Configuration Files

### Backend

#### `backend/app/config.py`
Central configuration module yang load semua environment variables.

**Functions:**
- Load `.env` file
- Provide defaults
- Export configuration constants

#### `backend/requirements.txt`
Python dependencies dengan versi spesifik.

**Key Dependencies:**
- `fastapi==0.104.1`
- `uvicorn[standard]==0.24.0`
- `sqlalchemy==2.0.23`
- `transformers==4.35.2`
- `torch==2.2.0`
- `crawl4ai>=0.3.0`
- `nltk==3.8.1`

#### `backend/Dockerfile`
Docker configuration untuk backend service.

**Features:**
- Python 3.11-slim base
- System dependencies
- NLTK data download
- Port 8000 exposed

---

### Frontend

#### `frontend/package.json`
Node.js dependencies dan scripts.

**Key Dependencies:**
- `next@15.5.7`
- `react@19.0.0`
- `typescript@5.7.2`
- `tailwindcss@3.4.17`
- `recharts@2.15.0`
- `axios@1.7.9`

#### `frontend/next.config.js`
Next.js configuration.

**Settings:**
- React strict mode
- TypeScript support

#### `frontend/tailwind.config.js`
Tailwind CSS configuration.

**Content:**
- Content paths
- Theme extensions
- Plugin configuration

#### `frontend/tsconfig.json`
TypeScript configuration.

**Settings:**
- Path aliases (`@/` → `src/`)
- Strict mode
- Module resolution

#### `frontend/postcss.config.js`
PostCSS configuration untuk Tailwind.

#### `frontend/Dockerfile`
Multi-stage Docker build untuk frontend.

**Stages:**
1. Builder: Install dependencies dan build
2. Runner: Production image dengan built files

---

### Infrastructure

#### `docker-compose.yml`
Orchestration untuk semua services.

**Services:**
- `backend`: FastAPI application
- `frontend`: Next.js application
- `nginx`: Reverse proxy

**Volumes:**
- `backend_data`: Persistent storage untuk database

**Networks:**
- `sa-network`: Bridge network untuk inter-service communication

#### `nginx.conf`
Nginx reverse proxy configuration.

**Routes:**
- `/api/` → backend:8000
- `/health` → backend:8000
- `/` → frontend:3000

**Features:**
- Proxy headers
- Timeout configuration (120s untuk long-running requests)

---

## Runtime Configuration

### Backend Startup

**Command:**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Startup Events:**
1. Load environment variables
2. Initialize database (`init_db()`)
3. Register routes
4. Start server

### Frontend Startup

**Development:**
```bash
npm run dev
```

**Production:**
```bash
npm start
```

**Build:**
```bash
npm run build
```

---

## Configuration Best Practices

### Security
- ✅ Never commit `.env` files
- ✅ Use environment variables for secrets
- ✅ `.gitignore` includes `.env` files
- ⚠️ Consider using secrets management for production

### Development
- ✅ Separate `.env` files per environment
- ✅ Default values untuk optional configs
- ✅ Clear documentation

### Production
- ⚠️ Use secure connection strings
- ⚠️ Enable HTTPS via Nginx
- ⚠️ Set appropriate log levels
- ⚠️ Configure resource limits in Docker

---

## Configuration Validation

### Backend
- Pydantic schemas validate request data
- Environment variables validated on startup
- Database connection tested on init

### Frontend
- TypeScript type checking
- Runtime validation via API client
- Environment variables validated at build time

---

## Troubleshooting

### Common Issues

1. **PERPLEXITY_API_KEY not found**
   - Check `.env` file exists
   - Verify variable name spelling
   - Check Docker Compose environment section

2. **Database connection failed**
   - Check `DATABASE_URL` format
   - Verify directory permissions for SQLite
   - Check Docker volume mounts

3. **Frontend can't connect to backend**
   - Verify `NEXT_PUBLIC_API_URL`
   - Check CORS configuration
   - Verify both services are running

4. **Model loading fails**
   - Check internet connection (for first download)
   - Verify disk space
   - Check `TORCH_DEVICE` setting

