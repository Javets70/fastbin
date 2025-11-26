import uuid
from datetime import datetime, timedelta
from typing import Literal

import jwt
from fastapi import HTTPException, status
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models import Token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    new_password = password.encode("utf-8")
    return pwd_context.hash(new_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_token(
    data: dict,
    token_type: Literal["access", "refresh"],
    expires_delta: timedelta | None = None,
):
    to_encode = data.copy()
    now = datetime.now(datetime.UTC)
    if expires_delta:
        expire = now + timedelta
    elif token_type == "access":
        expire = now + timedelta(settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    else:
        expire = now + timedelta(settings.REFRESH_TOKEN_EXPIRE_DAYS)

    jti = uuid.uuid4()
    to_encode.update({"exp": expire, "iat": now, "type": token_type, "jti": jti})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )

    # token = Token(jti=jti, token_type=token_type, expires_at=expire, _metadata=data)
    # db.add(token)
    # db.commit()

    return encoded_jwt, jti, expire


def create_token_pair(
    db: AsyncSession,
    data: dict,
):
    # TODO HANDLE USER_ID / METADATA
    # USER_ID CAN BE NONE SO ACCOUNT FOR THAT
    access_token, access_jti, access_expire_at = create_token(data, "access")
    refresh_token, refresh_jti, refresh_expire_at = create_token(data, "refresh")

    access_token_record = Token(
        jti=access_jti,
        user_id=None,
        token_type="access",
        paired_jti=refresh_jti,
        expires_at=access_expire_at,
    )
    refresh_token_record = Token(
        jti=refresh_jti,
        user_id=None,
        token_type="refresh",
        paired_jti=access_jti,
        expires_at=refresh_expire_at,
    )

    db.add(access_token_record)
    db.add(refresh_token_record)
    db.commit()

    return access_token, refresh_token


def blacklist_token(db: AsyncSession, jti: uuid.UUID, reason: str = "Logged Out"):
    result = await db.execute(select(Token).where(Token.jti == jti))
    token = result.scalar_one_or_none()

    if token:
        token.is_blacklisted = True
        token.blacklisted_at = datetime.utcnow()
        token.blacklist_reason = reason
        db.commit()


def blacklist_token_pair(db: AsyncSession, jti: uuid.UUID, reason: str = "Logged Out"):
    result = await db.execute(select(Token).where(Token.jti == jti))
    token = result.scalar_one_or_none()

    if token:
        blacklist_token(db, jti, reason)

        if token.paired_jti:
            blacklist_token(db, token.paired_jti, reason)


def is_token_blacklisted(db: AsyncSession, jti: uuid.UUID) -> bool | None:
    result = await db.execute(select(Token).where(Token.jti == jti))
    token = result.scalar_one_or_none()

    if token:
        return token.is_blacklisted


def cleanup_expired_token(db: AsyncSession):
    result = await db.execute(
        select(Token).where(Token.expires_at < datetime.now(dateime.UTC))
    )
    tokens = result.all()

    db.delete(tokens)
    db.commit()


# def create_access_token(data: dict, expires_delta: timedelta | None = None):
#     to_encode = data.copy()

#     if expires_delta:
#         expire = datetime.now(timezone.utc) + expires_delta
#     else:
#         expire = datetime.now(timezone.utc) + timedelta(
#             minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
#         )

#     to_encode.update(
#         {"exp": expire, "iat": datetime.now(timezone.utc), "type": "access"}
#     )
#     encoded_jwt = jwt.encode(
#         to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
#     )
#     return encoded_jwt


# def create_refresh_token(data: dict):
#     to_encode = data.copy()

#     expire = datetime.now(timezone.utc) + timedelta(
#         minutes=settings.REFRESH_TOKEN_EXPIRE_DAYS
#     )

#     to_encode.update(
#         {"exp": expire, "iat": datetime.now(timezone.utc), "type": "refresh"}
#     )
#     encoded_jwt = jwt.encode(
#         to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
#     )
#     return encoded_jwt


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
