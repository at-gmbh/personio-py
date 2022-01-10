"""
Definition of ORMs for objects that are available in the Personio API
"""
import logging
from datetime import date, datetime, timedelta
from typing import Any, ClassVar, Dict, List, Optional, TYPE_CHECKING, TypeVar

from pydantic import BaseModel, Extra

from personio_py import PersonioError
from personio_py.util import ReadOnlyDict, log_once

if TYPE_CHECKING:
    # only type checkers may import Personio, otherwise we get an evil circular import error
    from personio_py import Personio

logger = logging.getLogger('personio_py')

PersonioResourceType = TypeVar('PersonioResourceType', bound='PersonioResource')


class PersonioResource(BaseModel):
    # for class vars & private attributes, see
    # https://pydantic-docs.helpmanual.io/usage/models/#private-model-attributes

    _api_type_name: ClassVar[str] = None
    """the name of this resource type in the Personio API"""
    _flat_dict: ClassVar[bool] = True
    """Indicates if this class has a flat dictionary representation in the Personio API"""
    _client: Optional['Personio'] = None
    """reference to the API client that created this object (optional)"""

    def __init__(self, client: 'Personio' = None, **kwargs):
        if self._is_api_dict(kwargs):
            # smells like a parsed Personio API dict -> extract data
            kwargs = self._get_kwargs_from_api_dict(kwargs)
        super().__init__(_client=client, **kwargs)

    @classmethod
    def _is_api_dict(cls, d: Dict) -> bool:
        """Detect parsed Personio API data.

        If this smells like a Personio API response, return True, otherwise False.
        We assume it is a Personio API response, if we have only two keys: "type" and "attributes"

        :param d: the dict to inspect
        :return: True, iff the dict has just the keys "type" and "attributes"
        """
        return len(d) == 2 and 'type' in d and 'attributes' in d

    @classmethod
    def _get_kwargs_from_api_dict(cls, d: Dict) -> Dict:
        # handle 'type' & 'attributes', if available
        if 'type' in d and 'attributes' in d:
            cls._check_api_type(d)
            d = d['attributes']
        # transform the non-flat form of the input dictionary to a simple key-value dict
        if not cls._flat_dict:
            d = {k: v['value'] for k, v in d.items()}
        return d

    @classmethod
    def _check_api_type(cls, d: Dict[str, Any]):
        api_type_name = d['type']
        if api_type_name != cls._api_type_name:
            log_once(
                logging.WARNING,
                f"Unexpected API type '{api_type_name}' for class {cls.__name__}, "
                f"expected '{cls._api_type_name}' instead")

    class Config:
        extra = Extra.allow
        anystr_strip_whitespace = True


class AbsenceEntitlement(PersonioResource):
    _api_type_name = 'TimeOffType'

    id: int = None
    name: Optional[str] = None
    entitlement: Optional[float] = None


class AbsenceType(PersonioResource):
    _api_type_name = "TimeOffType"

    id: int = None
    name: Optional[str] = None
    unit: Optional[str] = None
    category: Optional[str] = None
    half_day_requests_enabled: Optional[bool] = None
    certification_required: Optional[bool] = None
    certification_submission_timeframe: Optional[int] = None
    substitute_option: Optional[str] = None
    approval_required: Optional[bool] = None


class CostCenter(PersonioResource):
    _api_type_name = 'CostCenter'

    id: int = None
    name: Optional[str] = None
    percentage: Optional[float] = None


class Department(PersonioResource):
    _api_type_name = 'Department'

    id: int = None
    name: Optional[str] = None


class HolidayCalendar(PersonioResource):
    _api_type_name = 'HolidayCalendar'

    id: int = None
    name: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None


class Office(PersonioResource):
    _api_type_name = 'Office'

    id: int = None
    name: Optional[str] = None


class ShortEmployee(PersonioResource):
    _api_type_name = "Employee"
    _flat_dict = False

    id: int = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None

    def resolve(self, client: 'Personio' = None) -> 'Employee':
        # TODO adjust
        client = client or self._client
        if client:
            return client.get_employee(self.id)
        else:
            raise PersonioError(
                f"no Personio client is is available in this {self.__class__.__name__} instance "
                f"to make a request for the full employee profile of "
                f"{self.first_name} {self.last_name} ({self.id})")


class Team(PersonioResource):
    _api_type_name = 'Team'

    id: int = None
    name: Optional[str] = None


class WorkSchedule(PersonioResource):
    _api_type_name = 'WorkSchedule'

    id: int = None
    name: Optional[str] = None
    valid_from: Optional[date] = None,
    monday: Optional[timedelta] = None,
    tuesday: Optional[timedelta] = None,
    wednesday: Optional[timedelta] = None,
    thursday: Optional[timedelta] = None,
    friday: Optional[timedelta] = None,
    saturday: Optional[timedelta] = None,
    sunday: Optional[timedelta] = None,

    def __init__(self, **kwargs):
        if self._is_api_dict(kwargs):
            kwargs = self._get_kwargs_from_api_dict(kwargs)
        # fix the time format so that it can be parsed as timedelta
        for key, field in self.__fields__.items():
            value = kwargs.get(key)
            if value and field.type_ == timedelta and value.count(':') < 2:
                kwargs[field.name] = value + ':00'
        super().__init__(**kwargs)


