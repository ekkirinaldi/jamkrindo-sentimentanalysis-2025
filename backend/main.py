"""
FastAPI main application.
API Analisis Sentimen untuk Penilaian Kredit
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.database import init_db
from app.api.v1 import company, health, news
from app.utils.logger import logger

app = FastAPI(
    title="API Analisis Sentimen untuk Penilaian Kredit",
    description="API untuk analisis sentimen dan penilaian risiko kredit perusahaan Indonesia",
    version="0.1.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8000",
        "http://frontend:3000",
        "http://backend:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Gagal menginisialisasi database: {str(e)}")

# Routes
app.include_router(company.router)
app.include_router(health.router)
app.include_router(news.router)

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "API Analisis Sentimen untuk Penilaian Kredit",
        "version": "0.1.0",
        "status": "ok"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

