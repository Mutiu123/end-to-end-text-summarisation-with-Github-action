"""
JWT authentication module.
Provides token generation, verification, and FastAPI dependency for protected routes.
"""

import time
from typing import Any, Dict, Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from textSummarizer.config.settings import Settings, get_settings

security_scheme = HTTPBearer(auto_error=False)


def create_access_token(
    data: Dict[str, Any],
    settings: Settings = None,
) -> str:
    """Generate a JWT access token.

    Args:
        data: Payload data to encode in the token.
        settings: Application settings. Uses default if not provided.

    Returns:
        Encoded JWT string.
    """
    if settings is None:
        settings = get_settings()

    payload = data.copy()
    expire = time.time() + (settings.JWT_EXPIRATION_MINUTES * 60)
    payload.update({"exp": expire, "iat": time.time()})

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def verify_token(token: str, settings: Settings = None) -> Dict[str, Any]:
    """Verify and decode a JWT token.

    Args:
        token: The JWT token string.
        settings: Application settings.

    Returns:
        Decoded token payload.

    Raises:
        HTTPException: If token is invalid or expired.
    """
    if settings is None:
        settings = get_settings()

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    settings: Settings = Depends(get_settings),
) -> Dict[str, Any]:
    """FastAPI dependency to extract and verify the current user from JWT.

    Args:
        credentials: Bearer token credentials from the request.
        settings: Application settings.

    Returns:
        Decoded user payload from the token.

    Raises:
        HTTPException: If credentials are missing or invalid.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return verify_token(credentials.credentials, settings)


def validate_api_key(api_key: str, settings: Settings = None) -> bool:
    """Validate an API key against configured keys.

    Args:
        api_key: The API key to validate.
        settings: Application settings.

    Returns:
        True if the key is valid.
    """
    if settings is None:
        settings = get_settings()

    valid_keys = settings.api_keys_list
    if not valid_keys:
        return True
    return api_key in valid_keys
