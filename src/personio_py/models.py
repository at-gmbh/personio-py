"""
definition of ORMs for objects that are available in the Personio API
"""
import json
import logging
from collections import namedtuple
from datetime import datetime, timedelta
from functools import total_ordering
from typing import Any, Dict, List, NamedTuple, Optional, TYPE_CHECKING, Tuple, Type, TypeVar

from personio_py import PersonioError, UnsupportedMethodError
from personio_py.mapping import DateFieldMapping, DateTimeFieldMapping, DurationFieldMapping, \
    DynamicMapping, FieldMapping, ListFieldMapping, NumericFieldMapping, ObjectFieldMapping

if TYPE_CHECKING:
    # only type checkers may import Personio, otherwise we get an evil circular import error
    from personio_py import Personio

logger = logging.getLogger('personio_py')


class DynamicAttr(NamedTuple):
    field_id: int
    label: str
    value: Any

    @classmethod
    def from_attributes(cls, d: Dict[str, Dict[str, Any]]) -> List['DynamicAttr']:
        return [DynamicAttr.from_dict(k, v) for k, v in d.items() if k.startswith('dynamic_')]

    @classmethod
    def to_attributes(cls, dyn_attrs: List['DynamicAttr']) -> Dict[str, Dict[str, Any]]:
        return {f'dynamic_{d.field_id}': d.to_dict() for d in dyn_attrs}

    @classmethod
    def from_dict(cls, key: str, d: Dict[str, Any]) -> 'DynamicAttr':
        if key.startswith('dynamic_'):
            _, field_id = key.split('_', maxsplit=1)
            return DynamicAttr(field_id=int(field_id), label=d['label'], value=d['value'])
        else:
            raise ValueError(f"dynamic attribute '{key}' does not start with 'dynamic_'")

    def to_dict(self) -> Dict[str, Any]:
        return {'label': self.label, 'value': self.value}

    def clone(self, new_value: Optional[Any] = None):
        return DynamicAttr(field_id=self.field_id, label=self.label,
                           value=self.value if new_value is None else new_value)


@total_ordering
class PersonioResource:

    _api_type_name: str = None
    """the name of this resource type in the Personio API"""
    _field_mapping_list: List[FieldMapping] = []
    """all known API fields and their type definitions that are mapped to this PersonioResource"""
    __field_mapping: Dict[str, FieldMapping] = None
    """see ``_field_mapping()``"""
    __label_mapping: Dict[str, str] = None
    """see ``_label_mapping()``"""
    __namedtuple: Type[tuple] = None
    """see ``_namedtuple()``"""
    _flat_dict = False
    """set this to True, if this class has a flat dictionary representation in the Personio API"""

    def __init__(self, client: 'Personio' = None, **kwargs):
        super().__init__()
        self._client = client

    @classmethod
    def _field_mapping(cls) -> Dict[str, FieldMapping]:
        # the field mapping as dictionary
        if cls.__field_mapping is None:
            cls.__field_mapping = {fm.api_field: fm for fm in cls._field_mapping_list}
        return cls.__field_mapping

    @classmethod
    def _label_mapping(cls) -> Dict[str, str]:
        # mapping from api field name to pretty label name
        if cls.__label_mapping is None:
            cls.__label_mapping = {}
        return cls.__label_mapping

    @classmethod
    def from_dict(cls, d: Dict[str, Any], client: 'Personio' = None) -> '__class__':
        # TODO from/to dict should probably always serialize from/to the full dict,
        #  not a subset like d['attributes']
        kwargs = cls._map_fields(d, client)
        return cls(client=client, **kwargs)

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        for mapping in self._field_mapping_list:
            value = getattr(self, mapping.class_field)
            if value is not None:
                d[mapping.api_field] = mapping.serialize(value)
        return d

    @classmethod
    def _namedtuple(cls) -> Type[Tuple]:
        if cls.__namedtuple is None:
            fields = [m.class_field for m in cls._field_mapping_list] + ['dynamic', 'class_name']
            cls.__namedtuple = namedtuple(f'{cls.__name__}Tuple', fields)
        return cls.__namedtuple

    def to_tuple(self) -> Tuple:
        values = ([getattr(self, m.class_field) for m in self._field_mapping_list] +
                  [getattr(self, 'dynamic'), str(self.__class__)])
        return self._namedtuple()(*values)

    @classmethod
    def _map_fields(cls, d: Dict[str, Dict[str, Any]], client: 'Personio' = None) -> Dict[str, Any]:
        kwargs = {}
        field_mapping_dict = cls._field_mapping()
        for key, value in d.items():
            if key in field_mapping_dict:
                field_mapping = field_mapping_dict[key]
                if not cls._is_empty(value):
                    value = field_mapping.deserialize(value, client=client)
                kwargs[field_mapping.class_field] = value
            else:
                log_once(logging.WARNING, f"unexpected field '{key}' in class {cls.__name__}")
        return kwargs

    @classmethod
    def _is_empty(cls, value: Any):
        # determine if this Personio API value is "empty".
        # empty values are: None, "", []
        # not empty values are: 0, False, "foo", [1,2,3], 42
        return value is None or value == "" or value == []

    def __hash__(self):
        return hash(json.dumps(self.to_tuple(), sort_keys=True, default=str))

    def __eq__(self, other):
        if isinstance(other, PersonioResource):
            return self.to_tuple() == other.to_tuple()
        else:
            return False

    def __lt__(self, other):
        if isinstance(other, PersonioResource):
            return self.to_tuple() < other.to_tuple()
        else:
            return False

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} {self.__dict__}"

    def __str__(self) -> str:
        fields = ', '.join(f'{k}={v}' for k, v in self.__dict__.items() if not k.startswith('_'))
        return f"{self.__class__.__name__}({fields})"


