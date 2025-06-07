from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fastapi_zero.database import get_session
from fastapi_zero.models import User
from fastapi_zero.schemas import (
    FilterPage,
    UserList,
    UserPublic,
    UserSchema,
)
from fastapi_zero.security import (
    get_current_user,
    get_password_hash,
)

router = APIRouter(prefix='/users', tags=['users'])

Session = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post(
    '/',
    response_model=UserPublic,
    status_code=HTTPStatus.CREATED,
)
def create_user(user: UserSchema, session: Session):
    db_user: User | None = session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )

    if db_user:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='User or email already exists',
        )

    user_with_id = User(
        email=user.email,
        username=user.username,
        password=get_password_hash(user.password),
    )
    session.add(user_with_id)
    session.commit()
    session.refresh(user_with_id)
    return user_with_id


@router.get(
    '/',
    response_model=UserList,
    status_code=HTTPStatus.OK,
)
def get_users(
    session: Session,
    current_user: CurrentUser,
    filter_page: Annotated[FilterPage, Query()],
):
    users = session.scalars(
        select(User).offset(filter_page.offset).limit(filter_page.limit)
    )
    return {'users': users}


@router.get(
    '/{user_id}/',
    response_model=UserPublic,
    status_code=HTTPStatus.OK,
)
def get_user(
    user_id: int,
    session: Session,
):
    user = session.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='User not found',
        )
    return user


@router.put(
    '/{user_id}/',
    response_model=UserPublic,
    status_code=HTTPStatus.OK,
)
def update_user(
    user_id: int,
    user: UserSchema,
    session: Session,
    current_user: CurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='You are not allowed to update this user',
        )

    try:
        current_user.email = user.email
        current_user.username = user.username
        current_user.password = get_password_hash(user.password)

        session.add(current_user)
        session.commit()
        session.refresh(current_user)
        return current_user
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='User or email already exists',
        )


@router.delete('/{user_id}/', status_code=HTTPStatus.NO_CONTENT)
def delete_user(
    user_id: int,
    session: Session,
    current_user: CurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='You are not allowed to delete this user',
        )

    session.delete(current_user)
    session.commit()
