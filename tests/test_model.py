from copy import deepcopy
from datetime import datetime, timedelta, timezone

from personio_py import Absence, Attendance, DynamicAttr, Employee
from personio_py.mapping import DynamicMapping

employee_dict = {
    'id': {'label': 'ID', 'value': 42},
    'first_name': {'label': 'First name', 'value': 'Ada'},
    'last_name': {'label': 'Last name', 'value': 'Lovelace'},
    'email': {'label': 'Email', 'value': 'ada@example.org'},
    'gender': {'label': 'Gender', 'value': 'female'},
    'status': {'label': 'Status', 'value': 'deceased'},
    'position': {'label': 'Position', 'value': 'first programmer ever'},
    'created_at': {'label': 'created_at', 'value': '1835-01-02T13:00:00+00:00'},
    'dynamic_42': {'label': 'quote', 'value':
        "The Analytical Engine has no pretensions whatever to originate anything. "
        "It can do whatever we know how to order it to perform."},
    'dynamic_43': {'label': 'birthday', 'value': '1815-12-10T00:00:00+00:00'},
    'dynamic_44': {'label': 'hobbies', 'value': 'math,analytical thinking,music'},
}

dyn_mapping = [
    DynamicMapping(field_id=43, alias='birthday', data_type=datetime),
    DynamicMapping(field_id=44, alias='hobbies', data_type=list),
]

absence_dict = {
    'id': 42100,
    'status': 'approved',
    'comment': 'Christmas <3',
    'start_date': '1835-12-24T00:00:00+00:00',
    'end_date': '1835-12-31T00:00:00+00:00',
    'days_count': 5,
    'half_day_start': 0,
    'half_day_end': 0,
    'time_off_type': {'type': 'TimeOffType', 'attributes': {'id': 1, 'name': 'vacation'}},
    'employee': {
        'type': 'Employee',
        'attributes': {
            'id': {'label': 'ID', 'value': 42},
            'first_name': {'label': 'First name', 'value': 'Ada'},
            'last_name': {'label': 'Last name', 'value': 'Lovelace'},
            'email': {'label': 'Email', 'value': 'ada@example.org'}
        }
    },
    'created_by': 'Ada Lovelace',
    'certificate': {'status': 'not-required'},
    'created_at': '1835-12-01T13:15:00+00:00'
}

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


def test_dynamic_attr():
    dyn_43_dict = employee_dict['dynamic_43']
    dyn_attr = DynamicAttr.from_dict('dynamic_43', dyn_43_dict)
    assert dyn_attr.field_id == 43
    assert dyn_attr.label == 'birthday'
    assert dyn_attr.value == '1815-12-10T00:00:00+00:00'
    d = dyn_attr.to_dict()
    assert d == dyn_43_dict


def test_dynamic_attr_list():
    dyn_attrs = DynamicAttr.from_attributes(employee_dict)
    assert len(dyn_attrs) == 3
    attr_dict = DynamicAttr.to_attributes(dyn_attrs)
    assert 'dynamic_42' in attr_dict
    assert 'dynamic_43' in attr_dict


def test_map_types():
    kwargs = Employee._map_fields(employee_dict)
    assert kwargs['id_'] == 42
    assert kwargs['dynamic']
    assert kwargs['dynamic'][1].label == 'birthday'


def test_parse_employee():
    employee = Employee.from_dict(employee_dict)
    assert employee.id_ == 42
    assert len(employee.dynamic_raw) == 3
    assert employee.first_name == 'Ada'
    assert employee.created_at == datetime(1835, 1, 2, 13, 0, 0, tzinfo=timezone.utc)
    serialized = employee.to_dict()
    assert serialized


def test_parse_employee_dyn_typed():
    employee = Employee.from_dict(employee_dict, dynamic_fields=dyn_mapping)
    assert employee.dynamic
    assert employee.dynamic['birthday'] == datetime(1815, 12, 10, 0, 0, 0, tzinfo=timezone.utc)
    assert employee.dynamic['hobbies'] == ['math', 'analytical thinking', 'music']
    assert len(employee.dynamic_raw) == 3


def test_parse_employee_dyn_changes():
    employee = Employee.from_dict(employee_dict, dynamic_fields=dyn_mapping)
    employee.dynamic['hobbies'].append('horse races')
    assert 'horse races' in employee.dynamic['hobbies']
    d = employee.to_dict()
    assert d['dynamic_44']['value'] == 'math,analytical thinking,music,horse races'


def test_serialize_employee():
    employee = Employee.from_dict(employee_dict, dynamic_fields=dyn_mapping)
    d = employee.to_dict()
    assert d == employee_dict


def test_tuple_view():
    employee = Employee.from_dict(employee_dict)
    employee_tuple = employee.to_tuple()
    assert isinstance(employee_tuple, tuple)
    assert len(employee_tuple) > 20
    assert employee_tuple.id_ == 42


def test_resource_equality():
    employee_1 = Employee.from_dict(employee_dict)
    employee_2 = Employee.from_dict(employee_dict)
    assert id(employee_1) != id(employee_2)
    assert employee_1 == employee_2
    assert hash(employee_1) == hash(employee_2)


def test_resource_inequality():
    employee_1 = Employee.from_dict(employee_dict)
    employee_dict_mod = get_employee_dict_mod(id=7, first_name='Beta')
    employee_2 = Employee.from_dict(employee_dict_mod)
    assert employee_2.id_ == 7
    assert employee_2.last_name == 'Lovelace'
    assert employee_1 != employee_2
    assert hash(employee_1) != hash(employee_2)


def test_resource_ordering():
    employee_1 = Employee.from_dict(employee_dict)
    employee_dict_mod = get_employee_dict_mod(id=7, first_name='Beta')
    employee_2 = Employee.from_dict(employee_dict_mod)
    assert employee_1 != employee_2
    # id 42 > id 7
    assert employee_1 > employee_2
    assert employee_2 < employee_1


def test_parse_absence():
    absence = Absence.from_dict(absence_dict)
    assert absence
    assert absence.comment == 'Christmas <3'
    assert absence.created_by == 'Ada Lovelace'
    assert absence.start_date == datetime(1835, 12, 24, tzinfo=timezone.utc)
    assert absence.certificate.status == 'not-required'
    assert absence.time_off_type.name == 'vacation'
    assert absence.employee.id_ == 42


def test_serialize_absence():
    absence = Absence.from_dict(absence_dict)
    d = absence.to_dict()
    assert d == absence_dict


def test_parse_attendance():
    attendance = Attendance.from_dict(attendance_dict)
    assert attendance
    assert attendance.id_ == 42200
    assert attendance.employee_id == 42
    assert attendance.comment == 'great progress today :)'
    assert attendance.date == datetime(1835, 6, 1)
    assert attendance.start_time == timedelta(hours=9, minutes=0)
    assert attendance.end_time == timedelta(hours=17, minutes=0)


def test_serialize_attendance():
    # TODO needs fixing. should probably change the way from/to dict works
    attendance = Attendance.from_dict(attendance_dict)
    d = attendance.to_dict()
    assert d == attendance_dict


def get_employee_dict_mod(**overrides):
    employee_dict_mod = deepcopy(employee_dict)
    for key, value in overrides.items():
        employee_dict_mod[key]['value'] = value
    return employee_dict_mod
