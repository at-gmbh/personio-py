from datetime import datetime, time
from functools import lru_cache

from personio_py import Attendance, Employee
from tests import connection
from tests.connection import get_skipif, personio

skip_if_no_auth = get_skipif()


@skip_if_no_auth
def test_get_attendances():
    employee = get_test_employee_for_attendances()
    attendances = personio.get_attendances(employee)
    assert attendances
    assert isinstance(attendances[0], Attendance)
    assert attendances[0].id == 162804610
    assert attendances[0].employee == employee.id


@skip_if_no_auth
def test_create_attendances():
    employee_id = connection.get_test_employee().id
    employee = personio.get_employee(employee_id)
    delete_all_attendances_for_employee(employee)
    attendances = personio.get_attendances([employee_id])
    assert len(attendances) == 0
    created_attendance = create_attendance_for_user(employee_id, create=True)
    attendances = personio.get_attendances([employee_id])
    assert len(attendances) == 1
    personio.delete_attendance(created_attendance.id)


@skip_if_no_auth
def test_update_attendace():
    employee = get_test_employee_for_attendances()
    attendance = personio.get_attendances(employee)[0]
    assert attendance
    attendance.break_duration = 15
    updated_attendance = attendance.update()
    assert updated_attendance.break_duration == attendance.break_duration
    # attendance.start_time = time(9)
    # start_time can't be updated probably due to a bug.
    # message: Existing overlapping attendances periods
    attendance.end_time = time(18)
    updated_attendance = attendance.update()
    assert updated_attendance.end_time == attendance.end_time


@skip_if_no_auth
def test_get_employee_for_attendace():
    employee = get_test_employee_for_attendances()
    attendances = personio.get_attendances(employee)
    for attendance in attendances:
        attendee = attendance.get_employee()
        assert attendee == employee


@skip_if_no_auth
def test_delete_attendance_from_client_id():
    employee_id = connection.get_test_employee().id
    employee = personio.get_employee(employee_id)
    delete_all_attendances_for_employee(employee)
    attendance = create_attendance_for_user(employee_id, create=True)
    assert len(personio.get_attendances([employee_id])) == 1
    personio.delete_attendance(attendance.id)
    assert len(personio.get_attendances([employee_id])) == 0


@skip_if_no_auth
def test_delete_attendance_from_client_object_with_id():
    employee_id = connection.get_test_employee().id
    employee = personio.get_employee(employee_id)
    delete_all_attendances_for_employee(employee)
    attendance = create_attendance_for_user(employee_id, create=True)
    assert len(personio.get_attendances([employee_id])) == 1
    personio.delete_attendance(attendance)
    assert len(personio.get_attendances([employee_id])) == 0


@skip_if_no_auth
def test_delete_attendance_from_model_passed_client():
    employee_id = connection.get_test_employee().id
    employee = personio.get_employee(employee_id)
    delete_all_attendances_for_employee(employee)
    attendance = create_attendance_for_user(employee_id, create=True)
    assert len(personio.get_attendances([employee_id])) == 1
    attendance.delete()
    assert len(personio.get_attendances([employee_id])) == 0


def delete_all_attendances_for_employee(employee: Employee):
    attendances = personio.get_attendances([employee.id])
    for attendance in attendances:
        attendance.delete()


def prepare_test_get_attendances() -> Employee:
    test_data = connection.get_test_employee()
    test_user = personio.get_employee(test_data['id'])

    # Be sure there are no leftover attendances
    delete_all_attendances_for_employee(test_user)
    return test_user


def create_attendance_for_user(employee_id: int,
                               date: datetime = None,
                               start_time: str = None,
                               end_time: str = None,
                               break_duration: int = None,
                               comment: str = None,
                               is_holiday: bool = None,
                               is_on_time_off: bool = None,
                               create: bool = False):
    if not date:
        date = datetime(2021, 1, 1)
    if not start_time:
        start_time = "08:00"
    if not end_time:
        end_time = "17:00"

    attendance_to_create = Attendance(
        employee=employee_id,
        date=date,
        start_time=start_time,
        end_time=end_time,
        break_duration=break_duration,
        comment=comment,
        is_holiday=is_holiday,
        is_on_time_off=is_on_time_off
    )
    if create:
        attendance_to_create.create()
    return attendance_to_create


@lru_cache(maxsize=1)
def get_test_employee_for_attendances():
    return personio.get_employee(13603465)
