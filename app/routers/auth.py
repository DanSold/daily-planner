from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.schemas.auth import RegisterInput, UserPublic
from app.services.users import (
    EmailAlreadyRegisteredError,
    register_user,
)

router = APIRouter(tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    data: Annotated[RegisterInput, Form()],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    try:
        return await register_user(session, data)
    except EmailAlreadyRegisteredError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        ) from None