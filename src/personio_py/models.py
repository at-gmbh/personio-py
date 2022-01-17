"""
Definition of ORMs for objects that are available in the Personio API
"""
import inspect
import logging
import sys
import unicodedata
from datetime import date, datetime, time, timedelta
from typing import Any, ClassVar, Dict, List, Optional, TYPE_CHECKING, Type, TypeVar

from pydantic import BaseModel, Extra, Field, PrivateAttr, create_model, validator

from personio_py import PersonioError
from personio_py.util import ReadOnlyDict, log_once

if TYPE_CHECKING:
    # the Personio client should only be visible for type checkers to avoid circular imports
    from personio_py.client import Personio

logger = logging.getLogger('personio_py')
PersonioResourceType = TypeVar('PersonioResourceType', bound='PersonioResource', covariant=True)


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
        if 'type' in d and 'attributes' in d:
            if len(d) == 2:
                return True
            elif len(d) == 3 and 'id' in d:
                return True
        return False

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

    @classmethod
    def _get_client(cls, client: 'Personio' = None) -> 'Personio':
        if client or cls._client:
            return client or cls._client
        raise PersonioError(f"no Personio client reference is available, please provide it to "
                            f"your {type(cls).__name__} or as function parameter")

    @validator('*', pre=True)
    def empty_str_to_none(cls, v):
        """custom validator for Personio API objects that converts empty strings to None"""
        return None if v == '' else v

    def __hash__(self):
        list_fields = [(k, tuple(v)) for k, v in self.__dict__.items() if isinstance(v, list)]
        if list_fields:
            list_field_keys, list_field_values = zip(*list_fields)
            other_values = [v for k, v in self.__dict__.items() if k not in list_field_keys]
            field_tuple = tuple(list_field_values) + tuple(other_values)
        else:
            field_tuple = tuple(self.__dict__.values())
        return hash((type(self),) + field_tuple)

    class Config:
        extra = Extra.ignore
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


class Certificate(PersonioResource):
    status: Optional[str] = None


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
    valid_from: Optional[date] = None
    monday: Optional[timedelta] = None
    tuesday: Optional[timedelta] = None
    wednesday: Optional[timedelta] = None
    thursday: Optional[timedelta] = None
    friday: Optional[timedelta] = None
    saturday: Optional[timedelta] = None
    sunday: Optional[timedelta] = None

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
    _api_type_name = 'TimeOffPeriod'

    id: int = None
    status: Optional[str] = None
    comment: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    days_count: Optional[float] = None
    half_day_start: Optional[bool] = None
    half_day_end: Optional[bool] = None
    time_off_type: Optional[AbsenceType] = None
    employee: Optional[ShortEmployee] = None
    certificate: Optional[Certificate] = None
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def create(self, client: 'Personio' = None):
        return self._get_client(client).create_absence(self)

    def delete(self, client: 'Personio' = None):
        return self._get_client(client).delete_absence(self)


