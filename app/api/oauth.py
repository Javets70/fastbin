from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_token, create_token_pair
from app.models import User

router = APIRouter()

oauth = OAuth()

# oauth.register(
#     name="github",
#     client_id=settings.GITHUB_CLIENT_ID,
#     client_secret=settings.GITHUB_CLIENT_SECRET,
#     authorize_url="https://github.com/login/oauth/authorize",
#     access_token_url="https://github.com/login/oauth/access_token",
#     api_base_url="https://api.github.com/",
#     client_kwargs={"scope": "user:email"},
# )

oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


# @router.get("/github/login")
# async def github_login(request: Request):
#     """
#     Redirect to GitHub OAuth
#     """
#     if not settings.GITHUB_CLIENT_ID or not settings.GITHUB_CLIENT_SECRET:
#         raise HTTPException(status_code=500, detail="GitHub OAuth not configured")

#     redirect_uri = f"{settings.FRONTEND_URL}/oauth/github/callback"
#     return await oauth.github.authorize_redirect(request, redirect_uri)


# @router.get("/github/callback")
# async def github_callback(request: Request, db: AsyncSession = Depends(get_db)):
#     """
#     GitHub OAuth callback handler
#     """
#     try:
#         token = await oauth.github.authorize_access_token(request)
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"OAuth error: {str(e)}")

#     # Get user info from GitHub
#     resp = await oauth.github.get("user", token=token)
#     user_data = resp.json()

#     # Get primary email
#     email = user_data.get("email")
#     if not email:
#         # Fetch emails if not in profile
#         resp = await oauth.github.get("user/emails", token=token)
#         emails = resp.json()
#         primary_email = next((e["email"] for e in emails if e["primary"]), None)
#         email = primary_email or emails[0]["email"]

#     # Check if user exists
#     result = await db.execute(select(User).where(User.email == email))
#     user = result.scalar_one_or_none()

#     if not user:
#         # Create new user (OAuth users don't have password)
#         user = User(
#             email=email,
#             hashed_password="",  # OAuth users don't need password
#         )
#         db.add(user)
#         await db.commit()
#         await db.refresh(user)

#     # Create tokens
#     access_token = create_access_token(data={"sub": user.id})
#     refresh_token = create_refresh_token(data={"sub": user.id})

#     # Redirect to frontend with tokens (adjust as needed)
#     return RedirectResponse(
#         url=f"{settings.FRONTEND_URL}/auth/callback?access_token={access_token}&refresh_token={refresh_token}"
#     )


@router.get("/google/login")
async def google_login(request: Request):
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="Google OAuth not configured")

    redirect_uri = f"{settings.FRONTEND_URL}/oauth/google/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback")
async def google_callback(request: Request, db: AsyncSession = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"OAuth error: {str(e)}")

    user_info = token.get("userinfo")
    if not user_info:
        raise HTTPException(status_code=400, detail="Failed to get user info")

    email = user_info.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email not provided by Google")

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            email=email,
            hashed_password="",
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    # Create tokens
    # access_token = create_access_token(data={"sub": user.id})
    # refresh_token = create_refresh_token(data={"sub": user.id})
    access_token, refresh_token = create_token_pair(db=db, data={"sub": user.id})

    # Redirect to frontend with tokens
    return RedirectResponse(
        url=f"{settings.FRONTEND_URL}/auth/callback?access_token={access_token}&refresh_token={refresh_token}"
    )
