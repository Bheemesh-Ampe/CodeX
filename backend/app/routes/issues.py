"""API routes for Civic Issues."""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.issue import (
    IssueCreate,
    IssueUpdateSchema,
    IssueStatusUpdate,
    IssueResponse,
    IssueStatsResponse,
    IssueStatus,
    IssuePriority,
)
from app.schemas.issue_update import IssueUpdateCreate, IssueUpdateResponse
from app.services.issue_service import issue_service
from app.utils.seed_data import seed_demo_data

router = APIRouter(prefix="/issues", tags=["Issues"])


@router.post(
    "",
    response_model=IssueResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Report a civic issue",
    description="Allows residents to report a new civic issue with title, description, latitude, longitude, and optional address or image.",
)
def create_issue(
    issue_in: IssueCreate,
    db: Session = Depends(get_db),
) -> IssueResponse:
    """
    Create and persist a new civic issue.
    - Validates request payload via Pydantic
    - Saves issue to SQLite
    - Sets initial status to REPORTED
    - Sets default priority to MEDIUM
    - Initializes status history audit log
    - Returns HTTP 201 Created with the created issue
    """
    return issue_service.create(db=db, issue_in=issue_in)


@router.get(
    "",
    response_model=List[IssueResponse],
    summary="List civic issues",
    description="Retrieve all reported civic issues. Supports optional filtering by status and category.",
)
def list_issues(
    status: Optional[str] = Query(None, description="Filter by issue status (e.g. REPORTED, IN_REVIEW, IN_PROGRESS, RESOLVED, REJECTED)"),
    category: Optional[str] = Query(None, description="Filter by category (e.g. Pothole, Streetlight, Water & Drainage)"),
    priority: Optional[str] = Query(None, description="Filter by priority (e.g. LOW, MEDIUM, HIGH, CRITICAL)"),
    search: Optional[str] = Query(None, description="Search term across title, description, and address"),
    created_by: Optional[int] = Query(None, description="Filter by resident user ID"),
    assigned_to: Optional[int] = Query(None, description="Filter by assigned staff/admin ID"),
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(100, ge=1, le=500, description="Page limit"),
    db: Session = Depends(get_db),
) -> List[IssueResponse]:
    """List issues matching query criteria."""
    items, _ = issue_service.get_multi(
        db=db,
        status=status,
        category=category,
        priority=priority,
        search=search,
        created_by=created_by,
        assigned_to=assigned_to,
        skip=skip,
        limit=limit,
    )
    return items


@router.get(
    "/stats/summary",
    response_model=IssueStatsResponse,
    summary="Get issue statistics",
    description="Provides aggregated issue counts by status, category, and priority for dashboard metrics.",
)
def get_stats_summary(
    db: Session = Depends(get_db),
) -> IssueStatsResponse:
    """Fetch breakdown metrics for issues."""
    stats = issue_service.get_stats(db=db)
    return IssueStatsResponse(**stats)


@router.post(
    "/seed",
    summary="Seed demo data",
    description="Populates the database with demo users, issues, and status history logs for hackathon demonstration.",
)
def seed_issues(
    force: bool = Query(False, description="Clear existing records and re-seed"),
    db: Session = Depends(get_db),
):
    """Seed synthetic demo civic issues and users."""
    count = seed_demo_data(db=db, force=force)
    return {
        "message": f"Successfully seeded {count} demo civic issues with audit trails.",
        "count": count,
    }


@router.get(
    "/{issue_id}",
    response_model=IssueResponse,
    summary="Get issue details",
    description="Retrieve complete issue details including geographic coordinates and complete status history audit logs.",
)
def get_issue(
    issue_id: int,
    db: Session = Depends(get_db),
) -> IssueResponse:
    """Fetch complete issue details and status history by ID."""
    issue = issue_service.get_by_id(db=db, issue_id=issue_id)
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Issue with ID {issue_id} not found",
        )
    return issue


@router.patch(
    "/{issue_id}/status",
    response_model=IssueResponse,
    summary="Update issue status (Admin)",
    description="Allows administrators to transition issue status, priority, and automatically record an IssueUpdate history record.",
)
def update_issue_status(
    issue_id: int,
    status_in: IssueStatusUpdate,
    db: Session = Depends(get_db),
) -> IssueResponse:
    """Update issue status and log update."""
    issue = issue_service.get_by_id(db=db, issue_id=issue_id)
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Issue with ID {issue_id} not found",
        )
    return issue_service.update_status(db=db, db_issue=issue, status_in=status_in)


@router.post(
    "/{issue_id}/updates",
    response_model=IssueUpdateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add an update/comment to an issue",
    description="Appends a progress note or status comment to the issue's audit trail.",
)
def add_issue_update(
    issue_id: int,
    update_in: IssueUpdateCreate,
    db: Session = Depends(get_db),
) -> IssueUpdateResponse:
    """Add a progress update record to an issue."""
    issue = issue_service.get_by_id(db=db, issue_id=issue_id)
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Issue with ID {issue_id} not found",
        )
    return issue_service.add_update(db=db, db_issue=issue, update_in=update_in)


@router.put(
    "/{issue_id}",
    response_model=IssueResponse,
    summary="Update issue details",
    description="Update general information of an existing issue.",
)
def update_issue(
    issue_id: int,
    issue_in: IssueUpdateSchema,
    db: Session = Depends(get_db),
) -> IssueResponse:
    """Update issue attributes."""
    issue = issue_service.get_by_id(db=db, issue_id=issue_id)
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Issue with ID {issue_id} not found",
        )
    return issue_service.update(db=db, db_issue=issue, issue_in=issue_in)


@router.delete(
    "/{issue_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an issue",
    description="Remove an issue and its cascade update history.",
)
def delete_issue(
    issue_id: int,
    db: Session = Depends(get_db),
):
    """Delete an issue by ID."""
    issue = issue_service.get_by_id(db=db, issue_id=issue_id)
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Issue with ID {issue_id} not found",
        )
    issue_service.delete(db=db, db_issue=issue)
    return None
