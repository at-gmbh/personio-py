import time
from datetime import datetime

import pytest

from personio_py import Department, Employee, PersonioApiError
from tests.connection import get_skipif, get_test_employee, personio

skip_if_no_auth = get_skipif()
created_employee_id = None


@skip_if_no_auth
def test_get_employees():
    employees = personio.get_employees()
    assert employees


@skip_if_no_auth
def test_get_employee():
    employee = get_test_employee()
    assert employee.first_name == 'Alan'
    serialization_test(employee)


@skip_if_no_auth
def test_get_employee_picture():
    employee = get_test_employee()
    # first request, slow
    t0 = time.perf_counter()
    picture = employee.picture()
    assert picture
    # picture should be cached, this request should be really fast
    t1 = time.perf_counter()
    picture_2 = employee.picture()
    t2 = time.perf_counter()
    assert picture_2 == picture
    assert 0.1 * (t2 - t1) < (t1 - t0)


@skip_if_no_auth
def test_get_custom_attributes():
    attrs = personio.get_custom_attributes()
    assert attrs


@skip_if_no_auth
def test_employee_custom_attributes():
    employee = get_test_employee()
    assert employee._custom_attribute_keys
    assert employee._custom_attribute_aliases
    # get custom attributes directly
    for key in employee._custom_attribute_keys:
        getattr(employee, key)
    # get custom attributes by their aliases
    for key in employee._custom_attribute_aliases.keys():
        getattr(employee, key)
    # set a custom attribute directly
    aliases = list(employee._custom_attribute_aliases.items())
    key_0 = aliases[0][0]
    assert getattr(employee, key_0) != 'foo'
    setattr(employee, key_0, 'foo')
    assert getattr(employee, key_0) == 'foo'
    # set a custom attribute using its alias
    key_1 = aliases[1][1]
    assert getattr(employee, key_1) != 'bar'
    setattr(employee, key_1, 'bar')
    assert getattr(employee, key_1) == 'bar'


@skip_if_no_auth
def test_create_employee():
    # note: sice Personio does not provide any API endpoints to delete employees,
    # you have to manually delete this employee via the web UI if you want to run
    # this test more than once...
    personio.update_model(globals())
    # create an employee object
    tim = Employee(
        first_name='Tim',
        last_name='Berners-Lee',
        email='timbl@example.org',
        position='inventor of the World Wide Web',
        department=Department(name='Operations'),
        hire_date=datetime(1989, 3, 12),
        weekly_working_hours='35',
    )
    custom_attr = tim._custom_attribute_keys[0]
    setattr(tim, custom_attr, 'foo')
    try:
        # send it to the API
        tim_created = personio.create_employee(tim)
        global created_employee_id
        created_employee_id = tim_created.id
        # check that it works
        assert tim.first_name == tim_created.first_name
        assert tim.email == tim_created.email
        assert tim_created.id
        assert tim_created.last_modified_at.date() == datetime.now().date()
        assert getattr(tim, custom_attr) == 'foo'
        assert tim_created.status == 'active'
    except PersonioApiError as e:
        if "already in use" in e.message:
            pytest.skip(f"cannot create already existing employee again. Please delete "
                        f"{tim.first_name} {tim.last_name} from the web UI to run this test")
        else:
            raise e


@skip_if_no_auth
def test_update_employee():
    tim = get_tim()
    tim.gender = 'male'
    tim.weekly_working_hours = '30'

    # due to a bug in the personio API, custom attributes are not updated
    #custom_attr = tim._custom_attribute_keys[-1]
    #setattr(tim, custom_attr, 'bar')
    # please uncomment the two lines above when it is fixed...

    d_before = dict(tim)
    tim_updated = tim.update()
    d_after = dict(tim_updated)
    del d_before['last_modified_at']
    del d_after['last_modified_at']
    assert d_after == d_before


@skip_if_no_auth
def test_absence_balance():
    employee = get_test_employee()
    balance = employee.absence_balance()
    assert balance


def serialization_test(employee: Employee):
    # reload the Employee class
    from personio_py import Employee
    # from/to dict
    d = dict(employee)
    assert d
    parsed_dict = Employee(**d)
    assert parsed_dict == employee
    # from/to json
    json_str = employee.json()
    assert json_str
    parsed_json = Employee.parse_raw(json_str)
    assert parsed_json == employee


def get_tim():
    if created_employee_id:
        return personio.get_employee(created_employee_id)
    else:
        return personio.search_first("Tim Berners-Lee")
