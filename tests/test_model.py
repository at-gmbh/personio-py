from copy import deepcopy
from datetime import datetime

from personio_py import DynamicAttr, Employee
from personio_py.mapping import DynamicMapping

employee_dict = {
    'id': {'label': 'ID', 'value': 42},
    'first_name': {'label': 'First name', 'value': 'Ada'},
    'last_name': {'label': 'Last name', 'value': 'Lovelace'},
    'email': {'label': 'Email', 'value': 'ada@example.org'},
    'gender': {'label': 'Gender', 'value': 'female'},
    'status': {'label': 'Status', 'value': 'deceased'},
    'position': {'label': 'Position', 'value': 'first programmer ever'},
    'dynamic_42': {'label': 'quote', 'value':
        "The Analytical Engine has no pretensions whatever to originate anything. "
        "It can do whatever we know how to order it to perform."},
    'dynamic_43': {'label': 'birthday', 'value': '1815-12-10'},
    'dynamic_44': {'label': 'hobbies', 'value': 'math,analytical thinking,music'},
}

dyn_mapping = [
    DynamicMapping(field_id=43, alias='birthday', data_type=datetime),
    DynamicMapping(field_id=44, alias='hobbies', data_type=list),
]


def test_dynamic_attr():
    dyn_43_dict = employee_dict['dynamic_43']
    dyn_attr = DynamicAttr.from_dict('dynamic_43', dyn_43_dict)
    assert dyn_attr.field_id == 43
    assert dyn_attr.label == 'birthday'
    assert dyn_attr.value == '1815-12-10'
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
    assert kwargs['dynamic_raw']
    assert kwargs['dynamic_raw'][1].label == 'birthday'


def test_parse_employee():
    employee = Employee.from_dict(employee_dict, dynamic_fields=dyn_mapping)
    assert employee.id_ == 42
    assert len(employee.dynamic_raw) == 3
    assert employee.first_name == 'Ada'
    serialized = employee.to_dict()
    assert serialized


def test_parse_employee_dyn_typed():
    employee = Employee.from_dict(employee_dict, dynamic_fields=dyn_mapping)
    assert employee.dynamic
    assert employee.dynamic['birthday'] == datetime(1815, 12, 10)
    assert employee.dynamic['hobbies'] == ['math', 'analytical thinking', 'music']
    assert len(employee.dynamic_raw) == 3


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


def get_employee_dict_mod(**overrides):
    employee_dict_mod = deepcopy(employee_dict)
    for key, value in overrides.items():
        employee_dict_mod[key]['value'] = value
    return employee_dict_mod
