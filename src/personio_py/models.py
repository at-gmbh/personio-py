import json
import logging
from collections import namedtuple
from datetime import datetime, timedelta
from functools import total_ordering
from typing import Any, Dict, List, NamedTuple, TYPE_CHECKING, Tuple, Type, TypeVar

from personio_py import PersonioError, UnsupportedMethodError
from personio_py.mapping import DateFieldMapping, DurationFieldMapping, DynamicMapping, \
    FieldMapping, ListFieldMapping, \
    NumericFieldMapping, \
    ObjectFieldMapping

if TYPE_CHECKING:
    from personio_py import Personio

logger = logging.getLogger('personio_py')

PersonioResourceType = TypeVar('PersonioResourceType', bound='PersonioResource')


class DynamicAttr(NamedTuple):
    field_id: int
    label: str
    value: str

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

    def __init__(self, **kwargs):
        super().__init__()

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
    def from_dict(cls, d: Dict[str, Any]) -> '__class__':
        kwargs = cls._map_fields(d)
        return cls(**kwargs)

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
    def _map_fields(cls, d: Dict[str, Dict[str, Any]],
                    dynamic_fields: List[DynamicMapping] = None) -> Dict[str, Any]:
        kwargs = {}
        dynamic_raw = []
        dynamic = {}
        field_mapping_dict = cls._field_mapping()
        dynamic_mapping_dict = {dm.field_id: dm for dm in dynamic_fields or []}
        label_mapping = cls._label_mapping()
        for key, data in d.items():
            label_mapping[key] = data['label']
            if key in field_mapping_dict:
                field_mapping = field_mapping_dict[key]
                value = data['value']
                if not cls._is_empty(value):
                    value = field_mapping.deserialize(value)
                kwargs[field_mapping.class_field] = value
            elif key.startswith('dynamic_'):
                dyn = DynamicAttr.from_dict(key, data)
                dynamic_raw.append(dyn)
                if dyn.field_id in dynamic_mapping_dict:
                    # we have a dynamic field mapping -> parse the value
                    dm: DynamicMapping = dynamic_mapping_dict[dyn.field_id]
                    field_mapping = dm.get_field_mapping()
                    value = dyn.value
                    if not cls._is_empty(value):
                        value = field_mapping.deserialize(value)
                    dynamic[field_mapping.class_field] = value
            else:
                log_once(logging.WARNING, f"unexpected field '{key}' in class {cls.__name__}")
        if dynamic_raw:
            kwargs['dynamic_raw'] = dynamic_raw
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

    def __init__(self, client: 'Personio' = None, dynamic: Dict[str, Any] = None,
                 dynamic_raw: List['DynamicAttr'] = None, **kwargs):
        super().__init__(**kwargs)
        self._client = client
        self.dynamic = dynamic
        self.dynamic_raw: Dict[int, DynamicAttr] = {d.field_id: d for d in dynamic_raw or []}

    @classmethod
    def from_dict(cls, d: Dict[str, Any], client: 'Personio' = None,
                  dynamic_fields: List[DynamicMapping] = None) -> '__class__':
        kwargs = cls._map_fields(d, dynamic_fields)
        return cls(client=client, **kwargs)

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        for dyn in self.dynamic_raw.values():
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
    def from_dict(cls, d: Dict[str, Any]) -> '__class__':
        kwargs = {}
        field_mapping_dict = cls._field_mapping()
        for key, value in d.items():
            if key in field_mapping_dict:
                field_mapping = field_mapping_dict[key]
                if not cls._is_empty(value):
                    value = field_mapping.deserialize(value)
                kwargs[field_mapping.class_field] = value
            else:
                log_once(logging.WARNING, f"unexpected field '{key}' in class {cls.__name__}")
        return cls(**kwargs)

    def __str__(self):
        return f"{self.__class__.__name__} {getattr(self, 'name', '')}"


class AbsenceEntitlement(SimplePersonioResource):

    def __init__(self):
        super().__init__()
        # TODO implement


class AbsenceType(SimplePersonioResource):

    def __init__(self, id_: int, name: str):
        super().__init__()


