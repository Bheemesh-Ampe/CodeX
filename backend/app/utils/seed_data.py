"""Synthetic demo dataset generator for CivicFix hackathon demonstration."""

from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.models.issue import Issue
from app.models.issue_update import IssueUpdate

DEMO_USERS = [
    {
        "name": "Alex Rivera",
        "email": "alex.resident@civicfix.org",
        "role": UserRole.RESIDENT.value,
    },
    {
        "name": "Sarah Connor",
        "email": "sarah.admin@civicfix.gov",
        "role": UserRole.ADMIN.value,
    },
    {
        "name": "Marcus Vance",
        "email": "marcus.works@civicfix.gov",
        "role": UserRole.ADMIN.value,
    },
]

DEMO_ISSUES = [
    {
        "title": "Severe Pothole on Elm Street",
        "description": "Deep tire-damaging pothole located right near the pedestrian crossing. Several cars have swerved dangerously to avoid it.",
        "category": "Road Damage",
        "status": "IN_PROGRESS",
        "priority": "HIGH",
        "latitude": 37.774929,
        "longitude": -122.419416,
        "address": "742 Elm Street, Downtown",
        "image_path": "https://images.unsplash.com/photo-1515162816999-a0c47dc192f7?auto=format&fit=crop&w=800&q=80",
        "ai_summary": "High-risk pothole hazard in high-traffic pedestrian crossing zone.",
        "ai_category": "Road Damage",
        "ai_priority": "HIGH",
        "ai_suggested_action": "Immediate cold mix asphalt patch within 24h.",
        "ai_status": "success",
    },
    {
        "title": "Flickering Streetlight Near Elementary School",
        "description": "The overhead street light on the corner has been flickering and completely goes out after 9 PM, creating unsafe walking conditions for families.",
        "category": "Street Light",
        "status": "REPORTED",
        "priority": "MEDIUM",
        "latitude": 37.783333,
        "longitude": -122.416667,
        "address": "450 Oak Avenue, Sunset District",
        "image_path": "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?auto=format&fit=crop&w=800&q=80",
        "ai_summary": "Flickering illumination near school safety corridor.",
        "ai_category": "Street Light",
        "ai_priority": "MEDIUM",
        "ai_suggested_action": "Dispatch municipal lighting technician for ballast inspection.",
        "ai_status": "success",
    },
    {
        "title": "Overflowing Public Garbage Dumpster",
        "description": "Public recycling and trash bins are overflowing onto the sidewalk. Attracting stray animals and generating foul odor.",
        "category": "Garbage/Waste",
        "status": "ACKNOWLEDGED",
        "priority": "MEDIUM",
        "latitude": 37.769040,
        "longitude": -122.446747,
        "address": "120 Market Street, Castro",
        "image_path": "https://images.unsplash.com/photo-1530587191325-3db32d826c18?auto=format&fit=crop&w=800&q=80",
        "ai_summary": "Sanitation backlog: Waste overflow in high foot-traffic zone.",
        "ai_category": "Garbage/Waste",
        "ai_priority": "MEDIUM",
        "ai_suggested_action": "Schedule emergency sanitation pickup route.",
        "ai_status": "success",
    },
    {
        "title": "Broken Water Main Leaking onto Roadway",
        "description": "Clean water is gushing from an underground pipe crack and flooding the right-hand lane. Pressure has reduced in nearby homes.",
        "category": "Water Leakage",
        "status": "IN_PROGRESS",
        "priority": "HIGH",
        "latitude": 37.755800,
        "longitude": -122.422500,
        "address": "88 Mission Blvd, Mission District",
        "image_path": "https://images.unsplash.com/photo-1584467735815-f778f274e296?auto=format&fit=crop&w=800&q=80",
        "ai_summary": "Critical infrastructure failure: Water main rupture with roadway flood risk.",
        "ai_category": "Water Leakage",
        "ai_priority": "HIGH",
        "ai_suggested_action": "Immediate water isolation valve closure and emergency pipe repair team dispatch.",
        "ai_status": "success",
    },
    {
        "title": "Obscured Stop Sign by Overgrown Branches",
        "description": "A stop sign at the intersection is completely hidden by tree branches, causing near-miss collisions every morning.",
        "category": "Public Safety",
        "status": "RESOLVED",
        "priority": "HIGH",
        "latitude": 37.790100,
        "longitude": -122.401000,
        "address": "Intersection of Pine & Taylor St",
        "image_path": "https://images.unsplash.com/photo-1448375240586-882707db888b?auto=format&fit=crop&w=800&q=80",
        "ai_summary": "Traffic safety hazard: Obscured regulatory signage at intersection.",
        "ai_category": "Public Safety",
        "ai_priority": "HIGH",
        "ai_suggested_action": "Trim foliage obstructing line of sight to stop sign.",
        "ai_status": "success",
    },
    {
        "title": "Damaged Playground Swing at Memorial Park",
        "description": "One of the child swings has a snapped chain and exposed sharp metal edges. Hazard for young children.",
        "category": "Public Safety",
        "status": "REPORTED",
        "priority": "LOW",
        "latitude": 37.769900,
        "longitude": -122.486200,
        "address": "Golden Gate Memorial Playground",
        "image_path": "https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?auto=format&fit=crop&w=800&q=80",
        "ai_summary": "Park playground equipment damage presenting minor hazard to children.",
        "ai_category": "Public Safety",
        "ai_priority": "LOW",
        "ai_suggested_action": "Replace swing seat and chain assembly during weekly park round.",
        "ai_status": "success",
    },
]


