from datetime import datetime, time

from personio_py import Employee, Attendance
from tests.apitest_shared import *


@skip_if_no_auth
def test_get_attendances():
    employee = get_test_employee_for_attendances()
    attendances = personio.get_attendances(employee)
    assert len(attendances) == 11
    assert isinstance(attendances[0], Attendance)
    assert attendances[0].id_ == 162804610
    assert attendances[0].employee_id == employee.id_
    assert attendances[0]._client == personio


@skip_if_no_auth
def test_create_attendances():
    employee_id = get_test_employee().id_
    employee = personio.get_employee(employee_id)
    delete_all_attendances_for_employee(employee)
    attendances = personio.get_attendances([employee_id])
    assert len(attendances) == 0
    created_attendance = create_attendance_for_user(employee_id, create=True)
    attendances = personio.get_attendances([employee_id])
    assert len(attendances) == 1
    personio.delete_attendance(created_attendance.id_)


@skip_if_no_auth
def test_delete_attendance_from_client_id():
    employee_id = get_test_employee().id_
    employee = personio.get_employee(employee_id)
    delete_all_attendances_for_employee(employee)
    attendance = create_attendance_for_user(employee_id, create=True)
    assert len(personio.get_attendances([employee_id])) == 1
    personio.delete_attendance(attendance.id_)
    assert len(personio.get_attendances([employee_id])) == 0


@skip_if_no_auth
def test_delete_attendance_from_client_object_with_id():
    employee_id = get_test_employee().id_
    employee = personio.get_employee(employee_id)
    delete_all_attendances_for_employee(employee)
    attendance = create_attendance_for_user(employee_id, create=True)
    assert len(personio.get_attendances([employee_id])) == 1
    personio.delete_attendance(attendance)
    assert len(personio.get_attendances([employee_id])) == 0


@skip_if_no_auth
def test_delete_attendance_from_model_passed_client():
    employee_id = get_test_employee().id_
    employee = personio.get_employee(employee_id)
    delete_all_attendances_for_employee(employee)
    attendance = create_attendance_for_user(employee_id, create=True)
    assert len(personio.get_attendances([employee_id])) == 1
    attendance.delete(client=personio)
    assert len(personio.get_attendances([employee_id])) == 0


@skip_if_no_auth
def test_delete_attendance_from_model_with_client():
    employee_id = get_test_employee().id_
    employee = personio.get_employee(employee_id)
    delete_all_attendances_for_employee(employee)
    attendance = create_attendance_for_user(employee_id, create=True)
    assert len(personio.get_attendances([employee_id])) == 1
    attendance._client = personio
    attendance.delete()
    assert len(personio.get_attendances([employee_id])) == 0


def delete_all_attendances_for_employee(employee: Employee):
    attendances = personio.get_attendances([employee.id_])
    for attendance in attendances:
        attendance.delete(personio)


def prepare_test_get_attendances() -> Employee:
    test_data = get_test_employee()
    test_user = personio.get_employee(test_data['id'])

    # Be sure there are no leftover attendances
    delete_all_attendances_for_employee(test_user)
    return test_user


def create_attendance_for_user(
                 employee_id: int,
                 date: datetime = None,
                 start_time: str = None,
                 end_time: str = None,
                 break_duration: int = None,
                 comment: str = None,
                 is_holiday: bool = None,
                 is_on_time_off: bool = None,
                 updated_at: datetime = None,
                 status: str = None,
                 project: int = None,
                 create: bool = False):
    if not date:
        date = datetime(2021, 1, 1)
    if not start_time:
        start_time = time(9)
    if not end_time:
        end_time = time(17)

    attendance_to_create = Attendance(
        employee_id=employee_id,
        date=date,
        start_time=start_time,
        end_time=end_time,
        break_duration=break_duration,
        comment=comment,
        is_holiday=is_holiday,
        is_on_time_off=is_on_time_off,
        updated_at=updated_at,
        status=status,
        project=project
    )
    if create:
        attendance_to_create.create(personio)
    return attendance_to_create
