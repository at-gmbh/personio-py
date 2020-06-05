import json
import logging
from collections import namedtuple
from datetime import datetime, timedelta
from functools import total_ordering
from typing import Any, Dict, List, NamedTuple, Optional, TYPE_CHECKING, Tuple, Type, TypeVar

from personio_py import PersonioError, UnsupportedMethodError
from personio_py.mapping import DateFieldMapping, DurationFieldMapping, DynamicMapping, \
    FieldMapping, ListFieldMapping, \
    NumericFieldMapping, \
    ObjectFieldMapping

if TYPE_CHECKING:
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

    _field_mapping_list: List[FieldMapping] = []
    """all known API fields and their type definitions that are mapped to this PersonioResource"""
    __field_mapping: Dict[str, FieldMapping] = None
    """see ``_field_mapping()``"""
    __label_mapping: Dict[str, str] = None
    """see ``_label_mapping()``"""
    __namedtuple: Type[tuple] = None
    """see ``_namedtuple()``"""

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
        kwargs = cls._map_fields(d, client)
        return cls(client=client, **kwargs)

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        label_mapping = self._label_mapping()
        for mapping in self._field_mapping_list:
            value = getattr(self, mapping.class_field)
            if value is not None:
                label = label_mapping.get(mapping.api_field)
                d[mapping.api_field] = {'label': label, 'value': value}
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

    @classmethod
    def _is_empty(cls, value: Any):
        # determine if this Personio API value is "empty".
        # empty values are: None, "", []
        # not empty values are: 0, False, "foo", [1,2,3], 42
        return value is None or value == "" or value == []

    def __hash__(self):
        return hash(json.dumps(self.to_tuple(), sort_keys=True))

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
        return self.__repr__()


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


class SimplePersonioResource(PersonioResource):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def from_dict(cls, d: Dict[str, Any], client: 'Personio' = None) -> '__class__':
        kwargs = cls._map_flat_fields(d, client)
        return cls(client=client, **kwargs)

    @classmethod
    def _map_flat_fields(cls, d: Dict[str, Dict[str, Any]],
                         client: 'Personio' = None) -> Dict[str, Any]:
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

    def __str__(self):
        return f"{self.__class__.__name__} {getattr(self, 'name', '')}"


class AbsenceEntitlement(SimplePersonioResource):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # TODO implement


class AbsenceType(SimplePersonioResource):

    def __init__(self, id_: int, name: str, **kwargs):
        super().__init__(**kwargs)
        # TODO implement


class CostCenter(SimplePersonioResource):

    _field_mapping_list = [
        NumericFieldMapping('id', 'id_', int),
        FieldMapping('name', 'name', str),
        NumericFieldMapping('percentage', 'percentage', float),
    ]

    def __init__(self, id_: int, name: str, percentage: float, **kwargs):
        super().__init__(**kwargs)
        self.id_ = id_
        self.name = name
        self.percentage = percentage


class Department(SimplePersonioResource):

    _field_mapping_list = [
        NumericFieldMapping('id', 'id_', int),
        FieldMapping('name', 'name', str),
    ]

    def __init__(self, id_: int, name: str, **kwargs):
        super().__init__(**kwargs)
        self.id_ = id_
        self.name = name


class HolidayCalendar(SimplePersonioResource):

    _field_mapping_list = [
        NumericFieldMapping('id', 'id_', int),
        FieldMapping('name', 'name', str),
        FieldMapping('country', 'country', str),
        FieldMapping('state', 'state', str),
    ]

    def __init__(self, id_: int, name: str, country: str, state: str, **kwargs):
        super().__init__(**kwargs)
        self.id_ = id_
        self.name = name
        self.country = country
        self.state = state


class Office(SimplePersonioResource):

    _field_mapping_list = [
        NumericFieldMapping('id', 'id_', int),
        FieldMapping('name', 'name', str),
    ]

    def __init__(self, id_: int, name: str, **kwargs):
        super().__init__(**kwargs)
        self.id_ = id_
        self.name = name


class ShortEmployee(PersonioResource):

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


class Team(SimplePersonioResource):

    _field_mapping_list = [
        NumericFieldMapping('id', 'id_', int),
        FieldMapping('name', 'name', str),
    ]

    def __init__(self, id_: int, name: str, **kwargs):
        super().__init__(**kwargs)
        self.id_ = id_
        self.name = name


class WorkSchedule(SimplePersonioResource):

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

    def __init__(self, id_: int, name: str, valid_from: datetime = None, monday: timedelta = None,
                 tuesday: timedelta = None, wednesday: timedelta = None, thursday: timedelta = None,
                 friday: timedelta = None, saturday: timedelta = None, sunday: timedelta = None,
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
                 time_off_type: List[AbsenceType] = None,
                 employee: ShortEmployee = None,
                 certificate: str = None,
                 created_at: datetime = None,
                 **kwargs):
        super().__init__(client=client, dynamic=dynamic, dynamic_raw=dynamic_raw, **kwargs)

    def _create(self, client: 'Personio'):
        pass

    def _delete(self, client: 'Personio'):
        pass


class Attendance(WritablePersonioResource):

    # TODO implement

    def __init__(self,
                 client: 'Personio' = None,
                 dynamic: Dict[str, Any] = None,
                 dynamic_raw: List['DynamicAttr'] = None,
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

    def _create(self, client: 'Personio'):
        pass

    def _update(self, client: 'Personio'):
        pass

    def _delete(self, client: 'Personio'):
        pass


class Employee(WritablePersonioResource):

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
        DateFieldMapping('created_at', 'created_at'),
        DateFieldMapping('last_modified_at', 'last_modified_at'),
        FieldMapping('subcompany', 'subcompany', str),
        ObjectFieldMapping('office', 'office', Office),
        ObjectFieldMapping('department', 'department', Department),
        ListFieldMapping(ObjectFieldMapping('cost_centers', 'cost_centers', CostCenter)),
        NumericFieldMapping('fix_salary', 'fix_salary', float),
        FieldMapping('fix_salary_interval', 'fix_salary_interval', str),
        NumericFieldMapping('hourly_salary', 'hourly_salary', float),
        NumericFieldMapping('vacation_day_balance', 'vacation_day_balance', float),
        DateFieldMapping('last_working_day', 'last_working_day'),
        ObjectFieldMapping('holiday_calendar', 'holiday_calendar', HolidayCalendar),
        ObjectFieldMapping('work_schedule', 'work_schedule', WorkSchedule),
        ObjectFieldMapping('absence_entitlement', 'absence_entitlement', AbsenceEntitlement),
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
                 absence_entitlement: AbsenceEntitlement = None,
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

    def _create(self, client: 'Personio'):
        pass

    def _update(self, client: 'Personio'):
        pass

    def picture(self) -> bytes:
        # TODO request from api & cache
        pass

    def __str__(self):
        return f"{self.__class__.__name__}: {self.first_name} {self.last_name}, " \
               f"{self.position or 'position undefined'} ({self.id_})"


_unique_logs = set()


def log_once(level: int, message: str):
    if message not in _unique_logs:
        logger.log(level, message)
        _unique_logs.add(message)
