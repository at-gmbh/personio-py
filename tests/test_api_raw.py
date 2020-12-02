from tests.apitest_shared import *


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
    assert len(absence_types['data']) >= 10 # Personio test accounts know 10 different absence types


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
