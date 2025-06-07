from http import HTTPStatus

from fastapi import FastAPI

from fastapi_zero.routers import auth, users
from fastapi_zero.schemas import (
    Message,
)

app = FastAPI(title='FastAPI Zero', version='0.1.0')

app.include_router(auth.router)
app.include_router(users.router)


@app.get('/', response_model=Message, status_code=HTTPStatus.OK)
def read_root():
    return {'message': 'Hello World'}
