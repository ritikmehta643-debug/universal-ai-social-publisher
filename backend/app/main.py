import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from .config import MEDIA_DIR, DEBUG
from .database import init_db
from .services.scheduler import PublishingScheduler
from .api import dashboard, providers, facebook, templates, topics, schedules, posts

# Configure Logging
logging.basicConfig(
    level=logging.INFO if DEBUG else logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("UniversalAIPublisher")

# Scheduler instance
scheduler = PublishingScheduler()

app = FastAPI(
    title="Universal AI Social Publisher",
    description="Universal AI Facebook Auto Posting Platform",
    version="1.0.0"
)

@app.on_event("startup")
def startup_event():
    logger.info("Initializing database...")
    init_db()
    logger.info("Starting background publisher scheduler...")
    scheduler.start()

@app.on_event("shutdown")
def shutdown_event():
    logger.info("Stopping scheduler...")
    scheduler.stop()

# Enable CORS for React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve generated media files
MEDIA_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=str(MEDIA_DIR)), name="media")

# Include Routers
app.include_router(dashboard.router)
app.include_router(providers.router)
app.include_router(facebook.router)
app.include_router(templates.router)
app.include_router(topics.router)
app.include_router(schedules.router)
app.include_router(posts.router)

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "app": "Universal AI Social Publisher",
        "scheduler_running": scheduler._is_running
    }

# Check if frontend build exists to serve static dist
FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="frontend")
