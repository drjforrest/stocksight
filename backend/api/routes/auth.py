from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from api.auth import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from api.schemas.auth import Token

router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
    responses={
        401: {"description": "Invalid credentials"},
        500: {"description": "Internal server error"}
    }
)

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Get an access token for authentication.
    
    This is a temporary implementation that accepts any username/password.
    In production, you should validate credentials against your user database.
    """
    # TODO: Implement proper user authentication
    # For now, accept any username/password for testing
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data.username},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"} 