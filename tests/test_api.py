from personio_py import Personio

# TODO environment variables
CLIENT_ID = None
CLIENT_SECRET = None
personio = Personio(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)


def test_employees():
    response = personio.request('company/employees')
    employees = response['data']
    assert len(employees) > 100
    id_0 = employees[0]['attributes']['id']['value']
    employee_0 = personio.request(f'company/employees/{id_0}')
    assert employee_0


def test_attendances():
    params = {
        "start_date": "2020-01-01",
        "end_date": "2020-06-01",
        "employees": "1142212,1142211",
        "limit": 200,
        "offset": 0
    }
    attendances = personio.request('company/attendances', params=params)
    assert attendances


def test_absence_types():
    params = {"limit": 200, "offset": 0}
    absence_types = personio.request('company/time-off-types', params=params)
    assert len(absence_types['data']) > 10


def test_absences():
    params = {"start_date": "2020-01-01", "end_date": "2020-06-01", "employees": 1142212, "limit": 200, "offset": 0}
    absences = personio.request('company/time-offs', params=params)
    assert absences
