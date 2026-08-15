"""Backwards compatibility router: aliases /api/reports to /api/issues."""

from typing import List
from fastapi import APIRouter, status
from app.routes import issues

router = APIRouter(prefix="/reports", tags=["Reports (Legacy Alias)"])

# Re-mount issue route handlers with /reports prefix
router.add_api_route("", issues.create_issue, methods=["POST"], response_model=issues.IssueResponse, status_code=status.HTTP_201_CREATED)
router.add_api_route("", issues.list_issues, methods=["GET"], response_model=issues.IssueListResponse)
router.add_api_route("/stats/summary", issues.get_stats_summary, methods=["GET"], response_model=issues.IssueStatsResponse)
router.add_api_route("/seed", issues.seed_issues, methods=["POST"])
router.add_api_route("/{issue_id}", issues.get_issue, methods=["GET"], response_model=issues.IssueResponse)
router.add_api_route("/{issue_id}/status", issues.update_issue_status, methods=["PATCH"], response_model=issues.IssueResponse)
router.add_api_route("/{issue_id}", issues.update_issue, methods=["PUT"], response_model=issues.IssueResponse)
router.add_api_route("/{issue_id}", issues.delete_issue, methods=["DELETE"], status_code=status.HTTP_204_NO_CONTENT)
