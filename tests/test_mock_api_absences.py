from datetime import date

import responses
import re

from tests.test_mock_api import mock_personio, compare_labeled_attributes, mock_employees
from tests.mock_data import json_dict_empty_response
from tests.test_mock_api_absence_data import json_dict_absence_alan, json_dict_absence_types


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
