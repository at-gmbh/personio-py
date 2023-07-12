import re
from datetime import date, time

import responses

from personio_py import Attendance, Employee
from tests.test_mock import load_mock_data, mock_personio


@responses.activate
def test_create_attendance():
    mock_create_attendance()
    mock_personio()
    employee = Employee(
        id=2116365,
        first_name='Alan',
        last_name='Turing',
        email='alan.turing@cetitec.com')
    attendance = Attendance(
        employee=employee.id,
        date=date(2020, 1, 10),
        start_time="09:00",
        end_time="17:00",
        break_duration=0)
    attendance.create()
    assert attendance.id


@responses.activate
def test_get_attendance():
    mock_attendances()
    # configure personio & get absences for alan
    personio = mock_personio()
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
    assert release.break_duration == 60
    assert release.employee == 2116366


@responses.activate
def test_patch_attendances():
    mock_attendances()
    mock_patch_attendance()
    personio = mock_personio()
    attendances = personio.get_attendances(2116366)
    attendance_to_patch = attendances[0]
    attendance_to_patch.break_duration = 1
    personio.update_attendance(attendance_to_patch)


@responses.activate
def test_delete_attendances():
    mock_attendances()
    mock_delete_attendance()
    personio = mock_personio()
    attendances = personio.get_attendances(2116366)
    attendance_to_delete = attendances[0]
    personio.delete_attendance(attendance_to_delete)


def mock_attendances():
    # mock the get absences endpoint (with different array offsets)
    responses.add(
        responses.GET,
        re.compile('https://api.personio.de/v1/company/attendances?.*'),
        status=200,
        json=load_mock_data('get-attendance.json'),
        adding_headers={'Authorization': 'Bearer foo'})


def mock_create_attendance():
    responses.add(
        responses.POST,
        'https://api.personio.de/v1/company/attendances',
        status=200,
        json=load_mock_data('create-attendance-no-break.json'),
        adding_headers={'Authorization': 'Bearer bar'})


def mock_patch_attendance():
    responses.add(
        responses.PATCH,
        'https://api.personio.de/v1/company/attendances/33479712',
        status=200,
        json=load_mock_data("update-attendance.json"),
        adding_headers={'Authorization': 'Bearer bar'})


def mock_delete_attendance():
    responses.add(
        responses.DELETE,
        'https://api.personio.de/v1/company/attendances/33479712',
        status=200,
        json=load_mock_data('delete-attendance.json'),
        adding_headers={'Authorization': 'Bearer bar'})
