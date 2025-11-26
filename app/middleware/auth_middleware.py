from typing import Literal

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_token, is_token_blacklisted
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)


class AuthMiddleware:
    @staticmethod
    async def verify_token(
        credentials: HTTPAuthorizationCredentials,
        required_token_type: Literal["access", "refresh"],
        db: AsyncSession,
    ):
        token = credentials.credentials
        CREDENTIALS_EXCEPTION = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        payload = decode_token(token)
        jti = payload.get("jti")
        exp = payload.get("exp")
        token_type = payload.get("type")

        if not all([jti, exp, token_type]):
            raise CREDENTIALS_EXCEPTION

        if token_type != required_token_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )

        is_blacklsited = is_token_blacklisted(db, jti)
        if is_blacklsited == True:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if is_blacklsited == None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token ID",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return {"payload": payload, "jti": jti, "token_type": token_type, "exp": exp}

    @staticmethod
    async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db),
    ) -> User:
        # payload = decode_token(token)
        # if payload.get("type") != "access":
        #     raise HTTPException(
        #         status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type"
        #     )
        result = await AuthMiddleware.verify_token(credentials, "access", db)
        payload = result.get("payload")

        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )

        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
            )

        return user

    @staticmethod
    async def get_current_active_user(
        current_user: User = Depends(get_current_user),
    ) -> User:
        if not current_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not active",
            )
        return current_user

    @staticmethod
    async def get_current_user_optional(
        credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme_optional),
        db: AsyncSession = Depends(get_db),
    ) -> User | None:
        if not credentials.credentials:
            return None

        try:
            # payload = decode_token(token)
            # if payload.get("type") != "access":
            #     return None
            result = await AuthMiddleware.verify_token(credentials, "access", db)
            payload = result.get("payload")

            user_id: int = payload.get("sub")
            if user_id is None:
                return None

            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()

            return user
        except Exception:
            return None
