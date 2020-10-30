from .apitest_shared import *
from datetime import datetime, timedelta
from personio_py import Employee


@skip_if_no_auth
def test_get_employees():
    employees = personio.get_employees()
    assert len(employees) > 0


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
