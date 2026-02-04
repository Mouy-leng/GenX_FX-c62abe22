from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
try:
    from jose import JWTError, jwt
    JOSE_AVAILABLE = True
except ImportError:
    JOSE_AVAILABLE = False
    JWTError = Exception
    class _DummyJWT:
        def decode(self, *args, **kwargs):
            raise ImportError("python-jose library not installed")
    jwt = _DummyJWT()
from datetime import datetime, timedelta
from typing import Optional
import logging
import os

from ..config import settings

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=True)  # Changed to auto_error=True for security

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token - SECURE VERSION"""
    
    # SECURITY FIX: Remove authentication bypass for testing
    # Only allow testing bypass in development with explicit test mode
    if os.getenv("ENVIRONMENT") == "testing" and os.getenv("DISABLE_AUTH_FOR_TESTS") == "true":
        logger.warning("AUTHENTICATION DISABLED FOR TESTS - NOT FOR PRODUCTION!")
        return {"username": "testuser", "exp": None, "test_mode": True}
    
    # SECURITY: Require credentials in all cases
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # SECURITY: Check if JOSE library is available
    if not JOSE_AVAILABLE:
        logger.error("python-jose library not available - JWT validation disabled")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="JWT validation library not available",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # SECURITY: Validate secret key is properly configured
    if not settings.SECRET_KEY or settings.SECRET_KEY == "your-super-secret-key-change-this-in-production":
        logger.error("SECRET_KEY not properly configured")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server configuration error",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # SECURITY: Use proper algorithm validation
        algorithms = [settings.ALGORITHM] if hasattr(settings, 'ALGORITHM') else ['HS256']
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=algorithms)
        
        username: str = payload.get("sub")
        exp = payload.get("exp")
        
        # SECURITY: Validate username exists
        if username is None:
            logger.warning("JWT token missing username (sub claim)")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # SECURITY: Check token expiration
        if exp is not None:
            current_time = datetime.utcnow().timestamp()
            if current_time > exp:
                logger.warning(f"Expired token for user {username}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        
        logger.info(f"User {username} authenticated successfully")
        return {"username": username, "exp": exp}
        
    except JWTError as e:
        logger.error(f"JWT verification failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Unexpected error during authentication: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service error",
            headers={"WWW-Authenticate": "Bearer"},
        )
