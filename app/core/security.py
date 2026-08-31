from datetime import UTC, datetime, timedelta
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from pwdlib import PasswordHash
from pydantic import BaseModel

from app.core.config import Settings, get_settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")
password_hash = PasswordHash.recommended()


class TokenPrincipal(BaseModel):
    username: str
    scopes: list[str] = []


def verify_password(plain_password: str, encoded_hash: str) -> bool:
    try:
        return password_hash.verify(plain_password, encoded_hash)
    except Exception:
        return False


def authenticate_user(username: str, password: str, settings: Settings) -> bool:
    if username != settings.app_user_username:
        # Deliberately perform one hash verification to reduce username timing signals.
        verify_password(password, settings.app_user_password_hash)
        return False
    return verify_password(password, settings.app_user_password_hash)


def create_access_token(
    subject: str,
    settings: Settings,
    scopes: list[str] | None = None,
) -> str:
    now = datetime.now(UTC)
    expires = now + timedelta(minutes=settings.access_token_expire_minutes)
    claims = {
        "sub": subject,
        "iat": now,
        "nbf": now,
        "exp": expires,
        "iss": settings.app_name,
        "aud": settings.app_name,
        "scope": " ".join(scopes or ["resume:generate"]),
    }
    return jwt.encode(claims, settings.jwt_secret, algorithm=settings.jwt_algorithm)


async def get_current_principal(
    token: Annotated[str, Depends(oauth2_scheme)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> TokenPrincipal:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired access token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
            audience=settings.app_name,
            issuer=settings.app_name,
        )
        username = payload.get("sub")
        scope_text = payload.get("scope", "")
        if not username:
            raise credentials_exception
        return TokenPrincipal(
            username=username,
            scopes=[s for s in scope_text.split(" ") if s],
        )
    except InvalidTokenError as exc:
        raise credentials_exception from exc


def require_scope(scope: str):
    async def dependency(
        principal: Annotated[TokenPrincipal, Depends(get_current_principal)],
    ) -> TokenPrincipal:
        if scope not in principal.scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required scope: {scope}",
            )
        return principal

    return dependency
