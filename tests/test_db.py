from dataclasses import asdict

from sqlalchemy import select

from fastapi_zero.models import User


def test_deve_criar_usuario(session, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(
            username='teste', email='teste@teste.com', password='teste'
        )

        session.add(new_user)
        session.commit()

        user = session.scalar(select(User).where(User.username == 'teste'))
    assert asdict(user) == {
        'id': 1,
        'username': 'teste',
        'email': 'teste@teste.com',
        'password': 'teste',
        'created_at': time,
        'updated_at': time,
    }
