from datetime import date, timedelta, datetime, timezone

from personio_py import Attendance, Project

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
        'is_on_time_off': False,
        'status': 'confirmed',
        'updated_at': '2017-01-17T16:41:08+00:00',
        'project': {
          'id': 567
        }
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
    assert attendance.status == 'confirmed'
    assert attendance.updated_at == datetime(2017, 1, 17, 16, 41, 8, tzinfo=timezone.utc)
    assert attendance.project == {"id": 567}

def test_serialize_attendance():
    attendance = Attendance.from_dict(attendance_dict)
    d = attendance.to_dict()
    assert d == attendance_dict
