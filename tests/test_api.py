import os
from datetime import datetime, timedelta, date

import pytest

from personio_py import Department, Employee, ShortEmployee, Personio, PersonioError, Absence, AbsenceType

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
        department=None,
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
@pytest.mark.parametrize("half_day_start", [True, False])
@pytest.mark.parametrize("half_day_end", [True, False])
def test_create_absences(half_day_start: bool, half_day_end: bool):
    """
    Test the creation of absence records on the server.
    """
    # Prepare data
    test_data = shared_test_data['test_employee']
    test_user = personio.get_employee(test_data['id'])
    start_date = date(2021, 1, 1)
    end_date = date(2021, 1, 10)

    # Ensure there are no left absences
    delete_all_absences_of_employee(test_user)

    # Start test
    absence_to_create = create_absence_for_user(test_user,
                                                start_date=start_date,
                                                end_date=end_date,
                                                half_day_start=half_day_start,
                                                half_day_end=half_day_end)
    assert absence_to_create.id_ is None
    absence_to_create.create(personio)
    assert absence_to_create.id_
    remote_absence = personio.get_absence(absence=absence_to_create)
    assert remote_absence.half_day_start is half_day_start
    assert remote_absence.half_day_end is half_day_end
    assert remote_absence.start_date - start_date < timedelta(seconds=1)
    assert remote_absence.end_date - end_date < timedelta(seconds=1)


@skip_if_no_auth
def test_get_absences_from_id():
    user = prepare_test_get_absences()
    id = create_absence_for_user(user, create=True).id_
    absence = personio.get_absence(id)
    assert absence.id_ == id


@skip_if_no_auth
def test_get_absences_from_absence_object():
    user = prepare_test_get_absences()
    remote_absence = create_absence_for_user(user, create=True)
    absence = personio.get_absence(remote_absence)
    assert absence.id_ == remote_absence.id_


@skip_if_no_auth
def test_get_absences_from_absence_object_without_id_remote_query():
    user = prepare_test_get_absences()
    remote_absence = create_absence_for_user(user, create=True)
    absence_id = remote_absence.id_
    remote_absence.id_ = None
    absence = personio.get_absence(remote_absence, remote_query_id=True)
    assert absence.id_ == absence_id


@skip_if_no_auth
def test_get_absences_from_absence_object_without_id_no_remote_query():
    user = prepare_test_get_absences()
    remote_absence = create_absence_for_user(user, create=True)
    remote_absence.id_ = None
    with pytest.raises(ValueError):
        personio.get_absence(remote_absence, remote_query_id=False)


@skip_if_no_auth
def test_delete_absences_from_model_no_client():
    test_data = shared_test_data['test_employee']
    test_user = personio.get_employee(test_data['id'])
    delete_all_absences_of_employee(test_user)
    absence = create_absence_for_user(test_user, create=True)
    with pytest.raises(PersonioError):
        absence.delete()


@skip_if_no_auth
def test_delete_absences_from_model_passed_client():
    test_data = shared_test_data['test_employee']
    test_user = personio.get_employee(test_data['id'])
    delete_all_absences_of_employee(test_user)
    absence = create_absence_for_user(test_user, create=True)
    assert absence.delete(client=personio) is True


@skip_if_no_auth
def test_delete_absences_from_model_with_client():
    test_data = shared_test_data['test_employee']
    test_user = personio.get_employee(test_data['id'])
    delete_all_absences_of_employee(test_user)
    absence = create_absence_for_user(test_user, create=True)
    absence.client = personio
    assert absence.delete() is True


@skip_if_no_auth
def test_delete_absences_from_client_id():
    test_data = shared_test_data['test_employee']
    test_user = personio.get_employee(test_data['id'])
    delete_all_absences_of_employee(test_user)
    absence = create_absence_for_user(test_user, create=True)
    assert personio.delete_absence(absence.id_) is True


@skip_if_no_auth
def test_delete_absences_from_client_object_with_id():
    test_data = shared_test_data['test_employee']
    test_user = personio.get_employee(test_data['id'])
    delete_all_absences_of_employee(test_user)
    absence = create_absence_for_user(test_user, create=True)
    assert personio.delete_absence(absence) is True


@skip_if_no_auth
def test_delete_absences_from_client_object_with_no_id_query():
    test_data = shared_test_data['test_employee']
    test_user = personio.get_employee(test_data['id'])
    delete_all_absences_of_employee(test_user)
    absence = create_absence_for_user(test_user, create=True)
    absence.id_ = None
    assert personio.delete_absence(absence, remote_query_id=True) is True


@skip_if_no_auth
def test_delete_absences_from_client_object_with_no_id_no_query():
    test_data = shared_test_data['test_employee']
    test_user = personio.get_employee(test_data['id'])
    delete_all_absences_of_employee(test_user)
    absence = create_absence_for_user(test_user, create=True)
    absence.id_ = None
    with pytest.raises(ValueError):
        personio.delete_absence(absence, remote_query_id=False)


@skip_if_no_auth
def test_get_attendances():
    attendances = personio.get_attendances(2007207)
    assert len(attendances) > 0


def delete_absences(client: Personio, absences: [int] or [Absence]):
    for absence in absences:
        client.delete_absence(absence)


def create_absences(client: Personio, absences: [Absence]):
    for absence in absences:
        client.create_absence(absence)


def delete_all_absences_of_employee(employee: Employee):
    absences = personio.get_absences(employee)
    delete_absences(personio, absences)


def create_absence_for_user(employee: Employee,
                            time_off_type: AbsenceType = None,
                            start_date: date = None,
                            end_date: date = None,
                            half_day_start: bool = False,
                            half_day_end: bool = False,
                            comment: str = None,
                            create: bool = False) -> Absence:
    if not time_off_type:
        absence_types = personio.get_absence_types()
        time_off_type = [absence_type for absence_type in absence_types if absence_type.name == "Unpaid vacation"][0]
    if not start_date:
        start_date = date(2021, 1, 1)
    if not end_date:
        end_date = date(2021, 1, 10)

    absence_to_create = Absence(
        start_date=start_date,
        end_date=end_date,
        time_off_type=time_off_type,
        employee=employee,
        half_day_start=half_day_start,
        half_day_end=half_day_end,
        comment=comment
    )
    if create:
        absence_to_create.create(personio)
    return absence_to_create


def prepare_test_get_absences() -> Employee:
    test_data = shared_test_data['test_employee']
    test_user = personio.get_employee(test_data['id'])

    # Be sure there are no leftover absences
    delete_all_absences_of_employee(test_user)
    return test_user

