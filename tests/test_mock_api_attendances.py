import responses
import re

from datetime import timedelta, date

from tests.mock_data import json_dict_empty_response, json_dict_attendance_rms
from tests.test_mock_api import compare_labeled_attributes, mock_personio


@responses.activate
def test_get_attendance():
    # mock the get absences endpoint (with different array offsets)
    responses.add(
        responses.GET, re.compile('https://api.personio.de/v1/company/attendances?.*offset=0.*'),
        status=200, json=json_dict_attendance_rms, adding_headers={'Authorization': 'Bearer foo'})
    responses.add(
        responses.GET, re.compile('https://api.personio.de/v1/company/attendances?.*offset=3.*'),
        status=200, json=json_dict_empty_response, adding_headers={'Authorization': 'Bearer bar'})
    # configure personio & get absences for alan
    personio = mock_personio()
    attendances = personio.get_attendances(2116366)
    # validate
    assert len(attendances) == 3
    selection = [a for a in attendances if "release" in a.comment.lower()]
    assert len(selection) == 1
    release = selection[0]
    assert "free software" in release.comment
    assert release.date == date(1985, 3, 20)
    assert release.start_time == timedelta(seconds=11*60*60)
    assert release.end_time == timedelta(seconds=12.5*60*60)
    assert release.break_duration == 60
    assert release.employee_id == 2116366
    # validate serialization
    source_dict = json_dict_attendance_rms['data'][0]
    target_dict = release.to_dict()
    compare_labeled_attributes(source_dict, target_dict)
