import os
from datetime import datetime, timedelta, date

import pytest

from personio_py import Department, Employee, ShortEmployee, Personio, PersonioError, Absence

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

# This is used to ensure the test check for existing objects
shared_test_data = {
    'absences_to_delete': []
}


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


@skip_if_no_auth
def test_get_employees():
    employees = personio.get_employees()
    assert len(employees) > 0
    test_employee = employees[0]
    shared_test_data['test_employee'] = {
        'id': test_employee.id_,
        'first_name': test_employee.first_name,
        'last_name': test_employee.last_name,
        'email': test_employee.email,
        'hire_date': test_employee.hire_date
    }


@skip_if_no_auth
def test_get_employee():
    test_data = shared_test_data['test_employee']
    employee = personio.get_employee(test_data['id'])
    assert employee.first_name == test_data['first_name']
    assert employee.last_name == test_data['last_name']
    assert employee.email == test_data['email']
    assert employee.hire_date == test_data['hire_date']
    d = employee.to_dict()
    assert d
    response = personio.request_json('company/employees/' + str(test_data['id']))
    api_attr = response['data']['attributes']
    attr = d['attributes']
    for att_name in attr.keys():
        if 'date' not in att_name:
            assert attr[att_name] == api_attr[att_name]
        else:
            att_date = datetime.fromisoformat(attr[att_name]['value']).replace(tzinfo=None)
            api_attr_date = datetime.fromisoformat(api_attr[att_name]['value']).replace(tzinfo=None)
            assert (att_date - api_attr_date) < timedelta(seconds=1)


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
def test_create_absences_no_halfdays():
    # Prepare data
    test_data = shared_test_data['test_employee']
    test_user = personio.get_employee(test_data['id'])
    start_date = date(2020, 1, 1)
    end_date = date(2020, 1, 10)

    # Ensure there are no left absences
    absences = personio.get_absences(test_user.id_)
    delete_absences(personio, absences)

    # Start test
    absence_to_create = Absence(
        start_date=start_date,
        end_date=end_date,
        time_off_type=personio.get_absence_types()[0],
        employee=test_user,
        comment="Test"
    )
    absence_to_create.create(personio)
    assert absence_to_create.id_
    remote_absence = personio.get_absence(absence_id=absence_to_create.id_)
    assert remote_absence.half_day_start is False
    assert remote_absence.half_day_start is False
    assert remote_absence.start_date - start_date < timedelta(seconds=1)
    assert remote_absence.end_date - end_date < timedelta(seconds=1)


@skip_if_no_auth
def test_get_absences():
    test_data = shared_test_data['test_employee']
    test_user = personio.get_employee(test_data['id'])
    absences = personio.get_absences(test_user.id_)
    #assert len(absences) == len(shared_test_data['absences_to_delete'])
    for created_absence in shared_test_data['absences_to_delete']:
        #assert len([absence for absence in absences if absence.id_ == created_absence.id_]) == 1
        remote_absence = [absence for absence in absences if absence.id_ == created_absence.id_][0]
        #assert created_absence.employee.id_ == remote_absence.employee.id_


@skip_if_no_auth
def test_delete_absences():
    test_data = shared_test_data['test_employee']
    test_user = personio.get_employee(test_data['id'])
    absences = personio.get_absences(test_user.id_)
    num_absences = len(absences)
    #assert len(absences) == len(shared_test_data['absences_to_delete'])
    for created_absence in shared_test_data['absences_to_delete'] or absences:
        created_absence.delete(client=personio)
        absences = personio.get_absences(test_user.id_)
        #assert len(absences) == num_absences - 1
        num_absences -= 1




@skip_if_no_auth
def test_get_attendances():
    attendances = personio.get_attendances(2007207)
    assert len(attendances) > 0


def delete_absences(client: Personio, absences: [int] or [Absence]):
    for absence in absences:
        client.delete_absence(absence)
