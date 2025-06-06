from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, registry

mapper_registry = registry()


@mapper_registry.mapped_as_dataclass
class User:
    """
    User model
    """

    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
        init=False, default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        init=False, default=func.now(), onupdate=func.now()
    )
