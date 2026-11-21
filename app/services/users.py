from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from app.models import User
from app.schemas.auth import RegisterInput
from app.security import hash_password


class EmailAlreadyRegisteredError(Exception):
    pass


async def find_user_by_email(
    session: AsyncSession,
    email: str,
) -> User | None:
    result = await session.execute(
        select(User).where(User.email == email)
    )
    return result.scalar_one_or_none()


async def register_user(
    session: AsyncSession,
    data: RegisterInput,
) -> User:
    existing_user = await find_user_by_email(
        session,
        str(data.email),
    )

    if existing_user is not None:
        raise EmailAlreadyRegisteredError()

    password_hash = await run_in_threadpool(
        hash_password,
        data.password,
    )

    user = User(
        display_name=data.display_name,
        email=str(data.email),
        password_hash=password_hash,
    )

    session.add(user)

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()

        existing_user = await find_user_by_email(
            session,
            str(data.email),
        )

        if existing_user is not None:
            raise EmailAlreadyRegisteredError() from None

        raise

    await session.refresh(user)
    return user