def seed_demo_data(db: Session, force: bool = False) -> int:
    """
    Seed demo users, issues, and audit update logs if empty or if forced.
    Returns the number of seeded issues.
    """
    existing_issues_count = db.query(Issue).count()
    if existing_issues_count > 0 and not force:
        return 0

    if force:
        db.query(IssueUpdate).delete()
        db.query(Issue).delete()
        db.query(User).delete()
        db.commit()

    # 1. Seed Users
    user_map = {}
    for user_data in DEMO_USERS:
        existing = db.query(User).filter(User.email == user_data["email"]).first()
        if not existing:
            user = User(**user_data)
            db.add(user)
            db.commit()
            db.refresh(user)
            user_map[user.email] = user
        else:
            user_map[existing.email] = existing

    resident_user = user_map.get("alex.resident@civicfix.org")
    admin_user = user_map.get("sarah.admin@civicfix.gov")
    inspector_user = user_map.get("marcus.works@civicfix.gov")

    # 2. Seed Issues and their IssueUpdate audit trails
    created_count = 0
    for issue_data in DEMO_ISSUES:
        issue = Issue(
            **issue_data,
            created_by=resident_user.id if resident_user else None,
            assigned_to=inspector_user.id if (inspector_user and issue_data["status"] != "REPORTED") else None,
        )
        db.add(issue)
        db.commit()
        db.refresh(issue)
        created_count += 1

        # Initial reported update
        initial_update = IssueUpdate(
            issue_id=issue.id,
            status="REPORTED",
            comment="Issue reported by resident.",
            updated_by=resident_user.id if resident_user else None,
        )
        db.add(initial_update)

        # Subsequent status updates for realistic demo history
        if issue.status in ["ACKNOWLEDGED", "IN_REVIEW", "IN_PROGRESS", "RESOLVED"]:
            ack_update = IssueUpdate(
                issue_id=issue.id,
                status="ACKNOWLEDGED",
                comment="City Works reviewed and acknowledged the report.",
                updated_by=admin_user.id if admin_user else None,
            )
            db.add(ack_update)

        if issue.status in ["IN_PROGRESS", "RESOLVED"]:
            progress_update = IssueUpdate(
                issue_id=issue.id,
                status="IN_PROGRESS",
                comment="Maintenance crew assigned and dispatched to location.",
                updated_by=inspector_user.id if inspector_user else None,
            )
            db.add(progress_update)

        if issue.status == "RESOLVED":
            resolved_update = IssueUpdate(
                issue_id=issue.id,
                status="RESOLVED",
                comment="Repairs completed and verified by site inspector.",
                updated_by=inspector_user.id if inspector_user else None,
            )
            db.add(resolved_update)

        db.commit()

    return created_count


# Backwards compatibility alias
DEMO_REPORTS = DEMO_ISSUES
