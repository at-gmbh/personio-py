import responses

from personio_py import Personio


@responses.activate
def test_authenticate_ok():
    # mock a successful authentication response
    resp_json = {'data': {'token': 'dummy_token'}}
    responses.add(responses.POST, 'https://api.personio.de/v1/auth', json=resp_json, status=200)
    # authenticate
    personio = Personio(client_id='test', client_secret='test')
    personio.authenticate()
    # validate
    assert personio.authenticated is True
    assert personio.headers['Authorization'] == "Bearer dummy_token"
