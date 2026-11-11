from dotenv import load_dotenv
import os
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import JWTError, jwt 
from fastapi import HTTPException , status


# ----------------------------------------------------------------------

# 1. Create the CryptContext object
pwd_context  = CryptContext(schemes=["bcrypt"], deprecated="auto")


# 2. Function to Hash a Password
"""Takes a plain text password and returns its secure bcrypt hash."""
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# 3. Function to Verify a Password
"""Checks whether a plain text password matches the stored bcrypt hash."""
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# ----------------------------------------------------------------------
load_dotenv()
JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")

if not JWT_SECRET_KEY :
    raise EnvironmentError(
        "JWT_SECRET_KEY not found in environment. "
        "Add it to .env and restart the application."
    )

ALGORITHM : str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES : int = 60 


# Creating the signed access token.
def create_access_token(
    data : Dict[str,Any] ,
    expires_delta : Optional[timedelta] = None
) -> str :
    to_encode = data.copy() 
    if "sub" in to_encode :
        to_encode["sub"] = str(to_encode["sub"])
        
    now = datetime.now(timezone.utc)

    expire = now + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

    to_encode.update(
        {
            "exp" : expire
        }
    )

    encode_jwt = jwt.encode(
        to_encode ,
        JWT_SECRET_KEY ,
        algorithm=ALGORITHM
    )

    return encode_jwt



# Decoding the access token
def decode_access_token(token : str) -> Dict[str,Any]:

    try :
        payload = jwt.decode(
            token ,
            JWT_SECRET_KEY ,
            algorithms=[ALGORITHM]
        )

        return payload 

    except JWTError as exc :
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Could not validate credentials"
        ) from exc 




