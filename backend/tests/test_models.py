"""Tests for SQLAlchemy Database Models and Relationships."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.session import Base
from app.models.user import User, UserRole
from app.models.issue import Issue
from app.models.issue_update import IssueUpdate


@pytest.fixture
def db_session():
    """Create an in-memory SQLite database session for unit testing models."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)
    session = TestingSession()
    yield session
    session.close()


def test_user_creation(db_session):
    """Test creating resident and admin users."""
    resident = User(name="Alice Resident", email="alice@test.org", role=UserRole.RESIDENT.value)
    admin = User(name="Bob Admin", email="bob@test.gov", role=UserRole.ADMIN.value)
    db_session.add_all([resident, admin])
    db_session.commit()

    assert resident.id is not None
    assert resident.role == "resident"
    assert admin.id is not None
    assert admin.role == "admin"


def test_issue_relationships_and_defaults(db_session):
    """Test creating an issue with default status, priority, and relationships."""
    user = User(name="John Doe", email="john@test.org", role="resident")
    admin = User(name="Inspector Gadget", email="gadget@test.gov", role="admin")
    db_session.add_all([user, admin])
    db_session.commit()

    # Create issue with defaults
    issue = Issue(
        title="Pothole on 4th Ave",
        description="Deep pothole in middle lane",
        category="Pothole",
        latitude=37.7749,
        longitude=-122.4194,
        created_by=user.id,
        assigned_to=admin.id,
    )
    db_session.add(issue)
    db_session.commit()
    db_session.refresh(issue)

    # Verify defaults
    assert issue.status == "REPORTED"
    assert issue.priority == "MEDIUM"
    assert issue.creator.id == user.id
    assert issue.assignee.id == admin.id
    assert len(user.issues_created) == 1
    assert len(admin.issues_assigned) == 1


def test_issue_updates_relationship_and_cascade(db_session):
    """Test issue updates relationship and cascade deletion."""
    user = User(name="Jane Reporter", email="jane@test.org", role="resident")
    admin = User(name="Officer Smith", email="smith@test.gov", role="admin")
    db_session.add_all([user, admin])
    db_session.commit()

    issue = Issue(
        title="Broken Streetlight",
        description="Light is out completely",
        latitude=37.7800,
        longitude=-122.4200,
        created_by=user.id,
    )
    db_session.add(issue)
    db_session.commit()

    # Add issue updates
    update1 = IssueUpdate(
        issue_id=issue.id,
        status="REPORTED",
        comment="Submitted by resident",
        updated_by=user.id,
    )
    update2 = IssueUpdate(
        issue_id=issue.id,
        status="IN_PROGRESS",
        comment="Technician on way",
        updated_by=admin.id,
    )
    db_session.add_all([update1, update2])
    db_session.commit()
    db_session.refresh(issue)

    assert len(issue.updates) == 2
    assert issue.updates[0].status in ["REPORTED", "IN_PROGRESS"]

    # Delete issue and verify cascade deletion of issue_updates
    db_session.delete(issue)
    db_session.commit()

    remaining_updates = db_session.query(IssueUpdate).filter(IssueUpdate.issue_id == issue.id).count()
    assert remaining_updates == 0
