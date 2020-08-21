import re
from datetime import date
from typing import Dict

import pytest
import responses

from personio_py import DynamicMapping, Employee, Personio, PersonioApiError, PersonioError
from tests.mock_data import *


@responses.activate
def test_authenticate_ok():
    # mock a successful authentication response
    resp_json = {'success': True, 'data': {'token': 'dummy_token'}}
    responses.add(responses.POST, 'https://api.personio.de/v1/auth', json=resp_json, status=200)
    # authenticate
    personio = Personio(client_id='test', client_secret='test')
    personio.authenticate()
    # validate
    assert personio.authenticated is True
    assert personio.headers['Authorization'] == "Bearer dummy_token"


@responses.activate
def test_authenticate_fail():
    # mock a failed authentication response
    resp_json = {'success': False, 'error': {'code': 0, 'message': 'Wrong credentials'}}
    responses.add(responses.POST, 'https://api.personio.de/v1/auth', json=resp_json, status=403)
    # try to authenticate
    personio = Personio(client_id='test', client_secret='test')
    with pytest.raises(PersonioApiError) as e:
        personio.authenticate()
    assert "Wrong credentials" in str(e.value)
    assert personio.authenticated is False


@responses.activate
def test_get_employees():
    # mock the get employees endpoint
    responses.add(
        responses.GET, 'https://api.personio.de/v1/company/employees', status=200,
        json=json_dict_employees, adding_headers={'Authorization': 'Bearer rotated_dummy_token'})
    # configure personio
    personio = mock_personio()
    personio.dynamic_fields = [
        DynamicMapping(1146666, 'birthday', date),
        DynamicMapping(1146702, 'origin', str),
    ]
    # get the list of employees
    employees = personio.get_employees()
    # validate
    assert len(employees) == 3
    employee_dict: Dict[str, Employee] = {e.first_name: e for e in employees}
    ada = employee_dict['Ada']
    alan = employee_dict['Alan']
    rms = employee_dict['Richard']
    assert ada.last_name == 'Lovelace'
    assert ada.dynamic['birthday'] == date(1815, 12, 10)
    assert alan.position == 'Chief Cryptanalyst'
    assert alan.vacation_day_balance == 25
    assert rms.hire_date.year == 1983
    assert rms.work_schedule.monday.seconds == 8*60*60


@responses.activate
def test_get_employee_by_id():
    # mock the get employee endpoint
    responses.add(
        responses.GET, 'https://api.personio.de/v1/company/employees/2040614', status=200,
        json=json_dict_employee_ada, adding_headers={'Authorization': 'Bearer rotated_dummy_token'})
    # configure personio & get employee
    personio = mock_personio()
    ada = personio.get_employee(2040614)
    # validate
    assert ada.id_ == 2040614
    assert ada.last_name == 'Lovelace'


@responses.activate
def test_auth_rotation_fail():
    # mock the get employees endpoint
    responses.add(
        responses.GET, 'https://api.personio.de/v1/company/employees', status=200,
        json=json_dict_employees, adding_headers={})
    # get the mocked response
    personio = mock_personio()
    with pytest.raises(PersonioError) as e:
        personio.get_employees()
    assert "authorization header" in str(e.value).lower()


@responses.activate
def test_get_absences():
    # mock the get absences endpoint (with different array offsets)
    responses.add(
        responses.GET, re.compile('https://api.personio.de/v1/company/time-offs?.*offset=0.*'),
        status=200, json=json_dict_absence_alan, adding_headers={'Authorization': 'Bearer foo'})
    responses.add(
        responses.GET, re.compile('https://api.personio.de/v1/company/time-offs?.*offset=3.*'),
        status=200, json=json_dict_empty_response, adding_headers={'Authorization': 'Bearer bar'})
    # configure personio & get absences for alan
    personio = mock_personio()
    absences = personio.get_absences(2116365)
    # validate
    assert len(absences) == 3
    selection = [a for a in absences if "marathon" in a.comment.lower()]
    assert len(selection) == 1
    marathon = selection[0]
    assert marathon.start_date == date(1944, 9, 1)
    assert marathon.half_day_start == 0
    assert marathon.half_day_end == 1
    assert marathon.status == 'approved'


def mock_personio():
    # mock the authentication endpoint, or all no requests will get through
    resp_json = {'success': True, 'data': {'token': 'dummy_token'}}
    responses.add(responses.POST, 'https://api.personio.de/v1/auth', json=resp_json, status=200)
    return Personio(client_id='test', client_secret='test')
