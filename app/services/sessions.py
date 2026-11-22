from datetime import UTC, datetime, timedelta

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from app.config import settings
from app.models import User, UserSession
from app.schemas.auth import LoginInput
from app.security import (
    DUMMY_PASSWORD_HASH,
    generate_session_token,
    hash_session_token,
    verify_password,
)
from app.services.users import find_user_by_email


class InvalidCredentialsError(Exception):
    pass


async def authenticate_user(
    session: AsyncSession,
    data: LoginInput,
) -> User:
    user = await find_user_by_email(session, str(data.email))
    password_hash = user.password_hash if user else DUMMY_PASSWORD_HASH

    is_valid = await run_in_threadpool(
        verify_password,
        data.password,
        password_hash,
    )

    if user is None or not is_valid:
        raise InvalidCredentialsError()

    return user


async def create_user_session(
    session: AsyncSession,
    user: User,
) -> str:
    token = generate_session_token()

    session.add(
        UserSession(
            user_id=user.id,
            token_hash=hash_session_token(token),
            expires_at=datetime.now(UTC)
            + timedelta(days=settings.session_lifetime_days),
        )
    )
    await session.commit()

    return token


async def get_user_by_session_token(
    session: AsyncSession,
    token: str,
) -> User | None:
    result = await session.execute(
        select(User)
        .join(UserSession, UserSession.user_id == User.id)
        .where(
            UserSession.token_hash == hash_session_token(token),
            UserSession.expires_at > datetime.now(UTC),
        )
    )
    return result.scalar_one_or_none()


async def delete_user_session(
    session: AsyncSession,
    token: str,
) -> None:
    await session.execute(
        delete(UserSession).where(
            UserSession.token_hash == hash_session_token(token)
        )
    )
    await session.commit()