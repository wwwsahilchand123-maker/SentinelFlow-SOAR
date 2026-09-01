from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from app.database import get_db
from app.models.user import User, RoleEnum
from app.schemas.user import UserLogin, Token, UserResponse, UserCreate
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.dependencies import get_current_user, require_role
from app.services.audit_service import AuditService

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=Token)
def login(user_login: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user with username/password and return JWT token"""
    user = db.query(User).filter(User.username == user_login.username).first()
    
    if not user or not verify_password(user_login.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )
    
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.value if hasattr(user.role, "value") else str(user.role)}
    )
    
    audit_service = AuditService(db)
    audit_service.log_action(
        user_id=user.id,
        action="USER_LOGIN_SUCCESS",
        resource="auth",
        resource_id=str(user.id),
        result="Success"
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Return currently authenticated user profile"""
    return current_user

@router.post("/register", response_model=UserResponse)
def register_user(
    user_create: UserCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_role([RoleEnum.ADMIN]))
):
    """Admin-only: Provision a new SOC user"""
    existing_user = db.query(User).filter(
        (User.username == user_create.username) | (User.email == user_create.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists"
        )
    
    new_user = User(
        username=user_create.username,
        email=user_create.email,
        full_name=user_create.full_name,
        role=user_create.role,
        hashed_password=get_password_hash(user_create.password),
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    audit_service = AuditService(db)
    audit_service.log_action(
        user_id=admin_user.id,
        action="USER_PROVISIONED",
        resource="user",
        resource_id=str(new_user.id),
        result="Success",
        metadata={"created_username": new_user.username, "role": str(new_user.role)}
    )
    
    return new_user
