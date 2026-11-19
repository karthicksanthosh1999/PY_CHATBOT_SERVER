from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from src.database.database import get_db
from src.schema.auth_schema import RegisterRequest, UserResponse, LoginRequest, TokenResponse
from src.services.auth_service import AuthService
from src.dependencies.auth_dependency import get_logged_user
from src.database.models import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

auth_service = AuthService()

@router.post("/login", response_model=TokenResponse, status_code=200)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    try:
        return auth_service.login(db, data)
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        ) from error

@router.post("/register", response_model=UserResponse, status_code=201)
def register_user(data: RegisterRequest, db: Session = Depends(get_db)):
    try:
        return auth_service.register(db, data)
    except ValueError as error:
        raise HTTPException(
            status_code=409,
            detail=str(error)
        ) from error

@router.get("/me", status_code=200)
def get_my_profile(current_user: User = Depends(get_logged_user)):
    return {
        "message" : "Authenticated Successfully",
        "user" : {
            "id" : current_user.id,
            "fullName": current_user.fullName,
            "email" : current_user.email,
            "mobile" : current_user.mobile
        }
    }

@router.get("/", response_model=list[UserResponse], status_code=200)
def get_all_user(db: Session = Depends(get_db)):
    try:
        users = auth_service.get_all_users(db)
        return users
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

@router.get("/{user_id}/users", response_model=UserResponse, status_code=200)
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    try:
        user = auth_service.get_user_by_id(db, user_id)
        return user
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

@router.get("/users", response_model=UserResponse, status_code=200)
def get_user_by_email(email: str, db: Session = Depends(get_db)):
    try:
        user = auth_service.get_user_by_email(db, email)
        return user
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

@router.delete("/{user_id}",status_code=200)
def delete_user_by_id(user_id: int, db: Session = Depends(get_db)):
    try:
        return auth_service.delete_user_by_id(db, user_id=user_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error