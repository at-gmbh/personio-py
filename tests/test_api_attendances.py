from tests.apitest_shared import *

from personio_py import Employee, Attendance

from datetime import datetime


@skip_if_no_auth
def test_create_attendances():
    employee_id = shared_test_data['test_employee']['id']
    employee = personio.get_employee(employee_id)
    delete_all_attendances_for_employee(employee)
    attendances = personio.get_attendances([employee_id])
    assert len(attendances) == 0
    create_attendance_for_user(employee_id, create=True)
    attendances = personio.get_attendances([employee_id])
    assert len(attendances) == 1


def delete_all_attendances_for_employee(employee: Employee, date: datetime = None):
    if not date:
        date = datetime(2020, 1, 1)
    attendances = personio.get_attendances([employee.id_], start_date=date, end_date=date)
    for attendance in attendances:
        personio.delete_attendance(attendance)


def prepare_test_get_attendances() -> Employee:
    test_data = shared_test_data['test_employee']
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
                 create: bool = False):
    if not date:
        date = datetime(2021, 1, 1)
    if not start_time:
        start_time = "08:00"
    if not end_time:
        end_time = "17:00"

    attendance_to_create = Attendance(
        employee_id=employee_id,
        date=date,
        start_time=start_time,
        end_time=end_time,
        break_duration=break_duration,
        comment=comment,
        is_holiday=is_holiday,
        is_on_time_off=is_on_time_off
    )
    if create:
        attendance_to_create.create(personio)
    return attendance_to_create
