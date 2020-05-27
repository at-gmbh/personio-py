from datetime import datetime
from typing import Any, Dict, List, NamedTuple, TYPE_CHECKING, Type

from personio_py import PersonioError, UnsupportedMethodError

if TYPE_CHECKING:
    from personio_py import Personio


class PersonioResource:

    def __init__(self):
        pass

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> Type['PersonioResource']:
        raise UnsupportedMethodError('from_dict', cls.__class__)

    def to_dict(self) -> Dict[str, Any]:
        raise UnsupportedMethodError('to_dict', self.__class__)


class WritablePersonioResource(PersonioResource):

    can_create = True
    can_update = True
    can_delete = True

    def __init__(self, client: 'Personio' = None, dynamic: List['DynamicAttr'] = None):
        super().__init__()
        self.client = client
        self.dynamic = {d.label: d for d in dynamic} if dynamic else {}

    @classmethod
    def from_dict(cls, d: Dict[str, Any], client: 'Personio' = None) -> Type['PersonioResource']:
        raise UnsupportedMethodError('from_dict', cls.__class__)

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
                 id_: int,
                 status: str,
                 comment: str,
                 start_date: datetime,
                 end_date: datetime,
                 days_count: float,
                 half_day_start: float,
                 half_day_end: float,
                 time_off_type: List[AbsenceType],
                 employee: ShortEmployee,
                 certificate: str,
                 created_at: datetime):
        super().__init__()

    def _create(self, client: 'Personio'):
        pass

    def _delete(self, client: 'Personio'):
        pass


class Attendance(WritablePersonioResource):

    def __init__(self,
                 employee_id: int,
                 date: datetime,
                 start_time: str,
                 end_time: str,
                 break_duration: int,
                 comment: str = None,
                 is_holiday=False,
                 is_on_time_off=False):
        super().__init__()

    def _create(self, client: 'Personio'):
        pass

    def _update(self, client: 'Personio'):
        pass

    def _delete(self, client: 'Personio'):
        pass


class Employee(WritablePersonioResource):

    can_delete = False

    def __init__(self,
                 id_: int,
                 first_name: str,
                 last_name: str,
                 email: str,
                 gender: str,
                 status: str,
                 position: str,
                 supervisor: ShortEmployee,
                 employment_type: str,
                 weekly_working_hours: str,
                 hire_date: datetime,
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
        super().__init__()
        pass

    def _create(self, client: 'Personio'):
        pass

    def _update(self, client: 'Personio'):
        pass

    def picture(self) -> bytes:
        # TODO request from api & cache
        pass

    @classmethod
    def from_dict(cls, d: Dict[str, Any], client: 'Personio' = None) -> 'Employee':
        # TODO implement
        return Employee()

    def to_dict(self) -> Dict[str, Any]:
        pass
