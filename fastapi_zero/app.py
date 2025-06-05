from http import HTTPStatus

from fastapi import FastAPI, HTTPException

from fastapi_zero.schemas import (
    Message,
    UserDB,
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
def create_user(user: UserSchema):
    user_with_id = UserDB(**user.model_dump(), id=len(database) + 1)
    database.append(user_with_id)
    return user_with_id


@app.get('/users', response_model=UserList, status_code=HTTPStatus.OK)
def get_users():
    return {'users': database}


@app.get(
    '/users/{user_id}',
    response_model=UserPublic,
    status_code=HTTPStatus.OK,
)
def get_user(user_id: int):
    for user_db in database:
        if user_db.id == user_id:
            return user_db
    raise HTTPException(
        status_code=HTTPStatus.NOT_FOUND,
        detail='User not found',
    )


@app.put(
    '/users/{user_id}',
    response_model=UserPublic,
    status_code=HTTPStatus.OK,
)
def update_user(user_id: int, user: UserSchema):
    user_with_id = UserDB(**user.model_dump(), id=user_id)
    for index, user_db in enumerate(database):
        if user_db.id == user_id:
            database[index] = user_with_id
            return user_with_id
    raise HTTPException(
        status_code=HTTPStatus.NOT_FOUND,
        detail='User not found',
    )


@app.delete('/users/{user_id}', status_code=HTTPStatus.NO_CONTENT)
def delete_user(user_id: int):
    for index, user_db in enumerate(database):
        if user_db.id == user_id:
            database.pop(index)
            return
    raise HTTPException(
        status_code=HTTPStatus.NOT_FOUND,
        detail='User not found',
    )
