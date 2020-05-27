from personio_py import DynamicAttr, Employee

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
}


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
    assert len(dyn_attrs) == 2
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
    assert len(employee.dynamic) == 2
    assert employee.first_name == 'Ada'
    serialized = employee.to_dict()
    assert serialized
