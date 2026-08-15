"""Service layer for Issue operations."""

from typing import List, Optional, Tuple, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from app.models.issue import Issue
from app.models.issue_update import IssueUpdate
from app.schemas.issue import IssueCreate, IssueUpdateSchema, IssueStatusUpdate
from app.schemas.issue_update import IssueUpdateCreate


class IssueService:
    """Service layer handling database operations for Issues and IssueUpdates."""

    def create(self, db: Session, issue_in: IssueCreate) -> Issue:
        """
        Create and persist a new civic issue with status=REPORTED and default priority=MEDIUM.
        Creates an initial IssueUpdate record to track the issue's lifecycle from inception.
        """
        issue_data = issue_in.model_dump(exclude={"image"})

        # Map image to image_path if provided
        if issue_in.image and not issue_data.get("image_path"):
            issue_data["image_path"] = issue_in.image

        # Priority defaults to MEDIUM until AI analysis is implemented
        if "priority" in issue_data and issue_data["priority"] is not None:
            if hasattr(issue_data["priority"], "value"):
                issue_data["priority"] = issue_data["priority"].value
            elif not str(issue_data["priority"]).strip():
                issue_data["priority"] = "MEDIUM"
        else:
            issue_data["priority"] = "MEDIUM"

        # Explicitly set status to REPORTED per Prompt 3 requirements
        issue_data["status"] = "REPORTED"

        db_issue = Issue(**issue_data)
        db.add(db_issue)
        db.commit()
        db.refresh(db_issue)

        # Create initial audit history update record
        initial_update = IssueUpdate(
            issue_id=db_issue.id,
            status="REPORTED",
            comment="Issue reported by resident.",
            updated_by=db_issue.created_by,
        )
        db.add(initial_update)
        db.commit()
        db.refresh(db_issue)

        return db_issue

    def get_by_id(self, db: Session, issue_id: int) -> Optional[Issue]:
        """Fetch a single issue by ID with related creator, assignee, and status history updates."""
        return db.query(Issue).filter(Issue.id == issue_id).first()

    def get_multi(
        self,
        db: Session,
        status: Optional[str] = None,
        category: Optional[str] = None,
        priority: Optional[str] = None,
        search: Optional[str] = None,
        created_by: Optional[int] = None,
        assigned_to: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[Issue], int]:
        """Fetch issues matching search and filter criteria with pagination."""
        query = db.query(Issue)

        if status:
            query = query.filter(func.upper(Issue.status) == status.strip().upper())
        if category:
            query = query.filter(func.lower(Issue.category) == category.strip().lower())
        if priority:
            query = query.filter(func.upper(Issue.priority) == priority.strip().upper())
        if created_by:
            query = query.filter(Issue.created_by == created_by)
        if assigned_to:
            query = query.filter(Issue.assigned_to == assigned_to)
        if search:
            pattern = f"%{search.strip()}%"
            query = query.filter(
                (Issue.title.ilike(pattern))
                | (Issue.description.ilike(pattern))
                | (Issue.address.ilike(pattern))
            )

        total = query.count()
        items = query.order_by(Issue.created_at.desc()).offset(skip).limit(limit).all()
        return items, total

    def update(self, db: Session, db_issue: Issue, issue_in: IssueUpdateSchema) -> Issue:
        """Update fields of an existing issue."""
        update_data = issue_in.model_dump(exclude_unset=True, exclude={"image"})
        if issue_in.image and not update_data.get("image_path"):
            update_data["image_path"] = issue_in.image

        for field, value in update_data.items():
            if hasattr(db_issue, field):
                if hasattr(value, "value"):
                    value = value.value
                setattr(db_issue, field, value)

        db.commit()
        db.refresh(db_issue)
        return db_issue

    def update_status(
        self, db: Session, db_issue: Issue, status_in: IssueStatusUpdate
    ) -> Issue:
        """
        Update the issue status (and optionally priority), and log an IssueUpdate entry.
        """
        new_status = status_in.status.value if hasattr(status_in.status, "value") else str(status_in.status)
        db_issue.status = new_status

        if status_in.priority:
            new_priority = status_in.priority.value if hasattr(status_in.priority, "value") else str(status_in.priority)
            db_issue.priority = new_priority

        # Create history record
        audit_update = IssueUpdate(
            issue_id=db_issue.id,
            status=new_status,
            comment=status_in.comment or f"Status updated to {new_status}",
            updated_by=status_in.updated_by,
        )
        db.add(audit_update)
        db.commit()
        db.refresh(db_issue)
        return db_issue

    def add_update(
        self, db: Session, db_issue: Issue, update_in: IssueUpdateCreate
    ) -> IssueUpdate:
        """Add an explicit progress update/comment to an issue."""
        new_update = IssueUpdate(
            issue_id=db_issue.id,
            status=update_in.status,
            comment=update_in.comment,
            updated_by=update_in.updated_by,
        )
        if update_in.status and update_in.status != db_issue.status:
            db_issue.status = update_in.status

        db.add(new_update)
        db.commit()
        db.refresh(new_update)
        return new_update

    def delete(self, db: Session, db_issue: Issue) -> None:
        """Delete an issue and its cascade updates."""
        db.delete(db_issue)
        db.commit()

    def get_stats(self, db: Session) -> Dict:
        """Aggregate breakdown metrics grouped by status, category, and priority."""
        total_issues = db.query(Issue).count()

        # Group by status
        status_counts = (
            db.query(Issue.status, func.count(Issue.id)).group_by(Issue.status).all()
        )
        by_status = {status: count for status, count in status_counts}

        # Group by category
        category_counts = (
            db.query(Issue.category, func.count(Issue.id)).group_by(Issue.category).all()
        )
        by_category = {cat: count for cat, count in category_counts}

        # Group by priority
        priority_counts = (
            db.query(Issue.priority, func.count(Issue.id)).group_by(Issue.priority).all()
        )
        by_priority = {prio: count for prio, count in priority_counts}

        return {
            "total_issues": total_issues,
            "by_status": by_status,
            "by_category": by_category,
            "by_priority": by_priority,
        }


issue_service = IssueService()
