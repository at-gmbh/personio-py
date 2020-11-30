from tests.apitest_shared import *

from personio_py import Employee, Attendance, PersonioApiError

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


@skip_if_no_auth
def test_delete_attendance_from_client_id():
    employee_id = shared_test_data['test_employee']['id']
    employee = personio.get_employee(employee_id)
    delete_all_attendances_for_employee(employee)
    attendance = create_attendance_for_user(employee_id, create=True)
    assert len(personio.get_attendances([employee_id])) == 1
    personio.delete_attendance(attendance.id_)
    assert len(personio.get_attendances([employee_id])) == 0


@skip_if_no_auth
def test_delete_attendance_from_client_object_with_id():
    employee_id = shared_test_data['test_employee']['id']
    employee = personio.get_employee(employee_id)
    delete_all_attendances_for_employee(employee)
    attendance = create_attendance_for_user(employee_id, create=True)
    assert len(personio.get_attendances([employee_id])) == 1
    personio.delete_attendance(attendance)
    assert len(personio.get_attendances([employee_id])) == 0


@skip_if_no_auth
def test_delete_attendance_from_client_object_no_id_query():
    employee_id = shared_test_data['test_employee']['id']
    employee = personio.get_employee(employee_id)
    delete_all_attendances_for_employee(employee)
    attendance = create_attendance_for_user(employee_id, create=True)
    assert len(personio.get_attendances([employee_id])) == 1
    attendance.id_ = None
    personio.delete_attendance(attendance, remote_query_id=True)
    assert len(personio.get_attendances([employee_id])) == 0


@skip_if_no_auth
def test_delete_attendance_from_client_object_no_id_no_query():
    employee_id = shared_test_data['test_employee']['id']
    employee = personio.get_employee(employee_id)
    delete_all_attendances_for_employee(employee)
    attendance = create_attendance_for_user(employee_id, create=True)
    assert len(personio.get_attendances([employee_id])) == 1
    attendance.id_ = None
    with pytest.raises(ValueError):
        personio.delete_attendance(attendance, remote_query_id=False)


@skip_if_no_auth
def test_delete_attendance_from_model_no_client():
    employee_id = shared_test_data['test_employee']['id']
    employee = personio.get_employee(employee_id)
    delete_all_attendances_for_employee(employee)
    attendance = create_attendance_for_user(employee_id, create=True)
    assert len(personio.get_attendances([employee_id])) == 1
    attendance.delete()
    with pytest.raises(PersonioApiError):
        personio.delete_attendance(attendance, remote_query_id=False)


@skip_if_no_auth
def test_delete_attendance_from_model_passed_client():
    employee_id = shared_test_data['test_employee']['id']
    employee = personio.get_employee(employee_id)
    delete_all_attendances_for_employee(employee)
    attendance = create_attendance_for_user(employee_id, create=True)
    assert len(personio.get_attendances([employee_id])) == 1
    attendance.delete(client=personio)
    assert len(personio.get_attendances([employee_id])) == 0


@skip_if_no_auth
def test_delete_attendance_from_model_with_client():
    employee_id = shared_test_data['test_employee']['id']
    employee = personio.get_employee(employee_id)
    delete_all_attendances_for_employee(employee)
    attendance = create_attendance_for_user(employee_id, create=True)
    assert len(personio.get_attendances([employee_id])) == 1
    attendance.client = personio
    attendance.delete()
    assert len(personio.get_attendances([employee_id])) == 0


@skip_if_no_auth
def test_add_attendance_id():
    employee_id = shared_test_data['test_employee']['id']
    employee = personio.get_employee(employee_id)
    delete_all_attendances_for_employee(employee)
    attendance = create_attendance_for_user(employee_id, create=True)
    attendance_id = attendance.id_
    attendance_date = attendance.date
    attendance.id_ = None
    assert attendance.id_ is None
    personio._Personio__add_remote_attendance_id(attendance)
    assert attendance.id_ == attendance_id

    # Test error conditions
    attendance.id_ = None
    attendance.employee_id = None
    with pytest.raises(ValueError):
        personio._Personio__add_remote_attendance_id(attendance)
    attendance.employee_id = employee_id
    attendance.date = None
    with pytest.raises(ValueError):
        personio._Personio__add_remote_attendance_id(attendance)
    attendance.date = attendance_date
    attendance.id_ = attendance_id
    attendance.delete(personio)
    with pytest.raises(ValueError):
        personio._Personio__add_remote_attendance_id(attendance)
    attendance_1 = create_attendance_for_user(employee_id, start_time="08:00", end_time="12:00", create=True)
    attendance_2 = create_attendance_for_user(employee_id, start_time="13:00", end_time="17:00", create=True)
    attendance_1.id_ = None
    with pytest.raises(ValueError):
        personio._Personio__add_remote_attendance_id(attendance_1)


def delete_all_attendances_for_employee(employee: Employee):
    attendances = personio.get_attendances([employee.id_])
    for attendance in attendances:
        attendance.delete(personio)


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
