"""Health check route."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database.session import get_db
from app.schemas.health import HealthResponse
from app.config import settings

router = APIRouter(prefix="/health", tags=["Health"])


@router.get(
    "",
    response_model=HealthResponse,
    summary="Application Health Check",
    description="Returns the system health status, version, and database connectivity.",
)
def check_health(db: Session = Depends(get_db)) -> HealthResponse:
    """Check API and database status."""
    try:
        # Perform a lightweight query to verify SQLite database connectivity
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as exc:
        db_status = f"disconnected: {str(exc)}"
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database unreachable: {str(exc)}",
        )

    return HealthResponse(
        status="healthy",
        app_name=settings.PROJECT_NAME,
        version="0.1.0",
        database=db_status,
    )