PersonioResourceType = TypeVar('PersonioResourceType', bound=PersonioResource)


class WritablePersonioResource(PersonioResource):

    _can_create = True
    _can_update = True
    _can_delete = True

    def __init__(self, client: 'Personio' = None, dynamic: List['DynamicAttr'] = None,
                 dynamic_fields: List[DynamicMapping] = None, **kwargs):
        super().__init__(client, **kwargs)
        self.dynamic_fields = dynamic_fields
        self.dynamic_raw: Dict[int, DynamicAttr] = {d.field_id: d for d in dynamic or []}
        self.dynamic = self._map_dynamic_values(dynamic, dynamic_fields, client)

    @classmethod
    def _map_dynamic_values(
            cls, dynamic_raw: List['DynamicAttr'], dynamic_fields: List[DynamicMapping] = None,
            client: 'Personio' = None) -> Dict[str, Any]:
        dynamic = {}
        if not dynamic_raw or not dynamic_fields:
            return dynamic
        dynamic_mapping_dict = {dm.field_id: dm for dm in dynamic_fields or []}
        for dyn in dynamic_raw:
            if dyn.field_id in dynamic_mapping_dict:
                # we have a dynamic field mapping -> parse the value
                dm: DynamicMapping = dynamic_mapping_dict[dyn.field_id]
                field_mapping = dm.get_field_mapping()
                value = dyn.value
                if not cls._is_empty(value):
                    value = field_mapping.deserialize(value, client=client)
                dynamic[field_mapping.class_field] = value
        return dynamic

    @classmethod
    def from_dict(cls, d: Dict[str, Any], client: 'Personio' = None,
                  dynamic_fields: List[DynamicMapping] = None) -> '__class__':
        kwargs = cls._map_fields(d, client)
        dynamic_fields = dynamic_fields or (client.dynamic_fields if client else None)
        return cls(client=client, dynamic_fields=dynamic_fields, **kwargs)

    def to_dict(self) -> Dict[str, Any]:
        # we prefer typed values from the dynamic dict over the raw values
        d = super().to_dict()
        dynamic_mapping_dict = {dyn.field_id: dyn for dyn in self.dynamic_fields or []}
        for dyn in self.dynamic_raw.values():
            if dyn.field_id in dynamic_mapping_dict:
                raw_value = dyn.value
                dm: DynamicMapping = dynamic_mapping_dict[dyn.field_id]
                rich_value = self.dynamic[dm.alias]
                if raw_value != rich_value:
                    field_mapping = dm.get_field_mapping()
                    serialized = field_mapping.serialize(rich_value)
                    if raw_value != serialized:
                        dyn = dyn.clone(new_value=serialized)
            d[f'dynamic_{dyn.field_id}'] = dyn.to_dict()
        return d

    def create(self, client: 'Personio' = None):
        if self._can_create:
            client = self._check_client(client)
            return self._create(client)
        else:
            raise UnsupportedMethodError('create', self.__class__)

    def _create(self, client: 'Personio'):
        raise UnsupportedMethodError('create', self.__class__)

    def update(self, client: 'Personio' = None):
        if self._can_update:
            client = self._check_client(client)
            return self._update(client)
        else:
            raise UnsupportedMethodError('update', self.__class__)

    def _update(self, client: 'Personio'):
        UnsupportedMethodError('update', self.__class__)

    def delete(self, client: 'Personio' = None):
        if self._can_delete:
            client = self._check_client(client)
            return self._delete(client)
        else:
            raise UnsupportedMethodError('delete', self.__class__)

    def _delete(self, client: 'Personio'):
        UnsupportedMethodError('delete', self.__class__)

    def _check_client(self, client: 'Personio' = None) -> 'Personio':
        client = client or self._client
        if not client:
            raise PersonioError()
        if not client.authenticated:
            client.authenticate()
        return client


