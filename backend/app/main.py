"""CivicFix FastAPI Application Entry Point."""

from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os

from app.config import settings
from app.database.session import init_db, SessionLocal
from app.routes.api import api_router
from app.utils.seed_data import seed_demo_data

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("civicfix")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    Initializes database tables and populates demo synthetic data if empty.
    """
    logger.info("Starting CivicFix backend application...")
    
    # 1. Initialize SQLite Database Tables
    init_db()
    logger.info("Database initialized.")

    # 2. Seed initial demo data for hackathon demonstration if empty
    db = SessionLocal()
    try:
        seeded_count = seed_demo_data(db=db, force=False)
        if seeded_count > 0:
            logger.info(f"Seeded {seeded_count} demo civic reports.")
        else:
            logger.info("Demo data already present in database.")
    except Exception as e:
        logger.warning(f"Demo data seeding skipped: {e}")
    finally:
        db.close()

    yield

    logger.info("Shutting down CivicFix backend application...")


# Initialize FastAPI App
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend API for CivicFix — A civic issue reporting platform connecting residents and city administration.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# 3. Configure CORS for frontend integration (Vite, Next.js, etc.)
origins = settings.CORS_ORIGINS
if isinstance(origins, str):
    origins = [origins]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Mount Uploads Directory for static file serving
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# 5. Include API Routers
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", include_in_schema=False)
def root_redirect():
    """Redirect root path to interactive Swagger documentation."""
    return RedirectResponse(url="/docs")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
