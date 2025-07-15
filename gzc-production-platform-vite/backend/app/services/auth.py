from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import msal
import jwt
import logging
from typing import Dict, Optional

from app.core.config import settings

logger = logging.getLogger(__name__)

# HTTP Bearer token scheme
security = HTTPBearer()


class MSALAuthenticator:
    def __init__(self):
        self.tenant_id = settings.AZURE_TENANT_ID
        self.client_id = settings.AZURE_CLIENT_ID
        
    def verify_token(self, token: str) -> Optional[Dict]:
        """
        Verify Azure AD token
        """
        try:
            # In production, you would validate the token properly with Azure AD
            # For now, we'll do basic JWT decoding without verification
            # This should be replaced with proper Azure AD token validation
            
            # Decode without verification (FOR DEVELOPMENT ONLY)
            decoded = jwt.decode(token, options={"verify_signature": False})
            
            # Basic validation
            if decoded.get("aud") != self.client_id:
                logger.warning("Token audience mismatch")
                return None
                
            if decoded.get("iss") != f"https://login.microsoftonline.com/{self.tenant_id}/v2.0":
                logger.warning("Token issuer mismatch")
                return None
            
            return decoded
            
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid token: {e}")
            return None
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return None


# Global authenticator instance
authenticator = MSALAuthenticator()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    """
    Dependency to get current authenticated user from token
    """
    try:
        token = credentials.credentials
        
        # Verify token
        user_data = authenticator.verify_token(token)
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[Dict]:
    """
    Optional authentication - returns None if no valid token
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None