# TODO adjust (this mixin concept has issues)
class LabeledAttributesMixin(PersonioResource):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        label_mapping = self._label_mapping()
        for mapping in self._field_mapping_list:
            value = getattr(self, mapping.class_field)
            if value is not None:
                label = label_mapping.get(mapping.api_field)
                d[mapping.api_field] = {'label': label, 'value': mapping.serialize(value)}
        return d

    @classmethod
    def _map_fields(cls, d: Dict[str, Dict[str, Any]], client: 'Personio' = None) -> Dict[str, Any]:
        kwargs = {}
        dynamic = []
        field_mapping_dict = cls._field_mapping()
        label_mapping = cls._label_mapping()
        for key, data in d.items():
            label_mapping[key] = data['label']
            if key in field_mapping_dict:
                field_mapping = field_mapping_dict[key]
                value = data['value']
                if not cls._is_empty(value):
                    value = field_mapping.deserialize(value, client=client)
                kwargs[field_mapping.class_field] = value
            elif key.startswith('dynamic_'):
                dyn = DynamicAttr.from_dict(key, data)
                dynamic.append(dyn)
            else:
                log_once(logging.WARNING, f"unexpected field '{key}' in class {cls.__name__}")
        if dynamic:
            kwargs['dynamic'] = dynamic
        return kwargs


class AbsenceEntitlement(PersonioResource):

    _api_type_name = "TimeOffType"
    _field_mapping_list = [
        NumericFieldMapping('id', 'id_', int),
        FieldMapping('name', 'name', str),
        NumericFieldMapping('entitlement', 'entitlement', float),
    ]

    def __init__(self, id_: int = None, name: str = None, entitlement: float = None, **kwargs):
        super().__init__(**kwargs)
        self.id_ = id_
        self.name = name
        self.entitlement = entitlement


class AbsenceType(PersonioResource):

    _api_type_name = "TimeOffType"
    _field_mapping_list = [
        NumericFieldMapping('id', 'id_', int),
        FieldMapping('name', 'name', str),
    ]

    def __init__(self, id_: int = None, name: str = None, **kwargs):
        super().__init__(**kwargs)
        self.id_ = id_
        self.name = name


class Certificate(PersonioResource):

    _field_mapping_list = [
        FieldMapping('status', 'status', str),
    ]
    _flat_dict = True

    def __init__(self, status: str = None, **kwargs):
        super().__init__(**kwargs)
        self.status = status


class CostCenter(PersonioResource):

    _api_type_name = 'CostCenter'
    _field_mapping_list = [
        NumericFieldMapping('id', 'id_', int),
        FieldMapping('name', 'name', str),
        NumericFieldMapping('percentage', 'percentage', float),
    ]

    def __init__(self, id_: int = None, name: str = None, percentage: float = None, **kwargs):
        super().__init__(**kwargs)
        self.id_ = id_
        self.name = name
        self.percentage = percentage


class Department(PersonioResource):

    _api_type_name = 'Department'
    _field_mapping_list = [
        NumericFieldMapping('id', 'id_', int),
        FieldMapping('name', 'name', str),
    ]

    def __init__(self, id_: int = None, name: str = None, **kwargs):
        super().__init__(**kwargs)
        self.id_ = id_
        self.name = name


class HolidayCalendar(PersonioResource):

    _api_type_name = 'HolidayCalendar'
    _field_mapping_list = [
        NumericFieldMapping('id', 'id_', int),
        FieldMapping('name', 'name', str),
        FieldMapping('country', 'country', str),
        FieldMapping('state', 'state', str),
    ]

    def __init__(self, id_: int = None, name: str = None, country: str = None,
                 state: str = None, **kwargs):
        super().__init__(**kwargs)
        self.id_ = id_
        self.name = name
        self.country = country
        self.state = state


