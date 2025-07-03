"""Authentication endpoints for Google OAuth."""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from typing import Dict, Any
import logging

from app.services.google_calendar import calendar_service

logger = logging.getLogger(__name__)
router = APIRouter()

# Simple in-memory storage for demo (use Redis/database in production)
user_tokens = {}


@router.get("/google/login")
async def google_login() -> Dict[str, str]:
    """Initiate Google OAuth flow."""
    try:
        auth_url = calendar_service.get_auth_url()
        return {
            "auth_url": auth_url,
            "message": "Visit the auth_url to authorize calendar access"
        }
    except Exception as e:
        logger.error(f"Error generating auth URL: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/google/callback")
async def google_callback(code: str) -> Dict[str, Any]:
    """Handle Google OAuth callback."""
    try:
        # Exchange code for tokens
        token_data = calendar_service.exchange_code_for_tokens(code)
        
        # Store tokens (use proper user management in production)
        user_id = "demo_user"  # In production, get from JWT or session
        user_tokens[user_id] = token_data
        
        logger.info("Google OAuth successful for user")
        
        return {
            "message": "Google Calendar connected successfully!",
            "status": "success",
            "user_id": user_id
        }
        
    except Exception as e:
        logger.error(f"OAuth callback error: {e}")
        raise HTTPException(status_code=400, detail=f"OAuth failed: {str(e)}")


@router.get("/google/status")
async def google_auth_status() -> Dict[str, Any]:
    """Check if user has authorized Google Calendar access."""
    user_id = "demo_user"  # In production, get from JWT
    
    has_tokens = user_id in user_tokens
    
    return {
        "authorized": has_tokens,
        "user_id": user_id if has_tokens else None,
        "message": "Google Calendar connected" if has_tokens else "Please authorize Google Calendar access"
    }