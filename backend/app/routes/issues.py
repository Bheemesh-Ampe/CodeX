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
    IssueListResponse,
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
    description="Allows residents to submit a new civic issue with coordinates, title, description, category, and photo path.",
)
def create_issue(
    issue_in: IssueCreate,
    db: Session = Depends(get_db),
) -> IssueResponse:
    """Create a new issue."""
    return issue_service.create(db=db, issue_in=issue_in)


@router.get(
    "",
    response_model=IssueListResponse,
    summary="List civic issues",
    description="Retrieve all reported issues with filters for status, category, priority, reporter, assignee, and search terms.",
)
def list_issues(
    status_filter: Optional[IssueStatus] = Query(None, alias="status", description="Filter by issue status"),
    category: Optional[str] = Query(None, description="Filter by category"),
    priority: Optional[IssuePriority] = Query(None, description="Filter by priority"),
    search: Optional[str] = Query(None, description="Search in title, description, or address"),
    created_by: Optional[int] = Query(None, description="Filter by resident user ID"),
    assigned_to: Optional[int] = Query(None, description="Filter by assigned staff/admin ID"),
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(100, ge=1, le=500, description="Page limit"),
    db: Session = Depends(get_db),
) -> IssueListResponse:
    """List issues matching query criteria."""
    items, total = issue_service.get_multi(
        db=db,
        status=status_filter.value if status_filter else None,
        category=category,
        priority=priority.value if priority else None,
        search=search,
        created_by=created_by,
        assigned_to=assigned_to,
        skip=skip,
        limit=limit,
    )
    return IssueListResponse(total=total, items=items)


@router.get(
    "/stats/summary",
    response_model=IssueStatsResponse,
    summary="Get issue statistics",
    description="Provides aggregated issue counts by status, category, and priority for admin dashboards.",
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
    description="Retrieve full details, creator, assignee, and complete update history for a specific issue.",
)
def get_issue(
    issue_id: int,
    db: Session = Depends(get_db),
) -> IssueResponse:
    """Fetch an issue by ID."""
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
