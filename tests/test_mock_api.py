import re
from datetime import date, timedelta
from typing import Any, Dict

import pytest
import responses

from personio_py import DynamicMapping, Employee, Personio, PersonioApiError, PersonioError
from tests.mock_data import *

iso_date_match = re.compile(r'\d\d\d\d-\d\d-\d\d')


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
    # mock data & configure personio
    mock_employees()
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
    # validate serialization
    source_dict = json_dict_employees['data'][2]
    target_dict = ada.to_dict()
    compare_labeled_attributes(source_dict, target_dict)


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
def test_get_attendance():
    # mock the get absences endpoint (with different array offsets)
    responses.add(
        responses.GET, re.compile('https://api.personio.de/v1/company/attendances?.*offset=0.*'),
        status=200, json=json_dict_attendance_rms, adding_headers={'Authorization': 'Bearer foo'})
    responses.add(
        responses.GET, re.compile('https://api.personio.de/v1/company/attendances?.*offset=3.*'),
        status=200, json=json_dict_empty_response, adding_headers={'Authorization': 'Bearer bar'})
    # configure personio & get absences for alan
    personio = mock_personio()
    attendances = personio.get_attendances(2116366)
    # validate
    assert len(attendances) == 3
    selection = [a for a in attendances if "release" in a.comment.lower()]
    assert len(selection) == 1
    release = selection[0]
    assert "free software" in release.comment
    assert release.date == date(1985, 3, 20)
    assert release.start_time == timedelta(seconds=11*60*60)
    assert release.end_time == timedelta(seconds=12.5*60*60)
    assert release.break_duration == 60
    assert release.employee_id == 2116366
    # validate serialization
    source_dict = json_dict_attendance_rms['data'][0]
    target_dict = release.to_dict()
    compare_labeled_attributes(source_dict, target_dict)


def mock_personio():
    # mock the authentication endpoint, or all no requests will get through
    resp_json = {'success': True, 'data': {'token': 'dummy_token'}}
    responses.add(responses.POST, 'https://api.personio.de/v1/auth', json=resp_json, status=200)
    return Personio(client_id='test', client_secret='test')


def mock_employees():
    # mock the get employees endpoint
    responses.add(
        responses.GET, 'https://api.personio.de/v1/company/employees', status=200,
        json=json_dict_employees, adding_headers={'Authorization': 'Bearer rotated_dummy_token'})


def compare_labeled_attributes(expected: Dict, actual: Dict):
    if actual == expected:
        # fast lane - exact match
        return
    # let's see if there is any significant difference...
    attr_expected = expected['attributes']
    attr_actual = actual['attributes']
    keys = sorted(set(attr_expected.keys()) | set(attr_actual.keys()))
    # check every item
    for key in keys:
        val_expected = get_serialized_value(attr_expected, key)
        # skip none values (these are not serialized)
        if val_expected is not None:
            val_actual = get_serialized_value(attr_actual, key)
            if isinstance(val_expected, list):
                for exp, act in zip(*(val_expected, val_actual)):
                    compare_serialized_values(exp, act)
            else:
                compare_serialized_values(val_expected, val_actual)


def compare_serialized_values(expected: Any, actual: Any):
    if isinstance(expected, dict):
        # another dict? recur
        compare_labeled_attributes(expected, actual)
    elif isinstance(expected, str):
        if expected != actual:
            if iso_date_match.match(expected):
                # match ISO dates (only the date part, not time)
                assert actual[:10] == expected[:10]
            else:
                # match the entire string
                assert actual == expected
    else:
        assert actual == expected


def get_serialized_value(d: Dict, key: str):
    # two possible structures here: d[key]['value'] or just d['key']
    val = d[key]
    if isinstance(val, dict) and 'value' in val:
        return val['value']
    else:
        return val
