import os
import jwt

from dotenv import load_dotenv
from fastapi import HTTPException, Security, Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from jwt import InvalidTokenError

from src.database.database import get_db
from src.database.models import User

load_dotenv()

SECURITY_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"

bearer_scheme = HTTPBearer()

if not SECURITY_KEY:
    raise RuntimeError("Security Key Not Found")

def get_logged_user(credentials : HTTPAuthorizationCredentials = Depends(bearer_scheme) , db: Session = Depends(get_db) ):
    
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            SECURITY_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Authentication Token")

    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Or Expired Token", headers={"WWW-Authenticate": "Bearer"})

    try:
        user_id = int(user_id)
    except  (TypeError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Authentication Token")

    user = db.get(User, user_id)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User Not Found", headers={"WWW-Authenticate": "Bearer"})

    return user


    