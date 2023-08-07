import re
from datetime import date
from typing import Dict

import pytest
import responses

from personio_py import Employee, PersonioError
from tests.test_mock import compare_dates, compare_labeled_attributes, load_mock_data, mock_personio


@responses.activate
def test_get_employees():
    # mock data & configure personio
    mock_employees()
    personio = mock_personio()
    # get the list of employees
    employees = personio.get_employees()
    # validate
    assert len(employees) == 3
    employee_dict: Dict[str, Employee] = {e.first_name: e for e in employees}
    ada = employee_dict['Ada']
    alan = employee_dict['Alan']
    rms = employee_dict['Richard']
    assert ada.last_name == 'Lovelace'
    compare_dates(date(1815, 12, 10), ada.dynamic_1146666)
    compare_dates(date(1815, 12, 10), ada.geburtstag)
    assert alan.position == 'Chief Cryptanalyst'
    assert alan.vacation_day_balance == 25
    assert rms.hire_date.year == 1983
    assert rms.work_schedule.monday.seconds == 8 * 60 * 60
    # validate serialization
    source_dict = load_mock_data('get-employees.json')
    ada_source_dict = source_dict['data'][2]
    ada_target_dict = ada.dict()
    compare_labeled_attributes(ada_source_dict, ada_target_dict)


@responses.activate
def test_get_employee_by_id():
    # mock the get employee endpoint
    responses.add(
        method=responses.GET,
        url='https://api.personio.de/v1/company/employees/2040614',
        status=200,
        json=load_mock_data('get-employee-ada.json'),
        adding_headers={'Authorization': 'Bearer rotated_dummy_token'})
    # configure personio & get employee
    personio = mock_personio()
    ada = personio.get_employee(2040614)
    # validate
    assert ada.id == 2040614
    assert ada.last_name == 'Lovelace'


@responses.activate
def test_auth_rotation_fail():
    # mock the get employees endpoint
    responses.add(
        responses.GET, 'https://api.personio.de/v1/company/employees', status=200,
        json=load_mock_data('get-custom-attributes.json'), adding_headers={})
    # get the mocked response
    personio = mock_personio()
    with pytest.raises(PersonioError) as e:
        personio.get_employees()
    assert "authorization header" in str(e.value).lower()


# TODO test employee create
@responses.activate
def test_update_employee():
    mock_get_employee()
    mock_update_employee()
    personio = mock_personio()
    employee = personio.get_employee(2040614)

    employee.weekly_working_hours = 30
    d_before = dict(employee)
    updated_employee = employee.update(refresh=False)
    d_after = dict(updated_employee)

    del d_before['last_modified_at']
    del d_after['last_modified_at']
    assert d_after == d_before


def test_resource_equality():
    employee_1 = get_test_employee()
    employee_2 = get_test_employee()
    assert id(employee_1) != id(employee_2)
    assert employee_1 == employee_2
    assert hash(employee_1) == hash(employee_2)


def test_resource_inequality():
    employee_1 = get_test_employee()
    employee_2 = employee_1.model_copy(deep=True)
    employee_2.id = 42
    employee_2.first_name = 'Beta'
    assert employee_1.first_name == 'Ada'
    assert employee_2.first_name == 'Beta'
    assert id(employee_1) != id(employee_2)
    assert employee_1 != employee_2
    assert hash(employee_1) != hash(employee_2)


def test_custom_fields():
    employee = get_test_employee()
    # read custom fields
    assert employee.geburtsland == 'England'
    assert employee.dynamic_1146702 == 'England'
    assert employee._custom_fields['dynamic_1146702'] == 'England'
    assert len([v for v in employee._custom_fields.values() if v]) == 2
    # write to custom fields and validate
    employee.geburtsland = 'UK'
    assert employee.dynamic_1146702 == 'UK'
    employee.dynamic_1146702 = 'British Empire'
    assert employee._custom_fields['dynamic_1146702'] == 'British Empire'
    with pytest.raises(RuntimeError):
        # writing to _custom_fields would not preserve the value, so it's forbidden
        employee._custom_fields['dynamic_1146702'] = 'yolo!'


@responses.activate
def get_test_employee() -> Employee:
    mock_employees()
    personio = mock_personio()
    employees = personio.get_employees()
    return employees[-1]


def mock_employees():
    """mock the get employees endpoint"""
    responses.add(
        method=responses.GET,
        url='https://api.personio.de/v1/company/employees',
        status=200,
        json=load_mock_data('get-employees.json'),
        adding_headers={'Authorization': 'Bearer rotated_dummy_token'})


def mock_get_employee():
    """mock the patch employees endpoint"""
    responses.add(
        method=responses.GET,
        url='https://api.personio.de/v1/company/employees/2040614',
        status=200,
        json=load_mock_data('get-employee-ada.json'),
        adding_headers={'Authorization': 'Bearer rotated_dummy_token'})


def mock_update_employee():
    """mock the patch employees endpoint"""
    responses.add(
        method=responses.PATCH,
        url='https://api.personio.de/v1/company/employees/2040614',
        status=200,
        json=load_mock_data('update-employee.json'),
        adding_headers={'Authorization': 'Bearer rotated_dummy_token'})
