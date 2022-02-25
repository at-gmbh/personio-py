import re
from datetime import date, time

import responses

from tests.test_mock import load_mock_data, mock_personio


@responses.activate
def test_get_attendance():
    # mock the get attendance endpoint
    mock_attendances()
    personio = mock_personio()
    # get attendances
    attendances = personio.get_attendances(2116366)
    # validate
    assert len(attendances) == 3
    selection = [a for a in attendances if "release" in a.comment.lower()]
    assert len(selection) == 1
    release = selection[0]
    assert "free software" in release.comment
    assert release.day == date(1985, 3, 20)
    assert release.start_time == time(hour=11)
    assert release.end_time == time(hour=12, minute=30)
    assert release.break_minutes == 60
    assert release.employee == 2116366
    assert release.dict()


def mock_attendances():
    """mock the get employees endpoint"""
    responses.add(
        method=responses.GET,
        url=re.compile('https://api.personio.de/v1/company/attendances.*'),
        status=200,
        json=load_mock_data('get-attendance-rms.json'),
        adding_headers={'Authorization': 'Bearer rotated_dummy_token'})
