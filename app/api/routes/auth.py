from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from app.core.config import Settings, get_settings
from app.core.security import authenticate_user, create_access_token

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_seconds: int


@router.post("/token", response_model=TokenResponse)
async def issue_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    settings: Annotated[Settings, Depends(get_settings)],
) -> TokenResponse:
    if not authenticate_user(form_data.username, form_data.password, settings):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(
        subject=form_data.username,
        settings=settings,
        scopes=["resume:generate"],
    )
    return TokenResponse(
        access_token=token,
        expires_in_seconds=settings.access_token_expire_minutes * 60,
    )
