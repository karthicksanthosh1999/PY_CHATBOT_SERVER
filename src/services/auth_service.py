from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from src.utils.security import hash_password, verify_password, create_access_token
from src.database.models import User

class AuthService:

    def register(self, db: Session, data):
        existing_user = db.query(User).filter(User.email == data.email).first()

        if existing_user:
            raise ValueError("User Already Registered")

        user = User(
            fullName=data.fullName,
            email=str(data.email).lower(),
            password_hash = hash_password(data.password),
            mobile = data.mobile
        )

        try:
            db.add(user)
            db.commit()
            db.refresh(user)
            
            return user
        except IntegrityError as error:
            db.rollback()
            raise ValueError("User Already Registered") from error
        except Exception:
            db.rollback()
            raise

    def login(self, db: Session, data):
        normalized_email = str(data.email).strip().lower()
        statement = select(User).where(User.email == normalized_email)
        user = db.scalar(statement)
        
        if not user:
            raise ValueError("Invalid email or password")

        is_password_valid = verify_password(data.password, user.password_hash)

        if not is_password_valid:
            raise ValueError("Invalid email or password")

        access_token = create_access_token(user.id)

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    
    def get_all_users(self, db: Session):
        
        statement = (
            select(User).order_by(User.created_at.desc())
        )

        conversations = db.scalars(statement).all()
        return conversations

    def get_user_by_id(self, db: Session, user_id: int):
        user = db.get(User, user_id)

        if user is None:
            raise ValueError("User Not Found")

        return user

    def get_user_by_email(self, db: Session, email: str):
        normalized_email = email.strip().lower()
        statement = select(User).where(User.email == normalized_email)
        user = db.execute(statement).scalar_one_or_none()

        if user is None:
            raise ValueError("User Not Found")

        return user

    def delete_user_by_id(self, db: Session, user_id: int):
        user = db.get(User, user_id)

        if user is None:
            raise ValueError("User Not Found")

        db.delete(user)
        db.commit()

        return {
            "message": "User Deleted Successfully"
        }


        

