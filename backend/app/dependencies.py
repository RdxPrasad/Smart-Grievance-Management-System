from fastapi.security import HTTPAuthorizationCredentials
from fastapi import Depends , HTTPException , status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.auth import decode_access_token




bearer_scheme = HTTPBearer()


def get_current_user(
    credentials : HTTPAuthorizationCredentials = Depends(bearer_scheme) ,
    db : Session = Depends(get_db)
) ->User :

    token = credentials.credentials
    payload = decode_access_token(token)

    user_id = payload.get("sub") 

    if not user_id :
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid token: user ID missing"
        )
    
    try :
        user_id = int(user_id)
    except (ValueError,TypeError):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED ,
            detail = "Invalid user ID in token"
        )

    current_user = db.query(User).filter(User.id == user_id).first()

    if not current_user :
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED ,
            detail = "User not found"
        )

    return current_user


def require_role(*allowed_roles : str ):
    """
    Allows access only to users whose role is in allowed_roles.
    """
    allowed_roles = {
        role.lower().strip()

        for role in allowed_roles
    }

    def role_checker(
        current_user : User = Depends(get_current_user)
    ) -> User :

        if current_user.role.lower().strip() not in allowed_roles :
            raise HTTPException(
                status_code = status.HTTP_403_FORBIDDEN ,
                detail = "You do not have permission to perform this action"
            )
        return current_user

    return role_checker

