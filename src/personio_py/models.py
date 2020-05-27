import logging
from datetime import datetime
from typing import Any, Dict, List, NamedTuple, TYPE_CHECKING, Type, TypeVar, Union

from personio_py import PersonioError, UnsupportedMethodError

if TYPE_CHECKING:
    from personio_py import Personio

logger = logging.getLogger('personio_py')

# type variables
PersonioResourceType = TypeVar('PersonioResourceType', bound='PersonioResource')
T = TypeVar('T')


class PersonioResource:

    _field_mapping: Dict[str, str] = {}

    def __init__(self, **kwargs):
        super().__init__()

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> PersonioResourceType:
        kwargs = cls._map_fields(d)
        return cls(**kwargs)

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        for api_field, class_field in self._field_mapping.items():
            d[api_field] = getattr(self, class_field)
        return d

    @classmethod
    def _map_fields(cls, d: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        kwargs = {}
        dynamic = {}
        for key, data in d.items():
            if key in cls._field_mapping:
                var_name = cls._field_mapping[key]
                kwargs[var_name] = data['value']
            elif key.startswith('dynamic_'):
                dyn = DynamicAttr.from_dict(key, data)
                dynamic[dyn.field_id] = dyn
            else:
                log_once(logging.WARNING,
                         f"unexpected field '{key}' in class {cls.__class__.__name__}")
        if dynamic:
            kwargs['dynamic'] = dynamic
        return kwargs


class WritablePersonioResource(PersonioResource):

    can_create = True
    can_update = True
    can_delete = True

    def __init__(self, client: 'Personio' = None, dynamic: List['DynamicAttr'] = None, **kwargs):
        super().__init__()
        self.client = client
        self.dynamic: Dict[int, DynamicAttr] = {d.field_id: d for d in dynamic} if dynamic else {}

    @classmethod
    def from_dict(cls, d: Dict[str, Any], client: 'Personio' = None) -> PersonioResourceType:
        kwargs = cls._map_fields(d)
        return cls(client=client, **kwargs)

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        for dyn in self.dynamic.values():
            d[f'dynamic_{dyn.field_id}'] = dyn.to_dict()
        return d

    def create(self, client: 'Personio' = None):
        if self.can_create:
            client = self._check_client(client)
            return self._create(client)
        else:
            raise UnsupportedMethodError('create', self.__class__)

    def _create(self, client: 'Personio'):
        raise UnsupportedMethodError('create', self.__class__)

    def update(self, client: 'Personio' = None):
        if self.can_update:
            client = self._check_client(client)
            return self._update(client)
        else:
            raise UnsupportedMethodError('update', self.__class__)

    def _update(self, client: 'Personio'):
        UnsupportedMethodError('update', self.__class__)

    def delete(self, client: 'Personio' = None):
        if self.can_delete:
            client = self._check_client(client)
            return self._delete(client)
        else:
            raise UnsupportedMethodError('delete', self.__class__)

    def _delete(self, client: 'Personio'):
        UnsupportedMethodError('delete', self.__class__)

    def _check_client(self, client: 'Personio' = None) -> 'Personio':
        client = client or self.client
        if not client:
            raise PersonioError()
        if not client.authenticated:
            client.authenticate()
        return client


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


class FieldMapping:

    def __init__(self, api_field: str, class_field: str, field_type: T):
        self.api_field = api_field
        self.class_field = class_field
        self.field_type = field_type

    def serialize(self, value: T) -> Union[str, Dict]:
        return str(value)

    def deserialize(self, value: Union[str, Dict]) -> T:
        raise self.field_type(value)


class DateFieldMapping(FieldMapping):

    def __init__(self, api_field: str, class_field: str):
        super().__init__(api_field, class_field, field_type=datetime)

    def serialize(self, value: datetime) -> str:
        return value.isoformat()[:10]

    def deserialize(self, value: str) -> datetime:
        return datetime.fromisoformat(value)


class ObjectFieldMapping(FieldMapping):

    def __init__(self, api_field: str, class_field: str, field_type: PersonioResourceType):
        super().__init__(api_field, class_field, field_type)

    def serialize(self, value: PersonioResource) -> Dict:
        return value.to_dict()

    def deserialize(self, value: Dict) -> PersonioResource:
        return self.field_type.from_dict(value)


class ListFieldMapping(FieldMapping):
    # wraps another field mapping, to handle list types
    # e.g. ``ListFieldMapping(ObjectFieldMapping('cost_centers', 'cost_centers', CostCenter))``

    def __init__(self, item_mapping: FieldMapping):
        super().__init__(item_mapping.api_field, item_mapping.class_field, field_type=List)
        self.item_mapping = item_mapping

    def serialize(self, values: List[Any]) -> List[Any]:
        return [self.item_mapping.serialize(item) for item in values]

    def deserialize(self, values: List[Any]) -> List[Any]:
        return [self.item_mapping.deserialize(item) for item in values]


class AbsenceEntitlement(PersonioResource):

    def __init__(self):
        super().__init__()
        # TODO implement


class AbsenceType(PersonioResource):

    def __init__(self, id_: int, name: str):
        super().__init__()


class CostCenter(PersonioResource):

    def __init__(self, id_: int, name: str, percentage: float):
        super().__init__()
        self.id_ = id_
        self.name = name
        self.percentage = percentage


class Department(PersonioResource):

    def __init__(self, name: str):
        super().__init__()
        self.name = name


class HolidayCalendar(PersonioResource):

    def __init__(self, id_: int, name: str, country: str, state: str):
        super().__init__()
        self.id_ = id_
        self.name = name
        self.country = country
        self.state = state


class Office(PersonioResource):

    def __init__(self, name: str):
        super().__init__()
        self.name = name


class ShortEmployee(PersonioResource):

    def __init__(self, id_: int, first_name: str, last_name: str, email: str):
        super().__init__()
        self.id_ = id_
        self.first_name = first_name
        self.last_name = last_name
        self.email = email

    def resolve(self):
        # TODO get full employee
        pass


class Team(PersonioResource):

    def __init__(self, id_: int, name: str):
        super().__init__()
        self.id_ = id_
        self.name = name


class WorkSchedule(PersonioResource):

    def __init__(self, id_: int, name: str, monday: str, tuesday: str, wednesday: str,
                 thursday: str, friday: str, saturday: str, sunday: str):
        super().__init__()
        self.id_ = id_
        self.name = name
        # pattern: ^\d\d:\d\d$
        self.monday = monday
        self.tuesday = tuesday
        self.wednesday = wednesday
        self.thursday = thursday
        self.friday = friday
        self.saturday = saturday
        self.sunday = sunday


class Absence(WritablePersonioResource):

    can_update = False

    def __init__(self,
                 client: 'Personio' = None,
                 dynamic: List['DynamicAttr'] = None,
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
        super().__init__(client=client, dynamic=dynamic)

    def _create(self, client: 'Personio'):
        pass

    def _delete(self, client: 'Personio'):
        pass


class Attendance(WritablePersonioResource):

    def __init__(self,
                 client: 'Personio' = None,
                 dynamic: List['DynamicAttr'] = None,
                 employee_id: int = None,
                 date: datetime = None,
                 start_time: str = None,
                 end_time: str = None,
                 break_duration: int = None,
                 comment: str = None,
                 is_holiday: bool = None,
                 is_on_time_off: bool = None):
        super().__init__(client=client, dynamic=dynamic)

    def _create(self, client: 'Personio'):
        pass

    def _update(self, client: 'Personio'):
        pass

    def _delete(self, client: 'Personio'):
        pass


class Employee(WritablePersonioResource):

    can_delete = False

    _field_mapping = {
        'id': 'id_',
        'first_name': 'first_name',
        'last_name': 'last_name',
        'email': 'email',
    }

    def __init__(self,
                 client: 'Personio' = None,
                 dynamic: List['DynamicAttr'] = None,
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
        super().__init__(client=client, dynamic=dynamic)
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


_unique_logs = set()


def log_once(level: int, message: str):
    if message not in _unique_logs:
        logger.log(level, message)
        _unique_logs.add(message)
