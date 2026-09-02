from tests.connection import get_skipif, get_test_employee, personio

skip_if_no_auth = get_skipif()


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
    employee = get_test_employee()
    params = {
        "start_date": "2010-01-01",
        "end_date": "2030-01-01",
        "employees[]": [employee.id],
        "limit": 200,
        "offset": 0
    }
    attendances = personio.request_json('company/attendances', params=params)
    assert attendances


@skip_if_no_auth
def test_raw_api_absence_types():
    params = {"limit": 200, "offset": 0}
    absence_types = personio.request_json('company/time-off-types', params=params)
    assert absence_types['data']


@skip_if_no_auth
def test_raw_api_absences():
    employee = get_test_employee()
    params = {
        "start_date": "2010-01-01",
        "end_date": "2030-01-01",
        "employees[]": [employee.id],
        "limit": 200,
        "offset": 0
    }
    absences = personio.request_json('company/time-offs', params=params)
    assert absences
