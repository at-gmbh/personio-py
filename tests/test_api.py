from personio_py import Employee, Department
from tests.apitest_shared import *
from datetime import datetime

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
