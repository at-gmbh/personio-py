import re
import responses

from tests.mock_data import json_dict_empty_response
from tests.mock.absence_data import json_dict_absence_alan, json_dict_absence_alan_first, \
    json_dict_delete_absence, json_dict_absence_create_no_halfdays, json_dict_absence_types, json_dict_get_absence


def mock_absence_types():
    # mock the get absence types endpoint
    responses.add(
        responses.GET, 'https://api.personio.de/v1/company/time-off-types', status=200,
        json=json_dict_absence_types, adding_headers={'Authorization': 'Bearer foo'})


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


def mock_create_absence_no_halfdays():
    responses.add(
        responses.POST,  'https://api.personio.de/v1/company/time-offs',
        status=200, json=json_dict_absence_create_no_halfdays, adding_headers={'Authorization': 'Bearer bar'})


def mock_get_absence():
    responses.add(
        responses.GET, re.compile('https://api.personio.de/v1/company/time-offs/.*'),
        status=200, json=json_dict_get_absence, adding_headers={'Authorization': 'Bearer bar'})
