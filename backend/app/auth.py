import os
from uuid import UUID

import httpx
from dotenv import load_dotenv
from fastapi import Depends , HTTPException
from fastapi.security import HTTPAuthorizationCredentials , HTTPBearer
from jose import jwt , jwk
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")

security =  HTTPBearer()



def get_current_user(
    credentials : HTTPAuthorizationCredentials = Depends(security) ,
    db : Session = Depends(get_db)
) :
    token = credentials.credentials

    header = jwt.get_unverified_header(token)
    kid = header.get("kid")

    if not kid :
        raise HTTPException(
            status_code=401 ,
            detail="Invalid token"
        )

    jwks_url = f"{SUPABASE_URL}/auth/v1/.well-known/jwks.json"

    response = httpx.get(jwks_url)

    if response.status_code != 200:
        raise HTTPException(
            status_code=401,
            detail="Unable to verify token"
        )

    jwks = response.json()

    key = next(
    (key for key in jwks["keys"] if key["kid"] == kid),
    None
    )

    if not key:
        raise HTTPException(
            status_code=401,
            detail="Invalid token key"
        )

    public_key = jwk.construct(key)

    payload = jwt.decode(
        token,
        public_key,
        algorithms=["ES256"],
        audience="authenticated",
        issuer=f"{SUPABASE_URL}/auth/v1"
    )

    auth_user_id = payload.get("sub")

    if not auth_user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    user = db.query(User).filter(
    User.auth_user_id == UUID(auth_user_id)
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Application user not found"
        )

    return user


def require_admin(
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    return current_user


def require_staff(
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["staff", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="Staff access required"
        )

    return current_user


def require_student(
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "student":
        raise HTTPException(
            status_code=403,
            detail="Student access required"
        )

    return current_user