"""Backwards-compatibility schemas mapping Report to Issue."""

from app.schemas.issue import (
    IssueStatus as ReportStatus,
    IssuePriority as ReportPriority,
    IssueBase as ReportBase,
    IssueCreate as ReportCreate,
    IssueUpdateSchema as ReportUpdate,
    IssueStatusUpdate as ReportStatusUpdate,
    IssueResponse as ReportResponse,
    IssueListResponse as ReportListResponse,
    IssueStatsResponse as ReportStatsResponse,
)

__all__ = [
    "ReportStatus",
    "ReportPriority",
    "ReportBase",
    "ReportCreate",
    "ReportUpdate",
    "ReportStatusUpdate",
    "ReportResponse",
    "ReportListResponse",
    "ReportStatsResponse",
]
