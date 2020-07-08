import os
from datetime import datetime

import pytest

from personio_py import Department, Employee, Personio, PersonioError

# Personio client authentication
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
personio = Personio(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)

# deactivate all tests that rely on a specific personio instance
try:
    personio.authenticate()
    can_authenticate = True
except PersonioError:
    can_authenticate = False
skip_if_no_auth = pytest.mark.skipif(not can_authenticate, reason="Personio authentication failed")


@skip_if_no_auth
def test_raw_api_employees():
    response = personio.request_json('company/employees')
    employees = response['data']
    assert len(employees) > 0
    id_0 = employees[0]['attributes']['id']['value']
    employee_0 = personio.request_json(f'company/employees/{id_0}')
    assert employee_0


@skip_if_no_auth
def test_raw_api_attendances():
    params = {
        "start_date": "2020-01-01",
        "end_date": "2020-06-01",
        "employees[]": [1142212, 1142211],
        "limit": 200,
        "offset": 0
    }
    attendances = personio.request_json('company/attendances', params=params)
    assert attendances


@skip_if_no_auth
def test_raw_api_absence_types():
    params = {"limit": 200, "offset": 0}
    absence_types = personio.request_json('company/time-off-types', params=params)
    assert len(absence_types['data']) > 10


@skip_if_no_auth
def test_raw_api_absences():
    params = {
        "start_date": "2020-01-01",
        "end_date": "2020-06-01",
        "employees[]": [1142212],  # [2007207, 2007248]
        "limit": 200,
        "offset": 0
    }
    absences = personio.request_json('company/time-offs', params=params)
    assert absences


@skip_if_no_auth
def test_get_employees():
    employees = personio.get_employees()
    assert len(employees) > 0


@skip_if_no_auth
def test_get_employee():
    employee = personio.get_employee(2007207)
    assert employee.first_name == 'Sebastian'
    d = employee.to_dict()
    assert d
    response = personio.request_json(f'company/employees/2007207')
    api_attr = response['data']['attributes']
    assert d == api_attr


@skip_if_no_auth
def test_get_employee_picture():
    employee = Employee(client=personio, id_=2007207)
    picture = employee.picture()
    assert picture


@skip_if_no_auth
def test_create_employee():
    ada = Employee(
        first_name='Ada',
        last_name='Lovelace',
        email='ada@example.org',
        gender='female',
        position='first programmer ever',
        department=Department(name='Operations'),
        hire_date=datetime(1835, 2, 1),
        weekly_working_hours="35",
    )
    ada_created = personio.create_employee(ada, refresh=True)
    assert ada.first_name == ada_created.first_name
    assert ada.email == ada_created.email
    assert ada_created.id_
    assert ada_created.last_modified_at.isoformat()[:10] == datetime.now().isoformat()[:10]
    assert ada_created.status == 'active'


@skip_if_no_auth
def test_get_absences():
    absences = personio.get_absences(2007207)
    assert len(absences) > 0


@skip_if_no_auth
def test_get_attendances():
    attendances = personio.get_attendances(2007207)
    assert len(attendances) > 0
