from http import HTTPStatus


def test_deve_retornar_token(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json()['token_type'] == 'Bearer'
    assert response.json()['access_token'] is not None