class Attendance(PersonioResource):
    _api_type_name = 'AttendancePeriod'

    employee: Optional[int] = None
    day: Optional[date] = Field(None, alias='date')
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    break_minutes: Optional[int] = Field(None, alias='break')
    comment: Optional[str] = None
    updated_at: Optional[datetime] = None
    status: Optional[str] = None
    is_holiday: Optional[bool] = None
    is_on_time_off: Optional[bool] = None

    def create(self, client: 'Personio' = None):
        return self._get_client(client).create_attendances(self)

    def update(self, client: 'Personio' = None):
        return self._get_client(client).update_attendance(self)

    def delete(self, client: 'Personio' = None):
        return self._get_client(client).delete_attendance(self)


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

    key: Optional[str] = None
    label: Optional[str] = None
    type: Optional[str] = None
    universal_id: Optional[str] = None

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
    _custom_attribute_aliases: ClassVar[Dict[str, str]] = {}
    """mapping from all custom attribute names (starting with 'dynamic_') to their aliases"""
    _property_setters: ClassVar[Dict[str, property]] = {}
    _picture: Optional[bytes] = PrivateAttr(None)

    id: int = None
    """unique identifier by which Personio refers to this employee"""
    first_name: Optional[str] = None
    """first name / given name of the employee"""
    last_name: Optional[str] = None
    """last name / surname / family name of the employee"""
    email: Optional[str] = None
    """the employee's email address"""
    gender: Optional[str] = None
    """the employee's gender"""
    status: Optional[str] = None
    """the employee's employment status (active, inactive, ...)"""
    position: Optional[str] = None
    """the employee's position / job title"""
    supervisor: Optional[ShortEmployee] = None
    """the employee's current supervisor"""
    employment_type: Optional[str] = None
    """the employee's employment type (internal, external)"""
    weekly_working_hours: Optional[str] = None
    """the employee's weekly working hours, as contracted"""
    hire_date: Optional[datetime] = None
    """the date when this employee was hired"""
    contract_end_date: Optional[datetime] = None
    """when specified, this employee's contract will end at this date"""
    termination_date: Optional[datetime] = None
    """date when this employee's contract has been terminated"""
    termination_type: Optional[str] = None
    """choice from a list of reasons for termination (retirement, temporary contract, etc.)"""
    termination_reason: Optional[str] = None
    """free-text field where details about the termination can be stored"""
    probation_period_end: Optional[datetime] = None
    """date at which this employee's probation period ends"""
    created_at: Optional[datetime] = None
    """date at which this employee profile was created in Personio"""
    last_modified_at: Optional[datetime] = None
    """date at which this employee profile was last updated in Personio"""
    subcompany: Optional[str] = None
    """name of the subcompany this employee is working for"""
    office: Optional[Office] = None
    """the office this employee is typically working from"""
    department: Optional[Department] = None
    """the department this employee belongs to"""
    cost_centers: List[CostCenter] = None
    """list of cost centers this employee is assigned to"""
    holiday_calendar: Optional[HolidayCalendar] = None
    """the holiday calender which is valid for this employee"""
    absence_entitlement: List[AbsenceEntitlement] = None
    """the list of absences this employee is entitled to (vacations, parental leave, etc.)"""
    work_schedule: Optional[WorkSchedule] = None
    """the employee's work schedule (expected working hours per week day)"""
    fix_salary: Optional[float] = None
    """the employee's fixed salary (without bonus payments)"""
    fix_salary_interval: Optional[str] = None
    """the interval at which the fixed salary is paid (monthly, weekly, etc.)"""
    hourly_salary: Optional[float] = None
    """the employee's hourly salary (as alternative to the fixed salary)"""
    vacation_day_balance: Optional[float] = None
    """the employee's current vacation day balance (can be negative)"""
    last_working_day: Optional[datetime] = None
    """the employee's last working day, in case the contract was terminated"""
    profile_picture: Optional[str] = None
    """URL to this employee's profile picture"""
    team: Optional[Team] = None
    """the team this employee is assigned to"""

    def __init__(self, client: 'Personio' = None, **kwargs):
        super().__init__(client=client, **kwargs)

    def create(self, client: 'Personio' = None, refresh=True) -> 'Employee':
        return self._get_client(client).create_employee(self, refresh=refresh)

    def update(self, client: 'Personio' = None, refresh=True):
        return self._get_client(client).update_employee(self, refresh=refresh)

    def picture(self, client: 'Personio' = None, width: int = None) -> Optional[bytes]:
        if self._picture is None:
            self._picture = self._get_client(client).get_employee_picture(self, width=width)
        return self._picture

    def __setattr__(self, name, value):
        """
        Workaround for an open issue in pydantic that prevents the use of property setters.

        We override pydantic's `BaseModel.__setattr__` and catch a ValueError, which occurs if we
        try to use a property setter, which is not one of pydantic's known fields.
        Then we check if the field name is actually a property that has a setter function and
        make use of it. Otherwise we re-raise the ValueError that was caught.
        The property setters are retrieved with python's `inspect` module and are cached in this
        class. If a ValueError is raised for an attribute and we don't have that attribute name
        in the property setter cache, we run the inspection again.

        Related issues:

        https://github.com/samuelcolvin/pydantic/issues/1577
        https://github.com/samuelcolvin/pydantic/issues/3395

        :param name: name of the attribute
        :param value: the value to set
        """
        try:
            super().__setattr__(name, value)
        except ValueError as e:
            if name not in self._property_setters:
                self.__cache_property_setters()
            if name in self._property_setters:
                object.__setattr__(self, name, value)
            else:
                raise e

    @classmethod
    def __cache_property_setters(cls):
        """
        Gets all properties of this class that have a setter function and stores them
        as dictionary (property name -> instance) in `cls._property_setters`
        """
        setters = inspect.getmembers(
            cls, predicate=lambda x: isinstance(x, property) and x.fset is not None)
        cls._property_setters = {name: prop for name, prop in setters}

    @property
    def _custom_fields(self) -> Dict[str, Any]:
        # return dynamic fields (keys and values) as ReadOnlyDict
        # to assign new values, use employee.dynamic_X directly
        return ReadOnlyDict((k, getattr(self, k)) for k in self._custom_attribute_keys)

    @classmethod
    def _get_subclass_for_client(
            cls, client: 'Personio', aliases: Dict[str, str] = None) -> Type['BaseEmployee']:
        """Generate a new subclass of BaseEmployee that contains all custom attributes.

        The subclass will contain:

        * all custom attributes, as defined in the Personio "custom-attributes" endpoint,
          as well as their types for automatic type conversion with pydantic
        * aliases for all custom attributes as property functions. Aliases are preferred from
          the specified aliases dict, but if not provided, names are automatically generated
          from the labels of the custom attributes. Label names are reduced to latin characters
          and digits and whitespace replaced with underscores, e.g. a label like "Phone (office)"
          would become "phone_office".
        * label names for all attributes (pydantic Field metadata)
        * class variables that describe the custom attributes and their aliases

        Learn more about dynamic model creation:
        https://pydantic-docs.helpmanual.io/usage/models/#dynamic-model-creation

        :param client: the Personio client instance to generate a dynamic model for
        :param aliases: custom aliases provided by the user (optional)
        :return: the class definition of the new Employee subclass
        """
        # get custom attributes, generate subclass
        attributes = client.get_custom_attributes()
        dynamic_attributes = [a for a in attributes if a.key.startswith('dynamic_')]
        pydantic_fields = {a.key: (Optional[a.py_type], None) for a in dynamic_attributes}
        employee_cls = create_model(
            'Employee',
            __base__=BaseEmployee,
            __module__='personio_py.models',
            **pydantic_fields
        )
        # set class variables
        aliases = aliases or {}
        employee_cls._client = client
        cls._custom_attribute_keys = [a.key for a in dynamic_attributes]
        cls._custom_attribute_aliases = {
            a.key: aliases.get(a.key) or cls._get_attribute_name_for(a.label)
            for a in dynamic_attributes}
        # add metadata to pydantic fields
        attributes_dict = {a.key: a for a in attributes}
        for key, field in employee_cls.__fields__.items():
            if key in attributes_dict:
                field.field_info.title = attributes_dict[key].label
        # add aliases as properties
        for attribute in dynamic_attributes:
            key = attribute.key
            alias = cls._custom_attribute_aliases[key]
            if hasattr(employee_cls, alias):
                logger.warning(f"cannot add alias '{alias}' for '{key}' to the Employee "
                               f"class, because that attribute already exists.")
            else:
                cls.__set_alias_property(employee_cls, key, alias, attribute.label)
        return employee_cls

    @staticmethod
    def __set_alias_property(cls: Type, attr: str, alias: str, label: str):
        """Add a new property to a class which serves as an alias to an existing attribute.

        :param cls: add the new property to this class
        :param attr: the original attribute to reference
        :param alias: the alias for the original attribute
        :param label: a properly formatted name/label/title for the alias (used in the docstring)
        """
        prop = property(
            fget=lambda self: getattr(self, attr),
            fset=lambda self, value: setattr(self, attr, value),
            doc=f"{alias} ({label}) is an alias for {attr}"
        )
        setattr(cls, alias, prop)

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
# all the custom fields and their types, and update this variable.
employee_classes: Dict[str, Type[BaseEmployee]] = {}
Employee = BaseEmployee


def update_model(client: 'Personio'):
    """Updates the model based on the state of the specified client instance.

    Note that this will create static references that will be overwritten when the next Personio
    client instance is created.

    :param client: the Personio client instance to use for the model update
    """
    # create a subclass of BaseEmployee that contains all custom attributes
    if client.client_id not in employee_classes:
        cls = BaseEmployee._get_subclass_for_client(client, client.employee_aliases)
        employee_classes[client.client_id] = cls
    # set the Employee subclass for this Personio instance as the new default
    global Employee
    Employee = employee_classes[client.client_id]
    # additionally, we replace the class definition in sys.modules,
    # so that from personio_py import Employee works as expected
    sys.modules['personio_py'].Employee = employee_classes[client.client_id]
    # set this client instance as static attribute of the employee class
    PersonioResource._client = client
