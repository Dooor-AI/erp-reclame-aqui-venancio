from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine
from app.db.base import Base
from app.api.endpoints import complaints, analytics, responses, benchmark
from app.scraper.scheduler import start_scheduler, stop_scheduler, run_now
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="API para gerenciamento de reclamaÃ§Ãµes da VenÃ¢ncio no Reclame Aqui"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ajustar em produÃ§Ã£o
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    """Create database tables and start scheduler on startup"""
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")

    # Start scraping scheduler
    logger.info("Starting scraping scheduler...")
    start_scheduler()


@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    logger.info("Shutting down...")
    stop_scheduler()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "VenÃ¢ncio RPA API",
        "version": settings.API_VERSION,
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok"}


@app.post("/scrape/run")
async def run_scraper_manually(background_tasks: BackgroundTasks):
    """
    Manually trigger scraping job (for testing)

    This will run the scraper in the background and return immediately.
    Check logs for scraping progress.
    """
    background_tasks.add_task(run_now)
    return {
        "message": "Scraping job started in background",
        "note": "Check logs for progress"
    }


# Include routers
app.include_router(complaints.router)
app.include_router(analytics.router)
app.include_router(responses.router)
app.include_router(benchmark.router)
