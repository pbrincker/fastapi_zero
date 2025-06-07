from http import HTTPStatus

from jwt import decode

from fastapi_zero.security import create_access_token


def test_deve_retornar_token(settings):
    token = create_access_token({'sub': 'teste@teste.com'})
    decoded = decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
    )
    assert decoded['sub'] == 'teste@teste.com'
    assert decoded['exp'] is not None


def test_deve_retornar_erro_quando_token_nao_eh_valido(client):
    response = client.get(
        '/users',
        headers={'Authorization': 'Bearer 1234567890'},
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_deve_retornar_erro_quando_nao_tem_email(client):
    token = create_access_token({'sub': ''})
    response = client.get(
        '/users',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_deve_retornar_erro_quando_usuario_nao_existe(client):
    token = create_access_token({'sub': 'testeerrado@teste.com'})
    response = client.get(
        '/users',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {
        'detail': 'Could not validate credentials',
    }
