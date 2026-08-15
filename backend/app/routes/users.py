"""API routes for Users."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.user import UserCreate, UserResponse, UserRole
from app.services.user_service import user_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    description="Registers a resident or administrator for the hackathon demo.",
)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
) -> UserResponse:
    """Create a new user."""
    existing = user_service.get_by_email(db=db, email=user_in.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists.",
        )
    return user_service.create(db=db, user_in=user_in)


@router.get(
    "",
    response_model=List[UserResponse],
    summary="List users",
    description="List all registered residents and administrators.",
)
def list_users(
    role: Optional[UserRole] = Query(None, description="Filter by user role"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> List[UserResponse]:
    """Retrieve users list."""
    return user_service.get_multi(
        db=db,
        role=role.value if role else None,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID",
    description="Retrieve profile details of a specific user.",
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
) -> UserResponse:
    """Fetch user by ID."""
    user = user_service.get_by_id(db=db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )
    return user
