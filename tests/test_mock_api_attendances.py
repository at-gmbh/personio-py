import responses
import re

from datetime import timedelta, date, datetime

from personio_py import Attendance, Employee

from tests.mock_data import json_dict_attendance_create_no_break, \
    json_dict_attendance_rms, json_dict_attendance_patch, json_dict_attendance_delete
from tests.test_mock_api import compare_labeled_attributes, mock_personio

@responses.activate
def test_create_attendance():
    mock_create_attendance()
    personio = mock_personio()
    employee = Employee(
        first_name="Alan",
        last_name='Turing',
        email='alan.turing@cetitec.com'
    )
    attendance = Attendance(
        client=personio,
        employee=employee,
        date=date(2020, 1, 10),
        #start_time = "09:00",
        #end_time = "17:00"
        start_time=timedelta(hours=datetime.strptime("09:00", "%H:%M").hour, minutes=datetime.strptime("09:00", "%H:%M").minute),
        end_time=timedelta(hours=datetime.strptime("17:00", "%H:%M").hour, minutes=datetime.strptime("17:00", "%H:%M").minute),
        break_duration=0
        )
    attendance.create()
    assert attendance.id_

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
    assert release.date == date(1985, 3, 20)
    assert release.start_time == timedelta(seconds=11*60*60)
    assert release.end_time == timedelta(seconds=12.5*60*60)
    assert release.break_duration == 60
    assert release.employee_id == 2116366
    # validate serialization
    source_dict = json_dict_attendance_rms['data'][0]
    target_dict = release.to_dict()
    compare_labeled_attributes(source_dict, target_dict)

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
        responses.GET, re.compile('https://api.personio.de/v1/company/attendances?.*'),
        status=200, json=json_dict_attendance_rms, adding_headers={'Authorization': 'Bearer foo'})

def mock_create_attendance():
    responses.add(
        responses.POST,  'https://api.personio.de/v1/company/attendances',
        status=200, json=json_dict_attendance_create_no_break, adding_headers={'Authorization': 'Bearer bar'})

def mock_patch_attendance():
    responses.add(
        responses.PATCH,  'https://api.personio.de/v1/company/attendances/33479712',
        status=200, json=json_dict_attendance_patch, adding_headers={'Authorization': 'Bearer bar'})

def mock_delete_attendance():
    responses.add(
        responses.DELETE,  'https://api.personio.de/v1/company/attendances/33479712',
        status=200, json=json_dict_attendance_delete, adding_headers={'Authorization': 'Bearer bar'})
