from typing import Any, Dict
from urllib.parse import urljoin

import requests


BASE_URL = "https://api.personio.de/v1/"
HEADERS = {'accept': 'application/json'}

# TODO environment variables
CLIENT_ID = ...
CLIENT_SECRET = ...


def authenticate(client_id: str, client_secret: str):
    url = urljoin(BASE_URL, 'auth')
    params = {"client_id": client_id, "client_secret": client_secret}
    response = requests.request("POST", url, headers=HEADERS, params=params)
    token = response.json()['data']['token']
    HEADERS['Authorization'] = f"Bearer {token}"
    return token


def request(path: str, method='GET', params: Dict[str, Any] = None):
    if 'Authorization' not in HEADERS:
        raise RuntimeError("Not authenticated!")
    url = urljoin(BASE_URL, path)
    response = requests.request(method, url, headers=HEADERS, params=params)
    HEADERS['Authorization'] = response.headers['Authorization']
    if response.ok:
        data = response.json()['data']
        return data
    else:
        error = response.json()['error']
        response.raise_for_status()


def setup_module(module):
    authenticate(CLIENT_ID, CLIENT_SECRET)


def test_employees():
    employees = request('company/employees')
    assert len(employees) > 100
    id_0 = employees[0]['attributes']['id']['value']
    employee_0 = request(f'company/employees/{id_0}')
    assert employee_0


def test_attendances():
    params = {
        "start_date": "2020-01-01",
        "end_date": "2020-06-01",
        "employees": "1142212,1142211",
        "limit": 200,
        "offset": 0
    }
    attendances = request('company/attendances', params=params)
    assert attendances


def test_absence_types():
    params = {"limit": 200, "offset": 0}
    absence_types = request('company/time-off-types', params=params)
    assert absence_types


def test_absences():
    params = {"start_date": "2020-01-01", "end_date": "2020-06-01", "employees": 1142212, "limit": 200, "offset": 0}
    absences = request('company/time-offs', params=params)
    assert absences