class Office(PersonioResource):

    _api_type_name = 'Office'
    _field_mapping_list = [
        NumericFieldMapping('id', 'id_', int),
        FieldMapping('name', 'name', str),
    ]

    def __init__(self, id_: int = None, name: str = None, **kwargs):
        super().__init__(**kwargs)
        self.id_ = id_
        self.name = name


class ShortEmployee(LabeledAttributesMixin):

    _api_type_name = "Employee"
    _field_mapping_list = [
        NumericFieldMapping('id', 'id_', int),
        FieldMapping('first_name', 'first_name', str),
        FieldMapping('last_name', 'last_name', str),
        FieldMapping('email', 'email', str),
    ]

    def __init__(self, client: 'Personio' = None, id_: int = None, first_name: str = None,
                 last_name: str = None, email: str = None, **kwargs):
        super().__init__(**kwargs)
        self._client = client
        self.id_ = id_
        self.first_name = first_name
        self.last_name = last_name
        self.email = email

    def resolve(self, client: 'Personio' = None) -> 'Employee':
        client = client or self._client
        if client:
            return client.get_employee(self.id_)
        else:
            raise PersonioError(
                f"no Personio client is is available in this {self.__class__.__name__} instance "
                f"to make a request for the full employee profile of "
                f"{self.first_name} {self.last_name} ({self.id_})")


class Team(PersonioResource):

    _api_type_name = 'Team'
    _field_mapping_list = [
        NumericFieldMapping('id', 'id_', int),
        FieldMapping('name', 'name', str),
    ]

    def __init__(self, id_: int = None, name: str = None, **kwargs):
        super().__init__(**kwargs)
        self.id_ = id_
        self.name = name


class WorkSchedule(PersonioResource):

    _api_type_name = 'WorkSchedule'
    _field_mapping_list = [
        NumericFieldMapping('id', 'id_', int),
        FieldMapping('name', 'name', str),
        DateFieldMapping('valid_from', 'valid_from'),
        DurationFieldMapping('monday', 'monday'),
        DurationFieldMapping('tuesday', 'tuesday'),
        DurationFieldMapping('wednesday', 'wednesday'),
        DurationFieldMapping('thursday', 'thursday'),
        DurationFieldMapping('friday', 'friday'),
        DurationFieldMapping('saturday', 'saturday'),
        DurationFieldMapping('sunday', 'sunday'),
    ]

    def __init__(self,
                 id_: int = None,
                 name: str = None,
                 valid_from: datetime = None,
                 monday: timedelta = None,
                 tuesday: timedelta = None,
                 wednesday: timedelta = None,
                 thursday: timedelta = None,
                 friday: timedelta = None,
                 saturday: timedelta = None,
                 sunday: timedelta = None,
                 **kwargs):
        super().__init__(**kwargs)
        self.id_ = id_
        self.name = name
        self.valid_from = valid_from
        self.monday = monday
        self.tuesday = tuesday
        self.wednesday = wednesday
        self.thursday = thursday
        self.friday = friday
        self.saturday = saturday
        self.sunday = sunday


class Absence(WritablePersonioResource):

    # TODO implement

    _can_update = False

    _field_mapping_list = [
        NumericFieldMapping('id', 'id_', int),
        FieldMapping('status', 'status', str),
        FieldMapping('comment', 'comment', str),
        DateFieldMapping('start_date', 'start_date'),
        DateFieldMapping('end_date', 'end_date'),
        NumericFieldMapping('days_count', 'days_count', float),
        NumericFieldMapping('half_day_start', 'half_day_start', float),
        NumericFieldMapping('half_day_end', 'half_day_end', float),
        ObjectFieldMapping('time_off_type', 'time_off_type', AbsenceType),
        ObjectFieldMapping('employee', 'employee', ShortEmployee),
        FieldMapping('created_by', 'created_by', str),
        ObjectFieldMapping('certificate', 'certificate', Certificate),
        DateTimeFieldMapping('created_at', 'created_at'),
    ]

    def __init__(self,
                 client: 'Personio' = None,
                 dynamic: Dict[str, Any] = None,
                 dynamic_raw: List['DynamicAttr'] = None,
                 id_: int = None,
                 status: str = None,
                 comment: str = None,
                 start_date: datetime = None,
                 end_date: datetime = None,
                 days_count: float = None,
                 half_day_start: float = None,
                 half_day_end: float = None,
                 time_off_type: AbsenceType = None,
                 employee: ShortEmployee = None,
                 created_by: str = None,
                 certificate: Certificate = None,
                 created_at: datetime = None,
                 **kwargs):
        super().__init__(client=client, dynamic=dynamic, dynamic_raw=dynamic_raw, **kwargs)
        self.id_ = id_
        self.status = status
        self.comment = comment
        self.start_date = start_date
        self.end_date = end_date
        self.days_count = days_count
        self.half_day_start = half_day_start
        self.half_day_end = half_day_end
        self.time_off_type = time_off_type
        self.employee = employee
        self.created_by = created_by
        self.certificate = certificate
        self.created_at = created_at

    def _create(self, client: 'Personio'):
        pass

    def _delete(self, client: 'Personio'):
        pass


