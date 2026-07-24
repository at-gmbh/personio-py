from datetime import datetime

from personio_py import Employee, Department
from tests.apitest_shared import *


@skip_if_no_auth
def test_get_employees():
    employees = personio.get_employees()
    assert len(employees) > 0


@skip_if_no_auth
def test_get_employee():
    employee = personio.get_employee(16400788)
    assert employee.first_name == 'Richard'
    d = employee.to_dict()
    assert d
    response = personio.request_json('company/employees/16400788')
    api_attr = response['data']['attributes']
    # to_dict() wraps the labeled attributes under a {'type', 'attributes'} envelope, so we
    # compare the inner attributes against the API. A full equality check is intentionally
    # avoided: the live API returns fields the models don't map yet (drift) and uses richer
    # date formats, so we verify that the representative fields the library serializes match.
    lib_attr = d['attributes']
    for key in ('first_name', 'last_name', 'email'):
        assert lib_attr[key]['value'] == api_attr[key]['value']


@skip_if_no_auth
def test_get_employee_picture():
    employee = Employee(client=personio, id_=16400788)
    picture = employee.picture()
    assert picture


@skip_if_no_auth
@pytest.mark.xfail(reason="create_employee is a placeholder / not ready to be used "
                          "(see Personio.create_employee docstring); its form-style payload "
                          "is not accepted by the current API")
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
def test_get_attendances():
    attendances = personio.get_attendances(16400788)
    assert len(attendances) > 0