class CostCenter(SimplePersonioResource):

    def __init__(self, id_: int, name: str, percentage: float):
        super().__init__()
        self.id_ = id_
        self.name = name
        self.percentage = percentage


class Department(SimplePersonioResource):

    _field_mapping_list = [
        NumericFieldMapping('id', 'id_', int),
        FieldMapping('name', 'name', str),
    ]

    def __init__(self, id_: int, name: str):
        super().__init__()
        self.id_ = id_
        self.name = name


class HolidayCalendar(SimplePersonioResource):

    _field_mapping_list = [
        NumericFieldMapping('id', 'id_', int),
        FieldMapping('name', 'name', str),
        FieldMapping('country', 'country', str),
        FieldMapping('state', 'state', str),
    ]

    def __init__(self, id_: int, name: str, country: str, state: str):
        super().__init__()
        self.id_ = id_
        self.name = name
        self.country = country
        self.state = state


class Office(SimplePersonioResource):

    _field_mapping_list = [
        NumericFieldMapping('id', 'id_', int),
        FieldMapping('name', 'name', str),
    ]

    def __init__(self, id_: int, name: str):
        super().__init__()
        self.id_ = id_
        self.name = name


class ShortEmployee(PersonioResource):

    _field_mapping_list = [
        NumericFieldMapping('id', 'id_', int),
        FieldMapping('first_name', 'first_name', str),
        FieldMapping('last_name', 'last_name', str),
        FieldMapping('email', 'email', str),
    ]

    def __init__(self, id_: int, first_name: str, last_name: str, email: str):
        super().__init__()
        self.id_ = id_
        self.first_name = first_name
        self.last_name = last_name
        self.email = email

    def resolve(self):
        # TODO get full employee
        pass


class Team(SimplePersonioResource):

    _field_mapping_list = [
        NumericFieldMapping('id', 'id_', int),
        FieldMapping('name', 'name', str),
    ]

    def __init__(self, id_: int, name: str):
        super().__init__()
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
                 friday: timedelta = None, saturday: timedelta = None, sunday: timedelta = None):
        super().__init__()
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
                 created_at: datetime = None):
        super().__init__(client=client, dynamic=dynamic, dynamic_raw=dynamic_raw)

    def _create(self, client: 'Personio'):
        pass

    def _delete(self, client: 'Personio'):
        pass


class Attendance(WritablePersonioResource):

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
                 is_on_time_off: bool = None):
        super().__init__(client=client, dynamic=dynamic, dynamic_raw=dynamic_raw)

    def _create(self, client: 'Personio'):
        pass

    def _update(self, client: 'Personio'):
        pass

    def _delete(self, client: 'Personio'):
        pass


class Employee(WritablePersonioResource):

    # standort, abteilung, geburtstag, gesellschaft

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
        ObjectFieldMapping('office', 'office', Office),
        ObjectFieldMapping('department', 'department', Department),
        ListFieldMapping(ObjectFieldMapping('cost_centers', 'cost_centers', CostCenter)),
        NumericFieldMapping('fix_salary', 'fix_salary', float),
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
                 office: Office = None,
                 department: Department = None,
                 cost_centers: List[CostCenter] = None,
                 fix_salary: float = None,
                 hourly_salary: float = None,
                 vacation_day_balance: float = None,
                 last_working_day: datetime = None,
                 holiday_calendar: HolidayCalendar = None,
                 work_schedule: WorkSchedule = None,
                 absence_entitlement: AbsenceEntitlement = None,
                 profile_picture: str = None,
                 team: Team = None):
        super().__init__(client=client, dynamic=dynamic, dynamic_raw=dynamic_raw)
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
        self.office = office
        self.department = department
        self.cost_centers = cost_centers
        self.fix_salary = fix_salary
        self.hourly_salary = hourly_salary
        self.vacation_day_balance = vacation_day_balance
        self.last_working_day = last_working_day
        self.holiday_calendar = holiday_calendar
        self.work_schedule = work_schedule
        self.absence_entitlement = absence_entitlement
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
