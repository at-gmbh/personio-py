import time
from datetime import datetime

import pytest

from personio_py import Department, Employee, PersonioApiError
from tests.connection import get_skipif, get_test_employee, personio

skip_if_no_auth = get_skipif()


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
    personio.update_model()
    from personio_py import Employee
    # create an employee object
    tim = Employee(
        first_name='Tim',
        last_name='Berners-Lee',
        email='timbl@example.org',
        position='inventor of the World Wide Web',
        department=Department(name='Operations'),
        hire_date=datetime(1989, 3, 12),
        weekly_working_hours="35",
    )
    custom_0 = tim._custom_attribute_keys[0]
    setattr(tim, custom_0, 'foo')
    try:
        # send it to the API
        tim_created = personio.create_employee(tim)
        # check that it works
        assert tim.first_name == tim_created.first_name
        assert tim.email == tim_created.email
        assert tim_created.id
        assert tim_created.last_modified_at.date() == datetime.now().date()
        assert getattr(tim, custom_0) == 'foo'
        assert tim_created.status == 'active'
    except PersonioApiError as e:
        if "already in use" in e.message:
            pytest.skip(f"cannot create already existing employee again. Please delete "
                        f"{tim.first_name} {tim.last_name} from the web UI to run this test")
        else:
            raise e


@skip_if_no_auth
def test_update_employee():
    # TODO implement
    pass


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
