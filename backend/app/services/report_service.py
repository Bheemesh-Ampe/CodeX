"""Backwards compatibility alias: report_service aliases issue_service."""

from app.services.issue_service import issue_service, IssueService

# Alias for backwards compatibility
report_service = issue_service
ReportService = IssueService

__all__ = ["report_service", "ReportService", "issue_service", "IssueService"]
