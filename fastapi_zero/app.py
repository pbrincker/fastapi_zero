from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from fastapi_zero.database import get_session
from fastapi_zero.models import User
from fastapi_zero.schemas import (
    Message,
    UserList,
    UserPublic,
    UserSchema,
)

app = FastAPI()

database = []


@app.get('/', response_model=Message, status_code=HTTPStatus.OK)
def read_root():
    return {'message': 'Hello World'}


@app.post('/users', response_model=UserPublic, status_code=HTTPStatus.CREATED)
def create_user(user: UserSchema, session: Session = Depends(get_session)):
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

    user_with_id = User(**user.model_dump())
    session.add(user_with_id)
    session.commit()
    session.refresh(user_with_id)
    return user_with_id


@app.get('/users', response_model=UserList, status_code=HTTPStatus.OK)
def get_users(
    session: Session = Depends(get_session),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    users = session.scalars(select(User).offset(offset).limit(limit))
    return {'users': users}


@app.get(
    '/users/{user_id}',
    response_model=UserPublic,
    status_code=HTTPStatus.OK,
)
def get_user(
    user_id: int,
    session: Session = Depends(get_session),
):
    user = session.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='User not found',
        )
    return user


@app.put(
    '/users/{user_id}',
    response_model=UserPublic,
    status_code=HTTPStatus.OK,
)
def update_user(
    user_id: int,
    user: UserSchema,
    session: Session = Depends(get_session),
):
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

    user_db = session.scalar(select(User).where(User.id == user_id))
    if not user_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='User not found',
        )

    user_db.email = user.email
    user_db.username = user.username
    user_db.password = user.password

    session.add(user_db)
    session.commit()
    session.refresh(user_db)

    return user_db


@app.delete('/users/{user_id}', status_code=HTTPStatus.NO_CONTENT)
def delete_user(
    user_id: int,
    session: Session = Depends(get_session),
):
    user_db = session.scalar(select(User).where(User.id == user_id))
    if not user_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='User not found',
        )
    session.delete(user_db)
    session.commit()
