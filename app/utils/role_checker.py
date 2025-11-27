from fastapi import Depends, HTTPException, status
from app.utils.oauth2 import get_current_user

def RoleChecker(allowed_roles: list):
    def wrapper(current_user=Depends(get_current_user)):
        user_role = current_user["role"]

        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource"
            )
        return current_user
    return wrapper
