import json
import re
from datetime import date, datetime, timedelta
from functools import lru_cache
from typing import Any, Dict

import pytest
import responses

from personio_py import Personio, PersonioApiError
from tests import resource_dir

# from pydantic.datetime_parse import parse_duration


iso_date_match = re.compile(r'\d\d\d\d-\d\d-\d\d')
timedelta_match = re.compile(r'\d\d:\d\d')


def test_load_mock_data():
    # see if we can load json data from the test folder
    data = load_mock_data('success.json')
    assert data
    assert data['success'] is True


@responses.activate
def test_authenticate_ok():
    # mock a successful authentication response
    resp_json = {'success': True, 'data': {'token': 'dummy_token'}}
    responses.add(responses.POST, 'https://api.personio.de/v1/auth', json=resp_json, status=200)
    # authenticate
    personio = Personio(client_id='test', client_secret='test')
    personio.authenticate()
    # validate
    assert personio.authenticated is True
    assert personio.headers['Authorization'] == "Bearer dummy_token"


@responses.activate
def test_authenticate_fail():
    # mock a failed authentication response
    resp_json = {'success': False, 'error': {'code': 0, 'message': 'Wrong credentials'}}
    responses.add(responses.POST, 'https://api.personio.de/v1/auth', json=resp_json, status=403)
    # try to authenticate
    personio = Personio(client_id='test', client_secret='test')
    with pytest.raises(PersonioApiError) as e:
        personio.authenticate()
    assert "Wrong credentials" in str(e.value)
    assert personio.authenticated is False


@lru_cache(maxsize=None)
def load_mock_data(file: str) -> Dict:
    """
    Load JSON data from the `tests/res` folder

    :param file: name of the file to load
    :return: the json content of the file as Python dict
    """
    with (resource_dir / file).open('r') as fp:
        return json.load(fp)


def mock_personio() -> Personio:
    """
    mock the authentication endpoint, the custom attributes endpoint
    and create a new Personio instance
    """
    resp_json = {'success': True, 'data': {'token': 'dummy_token'}}
    responses.add(responses.POST, 'https://api.personio.de/v1/auth', json=resp_json, status=200)
    mock_custom_attributes()
    return Personio(client_id='test', client_secret='test')


def mock_custom_attributes():
    """mock the custom attributes API endpoint"""
    responses.add(
        method=responses.GET,
        url='https://api.personio.de/v1/company/employees/custom-attributes',
        status=200,
        json=load_mock_data('get-custom-attributes.json'))


def compare_labeled_attributes(expected: Dict, actual: Dict):
    if actual == expected:
        # fast lane - exact match
        return
    # let's see if there is any significant difference...
    attr_expected = expected['attributes']
    attr_actual = actual['attributes'] if 'attributes' in actual else actual
    keys = sorted(set(attr_expected.keys()) | {k for k, v in attr_actual.items() if v})
    # check every item
    for key in keys:
        val_expected = get_serialized_value(attr_expected, key)
        # skip none values (these are not serialized)
        if val_expected is not None:
            val_actual = get_serialized_value(attr_actual, key)
            if isinstance(val_expected, list):
                for exp, act in zip(*(val_expected, val_actual)):
                    compare_serialized_values(exp, act)
            else:
                compare_serialized_values(val_expected, val_actual)


def compare_serialized_values(expected: Any, actual: Any):
    if isinstance(expected, dict):
        # another dict? recur
        compare_labeled_attributes(expected, actual)
    elif isinstance(expected, str):
        expected = expected.strip()
        if expected != actual:
            if not expected:
                # empty string expected? -> match any falsey result (None, empty string, etc.)
                assert not actual
            elif iso_date_match.match(expected):
                # match ISO dates (only the date part, not time)
                expected_date = date.fromisoformat(expected[:10])
                actual_date = actual.date() if isinstance(actual, datetime) else actual
                assert actual_date == expected_date
            elif timedelta_match.match(expected):
                # match timedelta strings
                expected_timedelta = parse_duration(f'{expected}:00')
                assert actual == expected_timedelta
            else:
                # match the entire string
                assert actual == expected
    else:
        assert actual == expected


def parse_duration(duration):
    dt = datetime.strptime(duration, "%H:%M:%S")
    total_sec = dt.hour*3600 + dt.minute*60 + dt.second
    td = timedelta(seconds=total_sec)
    return td


def compare_dates(expected: date, actual: Any):
    assert actual.isoformat()[:10] == expected.isoformat()[:10]


def get_serialized_value(d: Dict, key: str):
    # two possible structures here: d[key]['value'] or just d['key']
    val = d[key]
    if isinstance(val, dict) and 'value' in val:
        return val['value']
    else:
        return val
