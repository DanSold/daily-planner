from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    Request,
    Response,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.schemas.auth import LoginInput, RegisterInput, UserPublic
from app.services.users import (
    EmailAlreadyRegisteredError,
    register_user,
)
from app.services.sessions import (
    InvalidCredentialsError,
    authenticate_user,
    create_user_session,
    delete_user_session,
)
from app.config import settings
from app.dependencies import get_current_user
from app.models import User

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

@router.post("/login", response_model=UserPublic)
async def login(
    data: Annotated[LoginInput, Form()],
    response: Response,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    try:
        user = await authenticate_user(session, data)
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        ) from None

    token = await create_user_session(session, user)

    response.set_cookie(
        key=settings.session_cookie_name,
        value=token,
        max_age=settings.session_lifetime_days * 24 * 60 * 60,
        httponly=True,
        secure=settings.session_cookie_secure,
        samesite="lax",
        path="/",
    )

    return user


@router.get("/me", response_model=UserPublic)
async def me(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return current_user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    token = request.cookies.get(settings.session_cookie_name)

    if token:
        await delete_user_session(session, token)

    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    response.delete_cookie(
        key=settings.session_cookie_name,
        path="/",
        httponly=True,
        secure=settings.session_cookie_secure,
        samesite="lax",
    )
    return response