class Absence(PersonioResource):
    # TODO implement
    pass


class Attendance(PersonioResource):
    # TODO implement
    pass


class CustomFieldAlias(BaseModel):
    api_name: str
    """name of the field in the personio API (usually starts with 'dynamic_')"""
    alias: str
    """the alias to use as attribute name for the Employee object"""


class BaseEmployee(PersonioResource):
    _api_type_name = "Employee"
    _flat_dict = False
    custom_field_keys: ClassVar[List[str]] = None
    """the names of all known custom fields (usually starting with 'dynamic_')"""
    custom_field_aliases: ClassVar[Dict[str, str]] = None
    """mapping from all custom field names (starting with 'dynamic_') to their aliases"""

    id: int
    """unique identifier by which Personio refers to this employee"""
    first_name: Optional[str] = None
    """first name / given name of the employee"""
    last_name: Optional[str] = None
    """last name / surname / family name of the employee"""
    email: Optional[str] = None,
    """the employee's email address"""
    gender: Optional[str] = None,
    """the employee's gender"""
    status: Optional[str] = None,
    """the employee's employment status (active, inactive, ...)"""
    position: Optional[str] = None,
    """the employee's position / job title"""
    supervisor: Optional[ShortEmployee] = None,
    """the employee's current supervisor"""
    employment_type: Optional[str] = None,
    """the employee's employment type (internal, external)"""
    weekly_working_hours: Optional[str] = None,
    """the employee's weekly working hours, as contracted"""
    hire_date: Optional[datetime] = None,
    """the date when this employee was hired"""
    contract_end_date: Optional[datetime] = None,
    """when specified, this employee's contract will end at this date"""
    termination_date: Optional[datetime] = None,
    """date when this employee's contract has been terminated"""
    termination_type: Optional[str] = None,
    # TODO docstring
    termination_reason: Optional[str] = None,
    # TODO docstring
    probation_period_end: Optional[datetime] = None,
    """date at which this employee's probation period ends"""
    created_at: Optional[datetime] = None,
    """date at which this employee profile was created in Personio"""
    last_modified_at: Optional[datetime] = None,
    """date at which this employee profile was last updated in Personio"""
    subcompany: Optional[str] = None,
    """name of the subcompany this employee is working for"""
    office: Optional[Office] = None,
    """the office this employee is typically working from"""
    department: Optional[Department] = None,
    """the department this employee belongs to"""
    cost_centers: List[CostCenter] = None,
    """list of cost centers this employee is assigned to"""
    holiday_calendar: Optional[HolidayCalendar] = None,
    """the holiday calender which is valid for this employee"""
    absence_entitlement: List[AbsenceEntitlement] = None,
    """the list of absences this employee is entitled to (vacations, parental leave, etc.)"""
    work_schedule: Optional[WorkSchedule] = None,
    """the employee's work schedule (expected working hours per week day)"""
    fix_salary: Optional[float] = None,
    """the employee's fixed salary (without bonus payments)"""
    fix_salary_interval: Optional[str] = None,
    """the interval at which the fixed salary is paid (monthly, weekly, etc.)"""
    hourly_salary: Optional[float] = None,
    """the employee's hourly salary (as alternative to the fixed salary)"""
    vacation_day_balance: Optional[float] = None,
    """the employee's current vacation day balance (can be negative)"""
    last_working_day: Optional[datetime] = None,
    """the employee's last working day, in case the contract was terminated"""
    profile_picture: Optional[str] = None,
    """URL to this employee's profile picture"""
    team: Optional[Team] = None,
    """the team this employee is assigned to"""

    def __init__(self, client: 'Personio' = None, **kwargs):
        super().__init__(client=client, **kwargs)
        # TODO handle the 'dynamic_' fields

    # allow pretty names for dynamic fields, as extra attributes
    # use the `property` built-in function to link pretty names to the api name at runtime
    # also: add "label" as extra arg (see custom fields)
    # dynamically add field info with Model.__fields__['field'].field_info.extra['item'] = 42
    # or better yet as title: Model.__fields__['field'].field_info.title = "yolo"

    def foo(self):
        from pydantic import Field
        Field(title="42")

    @property
    def custom_fields(self) -> Dict[str, Any]:
        # return dynamic fields (keys and values) as ReadOnlyDict
        # to assign new values, use employee.dynamic_X directly
        return ReadOnlyDict((k, getattr(self, k)) for k in self.custom_field_keys)


# TODO override this at runtime with an extension of BaseEmployee that includes all dynamic fields
#   better yet: replace the existing implementation? subclass of same name?
#   https://pydantic-docs.helpmanual.io/usage/models/#dynamic-model-creation
Employee = TypeVar('Employee', bound=BaseEmployee)
