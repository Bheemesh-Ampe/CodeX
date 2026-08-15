"""Central API router configuration."""

from fastapi import APIRouter
from app.routes import health, issues, users, admin, reports, ai

api_router = APIRouter()

# Register sub-routers
api_router.include_router(health.router)
api_router.include_router(users.router)
api_router.include_router(issues.router)
api_router.include_router(admin.router)
api_router.include_router(reports.router)
api_router.include_router(ai.router)
