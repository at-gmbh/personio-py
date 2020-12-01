from datetime import date

import pytest
import responses
import re

from personio_py import PersonioError
from tests.test_mock_api import mock_personio, compare_labeled_attributes, mock_employees
from tests.mock_data import json_dict_empty_response
from tests.test_mock_api_absence_data import json_dict_absence_alan, json_dict_absence_types, json_dict_delete_absence, \
    json_dict_absence_alan_first


@responses.activate
def test_delete_absence():
    mock_delete_absence()
    personio = mock_personio()
    result = personio.delete_absence(2116365)
    assert result is True

    mock_absences()
    absence = personio.get_absences(2116365)[0]
    absence.delete()
    absence.client = None
    with pytest.raises(PersonioError):
        absence.delete()
    absence.delete(client=personio)
    absence.client = personio
    absence.id_ = None
    with pytest.raises(ValueError):
        absence.delete()
    with pytest.raises(ValueError):
        personio.delete_absence(None)


@responses.activate
def test_delete_absence_remote_query():
    mock_single_absences()
    personio = mock_personio()
    absence = personio.get_absences(111222333)[0]
    absence.id_ = None
    mock_delete_absence()
    personio.delete_absence(absence, remote_query_id=True)
    absence.id_ = None
    start_date = absence.start_date
    absence.start_date = None
    with pytest.raises(ValueError):
        personio.delete_absence(absence, remote_query_id=True)
    absence.start_date = start_date
    end_date = absence.end_date
    absence.end_date = None
    with pytest.raises(ValueError):
        personio.delete_absence(absence, remote_query_id=True)
    absence.end_date = end_date
    employee = absence.employee
    absence.employee = None
    with pytest.raises(ValueError):
        personio.delete_absence(absence, remote_query_id=True)
    absence.employee = employee
    responses.reset()
    mock_absences()
    personio = mock_personio()
    with pytest.raises(ValueError):
        personio.delete_absence(absence, remote_query_id=True)
    responses.reset()
    mock_no_absences()
    personio = mock_personio()
    with pytest.raises(ValueError):
        personio.delete_absence(absence, remote_query_id=True)



@responses.activate
def test_get_absences():
    # configure personio & get absences for alan
    mock_absences()
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
    # validate serialization
    source_dict = json_dict_absence_alan['data'][0]
    target_dict = marathon.to_dict()
    compare_labeled_attributes(source_dict, target_dict)


@responses.activate
def test_get_absences_from_employee_objects():
    # mock endpoints & get absences for all employees
    mock_employees()
    mock_absences()
    personio = mock_personio()
    employees = personio.get_employees()
    assert employees
    absences = personio.get_absences(employees)
    # the response is not important (it does not match the input), but the function should accept
    # a list of Employee objects as parameter and return a result
    assert absences


@responses.activate
def test_get_absence_types():
    # mock the get absence types endpoint
    responses.add(
        responses.GET, 'https://api.personio.de/v1/company/time-off-types', status=200,
        json=json_dict_absence_types, adding_headers={'Authorization': 'Bearer foo'})
    # configure personio & get absences for alan
    personio = mock_personio()
    absence_types = personio.get_absence_types()
    # non-empty contents
    assert len(absence_types) == 3
    for at in absence_types:
        assert at.id_ > 0
        assert isinstance(at.name, str)
    # serialization matches input
    for source_dict, at in zip(json_dict_absence_types['data'], absence_types):
        target_dict = at.to_dict()
        assert source_dict == target_dict


def mock_absences():
    # mock the get absences endpoint (with different array offsets)
    responses.add(
        responses.GET, re.compile('https://api.personio.de/v1/company/time-offs?.*offset=0.*'),
        status=200, json=json_dict_absence_alan, adding_headers={'Authorization': 'Bearer foo'})
    responses.add(
        responses.GET, re.compile('https://api.personio.de/v1/company/time-offs?.*offset=3.*'),
        status=200, json=json_dict_empty_response, adding_headers={'Authorization': 'Bearer bar'})


def mock_single_absences():
    # mock the get absences endpoint (with different array offsets)
    responses.add(
        responses.GET, re.compile('https://api.personio.de/v1/company/time-offs?.*offset=0.*'),
        status=200, json=json_dict_absence_alan_first, adding_headers={'Authorization': 'Bearer foo'})
    responses.add(
        responses.GET, re.compile('https://api.personio.de/v1/company/time-offs?.*offset=1.*'),
        status=200, json=json_dict_empty_response, adding_headers={'Authorization': 'Bearer bar'})


def mock_no_absences():
    # mock the get absences endpoint
    responses.add(
        responses.GET, re.compile('https://api.personio.de/v1/company/time-offs?.*offset=0.*'),
        status=200, json=json_dict_empty_response, adding_headers={'Authorization': 'Bearer bar'})


def mock_delete_absence():
    # mock the delete endpoint
    responses.add(
        responses.DELETE,  re.compile('https://api.personio.de/v1/company/time-offs/*'),
        status=200, json=json_dict_delete_absence, adding_headers={'Authorization': 'Bearer bar'})
