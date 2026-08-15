"""API routes for Municipal Administrators (Prompt 6)."""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.issue import (
    IssueStatusUpdate,
    IssueResponse,
    IssueStatsResponse,
    IssueStatus,
    IssuePriority,
)
from app.schemas.issue_update import IssueUpdateCreate, IssueUpdateResponse
from app.services.issue_service import issue_service

router = APIRouter(prefix="/admin", tags=["Administrator"])


@router.get(
    "/stats",
    response_model=IssueStatsResponse,
    summary="Get issue statistics (Administrator)",
    description="Provides aggregated issue counts by status, category, and priority.",
)
def admin_get_stats(
    db: Session = Depends(get_db),
) -> IssueStatsResponse:
    """Fetch breakdown metrics for issues."""
    stats = issue_service.get_stats(db=db)
    return IssueStatsResponse(**stats)


@router.get(
    "/issues",
    response_model=List[IssueResponse],
    summary="List issues for administrator review",
    description="Retrieve all reported issues with filtering by status, category, and priority for admin triage.",
)
def admin_list_issues(
    status: Optional[str] = Query(None, description="Filter by issue status (e.g. REPORTED, ACKNOWLEDGED, IN_PROGRESS, RESOLVED, REJECTED)"),
    category: Optional[str] = Query(None, description="Filter by category (e.g. Road Damage, Street Light)"),
    priority: Optional[str] = Query(None, description="Filter by priority (e.g. LOW, MEDIUM, HIGH)"),
    search: Optional[str] = Query(None, description="Search in title, description, or address"),
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(100, ge=1, le=500, description="Max issues to return"),
    db: Session = Depends(get_db),
) -> List[IssueResponse]:
    """Retrieve issues with optional admin filters."""
    items, _ = issue_service.get_multi(
        db=db,
        status=status,
        category=category,
        priority=priority,
        search=search,
        skip=skip,
        limit=limit,
    )
    return items


@router.get(
    "/issues/{issue_id}",
    response_model=IssueResponse,
    summary="Get complete issue details for administrator",
    description="Retrieve complete issue details including image, latitude, longitude, AI analysis, current status, and full status history.",
)
def admin_get_issue(
    issue_id: int,
    db: Session = Depends(get_db),
) -> IssueResponse:
    """Fetch complete issue record by ID for admin inspection."""
    issue = issue_service.get_by_id(db=db, issue_id=issue_id)
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Issue with ID {issue_id} not found",
        )
    return issue


@router.patch(
    "/issues/{issue_id}/status",
    response_model=IssueResponse,
    summary="Update issue status (Administrator)",
    description="Update issue status, update timestamp, create an IssueUpdate audit log, and store administrator comment.",
)
def admin_update_issue_status(
    issue_id: int,
    status_in: IssueStatusUpdate,
    db: Session = Depends(get_db),
) -> IssueResponse:
    """Transition issue status with audit trail logging."""
    issue = issue_service.get_by_id(db=db, issue_id=issue_id)
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Issue with ID {issue_id} not found",
        )
    return issue_service.update_status(db=db, db_issue=issue, status_in=status_in)


@router.post(
    "/issues/{issue_id}/updates",
    response_model=IssueUpdateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add progress update/comment to issue (Administrator)",
    description="Appends an administrative comment or progress note to the issue's audit trail.",
)
def admin_add_issue_update(
    issue_id: int,
    update_in: IssueUpdateCreate,
    db: Session = Depends(get_db),
) -> IssueUpdateResponse:
    """Append a status update note from administrator."""
    issue = issue_service.get_by_id(db=db, issue_id=issue_id)
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Issue with ID {issue_id} not found",
        )
    if update_in.updated_by is None:
        update_in.updated_by = 1
    return issue_service.add_update(db=db, db_issue=issue, update_in=update_in)
