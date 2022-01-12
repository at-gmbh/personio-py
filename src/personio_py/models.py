"""
Definition of ORMs for objects that are available in the Personio API
"""
import logging
import unicodedata
from datetime import date, datetime, timedelta
from typing import Any, ClassVar, Dict, List, Optional, TYPE_CHECKING, Type, TypeVar

from pydantic import BaseModel, Extra, create_model, validator

from personio_py import PersonioError
from personio_py.util import ReadOnlyDict, log_once

if TYPE_CHECKING:
    # the Personio client should only be visible for type checkers to avoid circular imports
    from personio_py.client import Personio

logger = logging.getLogger('personio_py')

PersonioResourceType = TypeVar('PersonioResourceType', bound='PersonioResource')


class PersonioResource(BaseModel):
    # for class vars & private attributes, see
    # https://pydantic-docs.helpmanual.io/usage/models/#private-model-attributes

    _api_type_name: ClassVar[str] = None
    """the name of this resource type in the Personio API"""
    _flat_dict: ClassVar[bool] = True
    """Indicates if this class has a flat dictionary representation in the Personio API"""
    _client: ClassVar['Personio'] = None
    """reference to the API client that created this object (optional)"""

    def __init__(self, client: 'Personio' = None, **kwargs):
        PersonioResource._client = client
        if self._is_api_dict(kwargs):
            # smells like a parsed Personio API dict -> extract data
            kwargs = self._get_kwargs_from_api_dict(kwargs)
        super().__init__(**kwargs)

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

    @validator('*', pre=True)
    def empty_str_to_none(cls, v):
        """custom validator for Personio API objects that converts empty strings to None"""
        return None if v == '' else v

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
            if field.type_ == timedelta and isinstance(value, str) and value.count(':') < 2:
                kwargs[field.name] = value + ':00'
        super().__init__(**kwargs)


class Absence(PersonioResource):
    # TODO implement
    pass


class Attendance(PersonioResource):
    # TODO implement
    pass


class PersonioTags(list):

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, str):
            return [tag.strip() for tag in v.split(',')]
        elif isinstance(v, list):
            return v
        elif not v:
            return None
        else:
            raise TypeError(f"unexpected input type {type(v)}")


class CustomAttribute(BaseModel):
    _type_mapping: ClassVar[Dict[str, Type]] = {
        'standard': str,
        'date': datetime,
        'integer': int,
        'decimal': float,
        'list': str,
        'link': str,
        'tags': PersonioTags,
        'multiline': str,
    }

    key: Optional[str] = None,
    label: Optional[str] = None,
    type: Optional[str] = None,
    universal_id: Optional[str] = None,

    @property
    def py_type(self) -> Type:
        type_str = str(self.type).lower()
        if type_str in self._type_mapping:
            return self._type_mapping[type_str]
        else:
            raise PersonioError(f"unexpected custom attribute type {self.type}")


class BaseEmployee(PersonioResource):
    _api_type_name = "Employee"
    _flat_dict = False
    _custom_attribute_keys: ClassVar[List[str]] = []
    """the names of all known custom attributes (usually starting with 'dynamic_')"""
    _custom_attribute_aliases: ClassVar[Dict[str, str]] = None
    """mapping from all custom attribute names (starting with 'dynamic_') to their aliases"""

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
    """choice from a list of reasons for termination (retirement, temporary contract, etc.)"""
    termination_reason: Optional[str] = None,
    """free-text field where details about the termination can be stored"""
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

    @property
    def _custom_fields(self) -> Dict[str, Any]:
        # return dynamic fields (keys and values) as ReadOnlyDict
        # to assign new values, use employee.dynamic_X directly
        return ReadOnlyDict((k, getattr(self, k)) for k in self._custom_attribute_keys)

    @classmethod
    def _get_subclass_for_client(
            cls, client: 'Personio', aliases: Dict[str, str] = None) -> Type['BaseEmployee']:
        # override Employee at runtime with an extension of BaseEmployee that includes all
        # dynamic fields: https://pydantic-docs.helpmanual.io/usage/models/#dynamic-model-creation

        # get custom attributes, generate subclass
        attributes = client.get_custom_attributes()
        dynamic_attributes = [a for a in attributes if a.key.startswith('dynamic_')]
        pydantic_fields = {a.key: (Optional[a.py_type], None) for a in dynamic_attributes}
        Employee = create_model(
            'Employee',
            __base__=BaseEmployee,
            **pydantic_fields
        )
        # set class variables
        aliases = aliases or {}
        cls._custom_attribute_keys = [a.key for a in dynamic_attributes]
        cls._custom_attribute_aliases = {
            a.key: aliases.get(a.key) or cls._get_attribute_name_for(a.label)
            for a in dynamic_attributes}

        # add metadata to pydantic fields
        attributes_dict = {a.key: a for a in attributes}
        for key, field in Employee.__fields__.items():
            if key in attributes_dict:
                field.field_info.title = attributes_dict[key].label

        # add aliases as properties
        for attribute in dynamic_attributes:
            key = attribute.key
            alias = cls._custom_attribute_aliases[key]
            if hasattr(Employee, alias):
                logger.warning(f"cannot add alias '{alias}' for '{key}' to the Employee "
                               f"class, because that attribute already exists.")
            else:
                # TODO this does not seem to work as expected
                prop = property(
                    fget=lambda self: getattr(self, key),
                    fset=lambda self, value: setattr(self, key, value),
                    doc=f"alias for {key} ({attribute.label})"
                )
                setattr(Employee, alias, prop)

        # TODO statically assign to "Employee", so it can be imported from anywhere...
        return Employee

    @classmethod
    def _get_attribute_name_for(cls, name: str) -> Optional[str]:
        if not name or not name.strip():
            return None
        # we want a lowercase attribute name
        result = name.lower()
        # special handling of German non-ascii letters, because Personio is a German company ;)
        table = str.maketrans({'ä': 'ae', 'ö': 'oe', 'ü': 'ue', 'ß': 'ss'})
        result = result.translate(table)
        # convert unicode chars to their closest ascii equivalents, ignoring the rest
        result = unicodedata.normalize('NFKD', result).encode('ascii', 'ignore').decode()
        # keep only letters, digits and whitespace
        result = ''.join(c for c in result if c.isalnum() or c.isspace())
        # remove consecutive whitespace and join tokens with underscores
        result = '_'.join(result.split())
        # remove leading digits, since they are not allowed in python attribute names
        result = result.lstrip('0123456789_')
        return result


# Here, Employee is just an alias for BaseEmployee
# As soon as we have access to the Personio API, we generate a subclass (at runtime) which contains
# all the custom fields and their types.
Employee = BaseEmployee
