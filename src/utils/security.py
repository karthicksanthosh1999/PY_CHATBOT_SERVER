import os
import jwt

from pwdlib import PasswordHash
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()

password_hash = PasswordHash.recommended()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

if SECRET_KEY is None:
    raise RuntimeError("JWT_SECRET_KEY is Not Found")


def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(password=plain_password, hash=hashed_password)

def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub" : str(user_id),
        "exp" : expire
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

