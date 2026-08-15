"""Backwards-compatibility alias: Report is an alias of Issue."""

from app.models.issue import Issue

# Backward-compatibility alias
Report = Issue

__all__ = ["Report", "Issue"]