class Attendance(WritablePersonioResource):

    _api_type_name = "AttendancePeriod"
    _field_mapping_list = [
        # note: the id is not in the attributes dict, but one level higher
        NumericFieldMapping('id', 'id_', int),
        NumericFieldMapping('employee', 'employee_id', int),
        DateFieldMapping('date', 'date'),
        DurationFieldMapping('start_time', 'start_time'),
        DurationFieldMapping('end_time', 'end_time'),
        NumericFieldMapping('break', 'break_duration', int),
        FieldMapping('comment', 'comment', str),
        FieldMapping('is_holiday', 'is_holiday', bool),
        FieldMapping('is_on_time_off', 'is_on_time_off', bool),
    ]

    def __init__(self,
                 client: 'Personio' = None,
                 dynamic: Dict[str, Any] = None,
                 dynamic_raw: List['DynamicAttr'] = None,
                 id_: int = None,
                 employee_id: int = None,
                 date: datetime = None,
                 start_time: str = None,
                 end_time: str = None,
                 break_duration: int = None,
                 comment: str = None,
                 is_holiday: bool = None,
                 is_on_time_off: bool = None,
                 **kwargs):
        super().__init__(client=client, dynamic=dynamic, dynamic_raw=dynamic_raw, **kwargs)
        self.id_ = id_
        self.employee_id = employee_id
        self.date = date
        self.start_time = start_time
        self.end_time = end_time
        self.break_duration = break_duration
        self.comment = comment
        self.is_holiday = is_holiday
        self.is_on_time_off = is_on_time_off

    @classmethod
    def from_dict(cls, d: Dict[str, Any], client: 'Personio' = None,
                  dynamic_fields: List[DynamicMapping] = None) -> '__class__':
        attendance: Attendance = super().from_dict(d['attributes'], client, dynamic_fields)
        attendance.id_ = d['id']
        return attendance

    def _create(self, client: 'Personio'):
        pass

    def _update(self, client: 'Personio'):
        pass

    def _delete(self, client: 'Personio'):
        pass


