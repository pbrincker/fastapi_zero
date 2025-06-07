from http import HTTPStatus

from fastapi_zero.schemas import UserPublic


def test_root_deve_retornar_hello_world(client):
    response = client.get('/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Hello World'}


def test_deve_criar_um_usuario(client):
    response = client.post(
        '/users',
        json={
            'username': 'teste',
            'email': 'teste@teste.com',
            'password': 'teste',
        },
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'username': 'teste',
        'email': 'teste@teste.com',
        'id': 1,
    }


def test_deve_retornar_erro_quando_usuario_ja_existe(client, user):
    response = client.post(
        '/users',
        json={
            'username': 'teste',
            'email': 'teste@teste.com',
            'password': 'teste',
        },
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'User or email already exists'}


def test_nao_deve_retornar_lista_de_usuarios_sem_token(client):
    response = client.get(
        '/users',
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Not authenticated'}


def test_deve_listar_usuarios(client, user, token):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get(
        '/users',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


def test_deve_retornar_um_usuario(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get('/users/1')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == user_schema


def test_deve_retornar_erro_quando_usuario_nao_existe_ao_buscar(client):
    response = client.get('/users/2')
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_deve_atualizar_um_usuario(client, user, token):
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'teste2',
            'email': 'teste2@teste.com',
            'password': 'teste2',
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'teste2',
        'email': 'teste2@teste.com',
        'id': 1,
    }


def test_deve_retornar_erro_quando_usuario_nao_tem_permissao(client, token):
    response = client.put(
        '/users/2',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'teste2',
            'email': 'teste2@teste.com',
            'password': 'teste2',
        },
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {
        'detail': 'You are not allowed to update this user',
    }


def test_deve_deletar_um_usuario(client, user, token):
    response = client.delete(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.NO_CONTENT


def test_deve_retornar_erro_quando_usuario_nao_existe_ao_deletar(
    client,
    token,
):
    response = client.delete(
        '/users/2',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {
        'detail': 'You are not allowed to delete this user',
    }


def test_deve_retornar_erro_quando_tiver_conflito(client, user, token):
    client.post(
        '/users',
        json={
            'username': 'teste2',
            'email': 'teste2@teste.com',
            'password': 'teste',
        },
    )
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'teste2',
            'email': 'teste2@teste.com',
            'password': 'teste',
        },
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'User or email already exists'}


def test_deve_retornar_token(client, user):
    response = client.post(
        '/token',
        data={'username': user.email, 'password': user.clean_password},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json()['token_type'] == 'Bearer'
    assert response.json()['access_token'] is not None
