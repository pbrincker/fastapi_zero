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


def test_deve_retornar_lista_de_usuarios_vazia(client):
    response = client.get('/users')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}


def test_deve_listar_usuarios(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get('/users')
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


def test_deve_atualizar_um_usuario(client, user):
    response = client.put(
        '/users/1',
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


def test_deve_retornar_erro_quando_usuario_nao_existe(client):
    response = client.put(
        '/users/2',
        json={
            'username': 'teste2',
            'email': 'teste2@teste.com',
            'password': 'teste2',
        },
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_deve_deletar_um_usuario(client, user):
    response = client.delete('/users/1')
    assert response.status_code == HTTPStatus.NO_CONTENT


def test_deve_retornar_erro_quando_usuario_nao_existe_ao_deletar(client):
    response = client.delete('/users/2')
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_deve_retornar_erro_quando_tiver_conflito(client, user):
    client.post(
        '/users',
        json={
            'username': 'teste2',
            'email': 'teste2@teste.com',
            'password': 'teste',
        },
    )
    response = client.put(
        '/users/1',
        json={
            'username': 'teste2',
            'email': 'teste2@teste.com',
            'password': 'teste',
        },
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'User or email already exists'}
