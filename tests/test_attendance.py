from datetime import date, timedelta

import pytest

from personio_py import Attendance

attendance_dict = {
    'id': 42200,
    'type': 'AttendancePeriod',
    'attributes': {
        'employee': 42,
        'date': '1835-06-01',
        'start_time': '09:00',
        'end_time': '17:00',
        'break': 60,
        'comment': 'great progress today :)',
        'is_holiday': False,
        'is_on_time_off': False
    }
}


def test_parse_attendance():
    attendance = Attendance.from_dict(attendance_dict)
    assert attendance
    assert attendance.id_ == 42200
    assert attendance.employee_id == 42
    assert attendance.comment == 'great progress today :)'
    assert attendance.date == date(1835, 6, 1)
    assert attendance.start_time == timedelta(hours=9, minutes=0)
    assert attendance.end_time == timedelta(hours=17, minutes=0)


@pytest.mark.skip(reason="wip")
def test_serialize_attendance():
    # TODO needs fixing. should probably change the way from/to dict works
    attendance = Attendance.from_dict(attendance_dict)
    d = attendance.to_dict()
    assert d == attendance_dict
