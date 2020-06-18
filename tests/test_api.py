import os

from personio_py import Employee, Personio

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
personio = Personio(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)

# TODO deactivate all tests that rely on a specific personio instance


def test_raw_api_employees():
    response = personio.request_json('company/employees')
    employees = response['data']
    assert len(employees) > 0
    id_0 = employees[0]['attributes']['id']['value']
    employee_0 = personio.request_json(f'company/employees/{id_0}')
    assert employee_0


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


def test_raw_api_absence_types():
    params = {"limit": 200, "offset": 0}
    absence_types = personio.request_json('company/time-off-types', params=params)
    assert len(absence_types['data']) > 10


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


def test_get_employees():
    employees = personio.get_employees()
    assert len(employees) > 0


def test_get_employee():
    employee = personio.get_employee(2007207)
    assert employee.first_name == 'Sebastian'
    d = employee.to_dict()
    assert d
    response = personio.request_json(f'company/employees/2007207')
    api_attr = response['data']['attributes']
    # TODO handle none values
    assert d == api_attr


def test_get_employee_picture():
    employee = Employee(client=personio, id_=2007207)
    picture = employee.picture()
    assert picture


def test_get_absences():
    absences = personio.get_absences(1460609)
    assert len(absences) > 0


def test_get_attendances():
    attendances = personio.get_attendances(2007207)
    assert len(attendances) > 0