class Employee(WritablePersonioResource, LabeledAttributesMixin):

    _api_type_name = "Employee"
    _can_delete = False
    _field_mapping_list = [
        NumericFieldMapping('id', 'id_', int),
        FieldMapping('first_name', 'first_name', str),
        FieldMapping('last_name', 'last_name', str),
        FieldMapping('email', 'email', str),
        FieldMapping('gender', 'gender', str),
        FieldMapping('status', 'status', str),
        FieldMapping('position', 'position', str),
        ObjectFieldMapping('supervisor', 'supervisor', ShortEmployee),
        FieldMapping('employment_type', 'employment_type', str),
        FieldMapping('weekly_working_hours', 'weekly_working_hours', str),
        DateFieldMapping('hire_date', 'hire_date'),
        DateFieldMapping('contract_end_date', 'contract_end_date'),
        DateFieldMapping('termination_date', 'termination_date'),
        FieldMapping('termination_type', 'termination_type', str),
        FieldMapping('termination_reason', 'termination_reason', str),
        DateFieldMapping('probation_period_end', 'probation_period_end'),
        DateTimeFieldMapping('created_at', 'created_at'),
        DateTimeFieldMapping('last_modified_at', 'last_modified_at'),
        FieldMapping('subcompany', 'subcompany', str),
        ObjectFieldMapping('office', 'office', Office),
        ObjectFieldMapping('department', 'department', Department),
        ListFieldMapping(ObjectFieldMapping(
            'cost_centers', 'cost_centers', CostCenter)),
        NumericFieldMapping('fix_salary', 'fix_salary', float),
        FieldMapping('fix_salary_interval', 'fix_salary_interval', str),
        NumericFieldMapping('hourly_salary', 'hourly_salary', float),
        NumericFieldMapping('vacation_day_balance', 'vacation_day_balance', float),
        DateFieldMapping('last_working_day', 'last_working_day'),
        ObjectFieldMapping('holiday_calendar', 'holiday_calendar', HolidayCalendar),
        ObjectFieldMapping('work_schedule', 'work_schedule', WorkSchedule),
        ListFieldMapping(ObjectFieldMapping(
            'absence_entitlement', 'absence_entitlement', AbsenceEntitlement)),
        FieldMapping('profile_picture', 'profile_picture', str),
        ObjectFieldMapping('team', 'team', Team),
    ]

    def __init__(self,
                 client: 'Personio' = None,
                 dynamic: Dict[str, Any] = None,
                 dynamic_raw: List['DynamicAttr'] = None,
                 id_: int = None,
                 first_name: str = None,
                 last_name: str = None,
                 email: str = None,
                 gender: str = None,
                 status: str = None,
                 position: str = None,
                 supervisor: ShortEmployee = None,
                 employment_type: str = None,
                 weekly_working_hours: str = None,
                 hire_date: datetime = None,
                 contract_end_date: datetime = None,
                 termination_date: datetime = None,
                 termination_type: str = None,
                 termination_reason: str = None,
                 probation_period_end: datetime = None,
                 created_at: datetime = None,
                 last_modified_at: datetime = None,
                 subcompany: str = None,
                 office: Office = None,
                 department: Department = None,
                 cost_centers: List[CostCenter] = None,
                 holiday_calendar: HolidayCalendar = None,
                 absence_entitlement: List[AbsenceEntitlement] = None,
                 work_schedule: WorkSchedule = None,
                 fix_salary: float = None,
                 fix_salary_interval: str = None,
                 hourly_salary: float = None,
                 vacation_day_balance: float = None,
                 last_working_day: datetime = None,
                 profile_picture: str = None,
                 team: Team = None,
                 **kwargs):
        super().__init__(client=client, dynamic=dynamic, dynamic_raw=dynamic_raw, **kwargs)
        self.id_ = id_
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.gender = gender
        self.status = status
        self.position = position
        self.supervisor = supervisor
        self.employment_type = employment_type
        self.weekly_working_hours = weekly_working_hours
        self.hire_date = hire_date
        self.contract_end_date = contract_end_date
        self.termination_date = termination_date
        self.termination_type = termination_type
        self.termination_reason = termination_reason
        self.probation_period_end = probation_period_end
        self.created_at = created_at
        self.last_modified_at = last_modified_at
        self.subcompany = subcompany
        self.office = office
        self.department = department
        self.cost_centers = cost_centers
        self.holiday_calendar = holiday_calendar
        self.absence_entitlement = absence_entitlement
        self.work_schedule = work_schedule
        self.fix_salary = fix_salary
        self.fix_salary_interval = fix_salary_interval
        self.hourly_salary = hourly_salary
        self.vacation_day_balance = vacation_day_balance
        self.last_working_day = last_working_day
        self.profile_picture = profile_picture
        self.team = team
        self._picture = None

    def _create(self, client: 'Personio' = None):
        pass

    def _update(self, client: 'Personio' = None):
        pass

    def picture(self, client: 'Personio' = None, width: int = None) -> bytes:
        if self._picture is None:
            client = get_client(self, client)
            self._picture = client.get_employee_picture(self.id_, width=width)
        return self._picture

    def __str__(self):
        return f"{self.__class__.__name__}: {self.first_name} {self.last_name}, " \
               f"{self.position or 'position undefined'} ({self.id_})"


_unique_logs = set()


def log_once(level: int, message: str):
    if message not in _unique_logs:
        logger.log(level, message)
        _unique_logs.add(message)


def get_client(resource: PersonioResource, client: 'Personio' = None):
    if resource._client or client:
        return resource._client or client
    raise PersonioError(f"no Personio client reference is available, please provide it to "
                        f"your {type(resource).__name__} or as function parameter")
