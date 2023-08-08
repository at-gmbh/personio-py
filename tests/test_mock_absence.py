import re
from datetime import date

import pytest
import responses

from personio_py import Absence, Employee, PersonioError, ShortEmployee
from tests.test_mock import load_mock_data
from tests.test_mock_employee import compare_labeled_attributes, mock_employees, mock_personio


@responses.activate
def test_get_absence_types():
    mock_absence_types()
    # configure personio & get absences for alan
    personio = mock_personio()
    absence_types = personio.get_absence_types()
    # non-empty contents
    assert len(absence_types) == 3
    for at in absence_types:
        assert at.id > 0
        assert at.name


@responses.activate
def test_get_absences():
    # configure personio & get absences for alan
    mock_get_absences()
    personio = mock_personio()
    absences = personio.get_absences(2116365)
    # validate
    assert len(absences) == 3
    selection = [a for a in absences if "marathon" in a.comment.lower()]
    assert len(selection) == 1
    marathon = selection[0]
    assert marathon.start_date == date(1944, 9, 1)
    assert marathon.half_day_start == 0
    assert marathon.half_day_end == 1
    assert marathon.status == 'approved'


@responses.activate
def test_get_absences_from_employee_objects():
    # mock endpoints & get absences for all employees
    mock_employees()
    mock_get_absences()
    personio = mock_personio()
    employees = personio.get_employees()
    assert employees
    absences = personio.get_absences(employees)
    # the response is not important (it does not match the input), but the function should accept
    # a list of Employee objects as parameter and return a result
    assert absences


@responses.activate
def test_get_absence_from_id():
    personio = mock_personio()
    mock_get_absence_id()
    absence_id_only = Absence(id=17205942)
    absence = personio.get_absence(absence_id_only)
    assert absence.employee.first_name == 'Alan'
    assert absence.employee.last_name == 'Turing'
    assert absence.id == 17205942
    assert absence.start_date == date(1944, 9, 1)
    assert absence.end_date == date(1944, 9, 1)


@responses.activate
def test_get_absence_from_object_without_id():
    personio = mock_personio()
    mock_get_absence_id()
    mock_get_absences_single()
    # get all properties of this absence object
    target = personio.get_absence(17205942)
    search = target.model_copy()
    search.id = None
    # now find this absence without knowing its ID
    absence = personio.get_absence(search)
    assert absence == target


@responses.activate
def test_serialization():
    mock_get_absences()
    personio = mock_personio()
    absence = personio.get_absences(2116365)[0]
    serialized = absence.to_api_dict()
    assert serialized['employee_id'] == absence.employee.id
    assert serialized['start_date'] == absence.start_date.isoformat()
    assert serialized['end_date'] == absence.end_date.isoformat()


@responses.activate
def test_create_absence():
    mock_absence_types()
    mock_create_absence()
    personio = mock_personio()
    absence_type = personio.get_absence_types()[0]
    employee = ShortEmployee(
        id=2116365,
        first_name="Alan",
        last_name='Turing',
        email='alan.turing@cetitec.com'
    )
    absence = Absence(
        employee=employee,
        start_date=date(2020, 1, 1),
        end_date=date(2020, 1, 10),
        half_day_start=False,
        half_day_end=False,
        time_off_type=absence_type)
    absence.create()
    assert absence.id


@responses.activate
def test_delete_absence():
    mock_delete_absence()
    personio = mock_personio()
    result = personio.delete_absence(2116365)
    assert result is True


@responses.activate
def test_delete_absence_no_id():
    personio = mock_personio()
    mock_get_absences()
    absence = personio.get_absences(2116365)[0]
    absence.id = None
    with pytest.raises(PersonioError):
        absence.delete()
    with pytest.raises(PersonioError):
        personio.delete_absence(absence)


def mock_absence_types():
    """mock the get absence types endpoint"""
    responses.add(
        method=responses.GET,
        url='https://api.personio.de/v1/company/time-off-types',
        status=200,
        json=load_mock_data('get-absence-types.json'),
        adding_headers={'Authorization': 'Bearer rotated_dummy_token'})


def mock_get_absences():
    """mock the get absences endpoint"""
    responses.add(
        method=responses.GET,
        url=re.compile('https://api.personio.de/v1/company/time-offs?.*offset.*'),
        status=200,
        json=load_mock_data('get-absence-alan-many.json'),
        adding_headers={'Authorization': 'Bearer rotated_dummy_token'})


def mock_get_absences_single():
    """mock the get absences endpoint (only a single result)"""
    responses.add(
        method=responses.GET,
        url=re.compile('https://api.personio.de/v1/company/time-offs?.*offset.*'),
        status=200,
        json=load_mock_data('get-absence-alan-one.json'),
        adding_headers={'Authorization': 'Bearer rotated_dummy_token'})


def mock_get_absences_missing():
    """mock the get absences endpoint (empty result)"""
    responses.add(
        method=responses.GET,
        url=re.compile('https://api.personio.de/v1/company/time-offs?.*'),
        status=200,
        json=load_mock_data('success.json'),
        adding_headers={'Authorization': 'Bearer rotated_dummy_token'})


def mock_get_absence_id():
    """mock the get absences endpoint (only a single result)"""
    responses.add(
        method=responses.GET,
        url=re.compile('https://api.personio.de/v1/company/time-offs/.*'),
        status=200,
        json=load_mock_data('get-absence-id.json'),
        adding_headers={'Authorization': 'Bearer rotated_dummy_token'})


def mock_delete_absence():
    """mock the delete absence endpoint"""
    responses.add(
        method=responses.DELETE,
        url=re.compile('https://api.personio.de/v1/company/time-offs/.*'),
        status=200,
        json=load_mock_data('delete-absence.json'),
        adding_headers={'Authorization': 'Bearer rotated_dummy_token'})


def mock_create_absence():
    """mock the create absence endpoint"""
    responses.add(
        method=responses.POST,
        url='https://api.personio.de/v1/company/time-offs',
        status=200,
        json=load_mock_data('create-absence.json'),
        adding_headers={'Authorization': 'Bearer rotated_dummy_token'})
