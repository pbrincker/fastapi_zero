from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from fastapi_zero.settings import Settings


def get_session() -> Generator[Session, None, None]:
    engine = create_engine(Settings().DATABASE_URL)
    with Session(engine) as session:
        yield session
