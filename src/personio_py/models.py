"""
Definition of ORMs for objects that are available in the Personio API
"""
import inspect
import logging
import operator
import sys
import unicodedata
from datetime import date, datetime, time, timedelta
from typing import TYPE_CHECKING, Any, ClassVar, Dict, List, Optional, Tuple, Type, TypeVar, Union

from pydantic import BaseModel, ConfigDict, Extra, Field, GetCoreSchemaHandler, PrivateAttr, \
    create_model, field_validator
from pydantic_core import CoreSchema, core_schema

from personio_py import PersonioError, g
from personio_py.util import ReadOnlyDict, log_once

if TYPE_CHECKING:
    # the Personio client should only be visible for type checkers to avoid circular imports
    from personio_py import Personio

logger = logging.getLogger('personio_py')
PersonioResourceType = TypeVar('PersonioResourceType', bound='PersonioResource', covariant=True)


class PersonioResource(BaseModel):
    # for class vars & private attributes, see
    # https://pydantic-docs.helpmanual.io/usage/models/#private-model-attributes

    _api_type_name: ClassVar[str] = None
    """the name of this resource type in the Personio API"""
    _flat_dict: ClassVar[bool] = True
    """Indicates if this class has a flat dictionary representation in the Personio API"""

    def __init__(self, **kwargs):
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
        return 'type' in d and 'attributes' in d and (len(d) == 2 or (len(d) == 3 and 'id' in d))

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
    def _add_api_dict_field(
            cls, resource: PersonioResourceType, d: Dict, field: Union[str, Tuple[str, str]],
            required=False):
        if isinstance(field, tuple):
            key_get, key_set = field
        else:
            key_get = key_set = field
        try:
            value = operator.attrgetter(key_get)(resource)
        except AttributeError:
            value = None
        if value is not None:
            if isinstance(value, datetime) or isinstance(value, date):
                value = value.isoformat()[:10]
            d[key_set] = value
        elif required:
            raise PersonioError(f"required field {field} has no value")

    @field_validator('*', mode="before")
    def _empty_str_to_none(cls, v):
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

    model_config = ConfigDict(extra=Extra.ignore, str_strip_whitespace=True,
                              populate_by_name=True)


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

    def resolve(self) -> 'Employee':
        return g.get_client().get_employee(self.id)


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
        # for key, field in self.model_fields.items():
        #     if key == "id":
        #         continue
        #     value = kwargs.get(key)
        #     if timedelta in field.annotation.__args__ and \
        #        isinstance(value, str) and value.count(':') < 2:
        #         kwargs[key] = value + ':00'
        super().__init__(**kwargs)


class Absence(PersonioResource):
    _api_type_name = 'TimeOffPeriod'
    _api_fields_required: ClassVar[List] = [
        ('employee.id', 'employee_id'), ('time_off_type.id', 'time_off_type_id'),
        'start_date', 'end_date', 'half_day_start', 'half_day_end']
    _api_fields_optional: ClassVar[List] = ['comment']

    id: int = None
    status: Optional[str] = None
    comment: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    days_count: Optional[float] = None
    half_day_start: Optional[bool] = None
    half_day_end: Optional[bool] = None
    time_off_type: Optional[AbsenceType] = None
    employee: Optional[ShortEmployee] = None
    certificate: Optional[Certificate] = None
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_validator('start_date', 'end_date', mode="before")
    def _datetime_to_date(cls, v):
        if v and isinstance(v, str):
            return v[:10]
        return v

    def create(self) -> 'Absence':
        return g.get_client().create_absence(self)

    def delete(self):
        return g.get_client().delete_absence(self)

    def get_employee(self):
        return self.employee.resolve()

    def to_api_dict(self) -> Dict:
        data = {}
        for field in self._api_fields_required:
            self._add_api_dict_field(self, data, field, required=True)
        for field in self._api_fields_optional:
            self._add_api_dict_field(self, data, field, required=False)
        return data

    @field_validator('employee', mode="before")
    def short_employee_conversion(cls, v):
        if isinstance(v, Employee):
            return v.to_short_employee()
        return v


class Project(PersonioResource):
    _api_type_name = "Project"

    id: int = None
    name: Optional[str] = None
    active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def create(self):
        return g.get_client().create_project(self)

    def delete(self):
        return g.get_client().delete_project(self)

    def update(self):
        return g.get_client().update_project(self)

    def to_body_params(self):
        data = {
            'name': self.name,
            'active': self.active}
        return data

    def _get_kwargs_from_api_dict(cls, d: Dict) -> Dict:
        # handle 'type' & 'attributes', if available
        id = d.get('id')
        # keep id for project
        if 'type' in d and 'attributes' in d:
            cls._check_api_type(d)
            d = d['attributes']
            d['id'] = id
        # transform the non-flat form of the input dictionary to a simple key-value dict
        if not cls._flat_dict:
            d = {k: v['value'] for k, v in d.items()}
        return d


class Attendance(PersonioResource):
    _api_type_name = 'AttendancePeriod'

    id: int = None
    employee: Optional[int] = None
    day: Optional[date] = Field(None, alias='date')
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    break_duration: Optional[int] = Field(None, alias='break')
    comment: Optional[str] = None

    def create(self):
        return g.get_client().create_attendances([self])

    def update(self):
        return g.get_client().update_attendance(self)

    def delete(self):
        return g.get_client().delete_attendance(self)

    def get_employee(self):
        return g.get_client().get_employee(self.employee)

    def to_body_params(self, patch_existing_attendance=False):
        """
        Return the Attendance object in the representation expected by the Personio API

        For an attendance record to be created all_values_required needs to be True.
        For patch operations only the attendance id is required, but it is not
        included into the body params.

        :param patch_existing_attendance Get patch body. If False a create body is returned.
        """
        if patch_existing_attendance:
            if self.id is None:
                raise ValueError("An attendance id is required")
            body_dict = {}
            if self.day is not None:
                body_dict['date'] = self.day.strftime("%Y-%m-%d")
            if self.start_time is not None:
                body_dict['start_time'] = str(self.start_time)
            if self.end_time is not None:
                body_dict['end_time'] = str(self.end_time)
            if self.break_duration is not None:
                body_dict['break'] = self.break_duration
            if self.comment is not None:
                body_dict['comment'] = self.comment
            return body_dict
        else:
            return {"employee": self.employee,
                    "date": self.day.strftime("%Y-%m-%d"),
                    "start_time": str(self.start_time),
                    "end_time": str(self.end_time),
                    "break": self.break_duration or 0,
                    "comment": self.comment or ""}

    def _get_kwargs_from_api_dict(cls, d: Dict) -> Dict:
        # handle 'type' & 'attributes', if available
        id = d.get('id')
        # keep id for attendance
        if 'type' in d and 'attributes' in d:
            cls._check_api_type(d)
            d = d['attributes']
            d['id'] = id
        # transform the non-flat form of the input dictionary to a simple key-value dict
        if not cls._flat_dict:
            d = {k: v['value'] for k, v in d.items()}
        return d


class AbsenceBalance(PersonioResource):
    id: int = None
    name: Optional[str] = None
    balance: Optional[float] = None


class PersonioTags(list):

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any,
                                     handler: GetCoreSchemaHandler) -> CoreSchema:
        return core_schema.no_info_after_validator_function(cls.validate, core_schema.str_schema())

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
        # standard text field, no line breaks
        'standard': str,
        # a date field. the API provides date and time information as ISO 8601 string
        'date': datetime,
        # an interger field
        'integer': int,
        # a float field (limited precision)
        'decimal': float,
        # "list" refers to an option field, where only one item can be selected.
        # only the selected item is provided by the API, therefore this is a string.
        'list': str,
        # a hyperlink
        'link': str,
        # "tags" refers to a multiple choice field, where you can select 0 or more items from a
        # predefined list of items. The list of all selected items is provided by the API.
        'tags': list[str],
        # a multiline text field, can contain line breaks
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
    """a cache of setter functions for all custom attributes"""
    _picture: Dict[Union[int, None], bytes] = PrivateAttr(default_factory=dict)
    """the Employee's picture is cached in this attribute on first request
    (mapping from image width to image bytes)"""
    _api_fields_required: ClassVar[List] = [
        'email', 'first_name', 'last_name']
    """these are the standard fields that are required by the Employee create/update API"""
    _api_fields_optional: ClassVar[List] = [
        'gender', 'position', 'subcompany', ('department.name', 'department'),
        ('office.name', 'office'), 'hire_date', 'weekly_working_hours']
    """these are the standard fields that are supported by the Employee create/update API,
    but optional. Any other standard fields besides those defined in `_api_fields_required` are
    not supported and will by ignored by the Personio API"""

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
    hire_date: Optional[date] = None
    """the date when this employee was hired"""
    contract_end_date: Optional[date] = None
    """when specified, this employee's contract will end at this date"""
    termination_date: Optional[date] = None
    """date when this employee's contract has been terminated"""
    termination_type: Optional[str] = None
    """choice from a list of reasons for termination (retirement, temporary contract, etc.)"""
    termination_reason: Optional[str] = None
    """free-text field where details about the termination can be stored"""
    probation_period_end: Optional[date] = None
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
    last_working_day: Optional[date] = None
    """the employee's last working day, in case the contract was terminated"""
    profile_picture: Optional[str] = None
    """URL to this employee's profile picture"""
    team: Optional[Team] = None
    """the team this employee is assigned to"""

    @field_validator('hire_date', 'contract_end_date', 'termination_date', 'probation_period_end',
                     'last_working_day', mode="before")
    def _datetime_to_date(cls, v):
        if v and isinstance(v, str):
            return v[:10]
        return v

    def create(self, refresh=True) -> 'Employee':
        return g.get_client().create_employee(self, refresh=refresh)

    def update(self, refresh=True) -> 'Employee':
        return g.get_client().update_employee(self, refresh=refresh)

    def absence_balance(self) -> List[AbsenceBalance]:
        return g.get_client().get_absence_balance(self)

    def picture(self, width: int = None) -> Optional[bytes]:
        """
        Get the profile picture of this employee as image file (usually png or jpg).
        The data will be cached locally, so subsequent requests of a profile picture
        of the same size will be fast.

        :param width: optionally scale the profile picture to this width.
               Defaults to the original width of the profile picture.
        :return: the profile picture as png or jpg file (bytes)
        """
        if width not in self._picture:
            self._picture[width] = g.get_client().get_employee_picture(self, width=width)
        return self._picture[width]

    def to_api_dict(self) -> Dict:
        """
        Convert this Employee instance to a dictionary in the format expected by the Personio API
        endpoints to create a new employee or update an existing employee.

        Please note that only a subset of all Employee fields is supported by the create/update API
        of Personio. These are the fields defined in `Employee._api_fields_required`,
        `Employee._api_fields_optional` as well as all custom attributes.

        :return: the Employee object as dict, in the format expected by the Personio
                 create/update API
        """
        data = {}
        custom_attributes = {}
        for field in self._api_fields_required:
            self._add_api_dict_field(self, data, field, required=True)
        for field in self._api_fields_optional:
            self._add_api_dict_field(self, data, field, required=False)
        for field in self._custom_attribute_keys:
            self._add_api_dict_field(self, custom_attributes, field, required=False)
        if custom_attributes:
            data['custom_attributes'] = custom_attributes
        return {'employee': data}

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
        cls._custom_attribute_keys = [a.key for a in dynamic_attributes]
        cls._custom_attribute_aliases = {
            a.key: aliases.get(a.key) or cls._get_attribute_name_for(a.label)
            for a in dynamic_attributes}
        # add metadata to pydantic fields
        attributes_dict = {a.key: a for a in attributes}
        for key, field in employee_cls.model_fields.items():
            if key in attributes_dict:
                field.title = attributes_dict[key].label
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

    def to_short_employee(self):
        return ShortEmployee(id=self.id, first_name=self.first_name,
                             last_name=self.last_name, email=self.email)


# Here, Employee is just an alias for BaseEmployee
# As soon as we have access to the Personio API, we generate a subclass (at runtime) which contains
# all the custom fields and their types, and update this variable.
employee_classes: Dict[str, Type[BaseEmployee]] = {}
Employee = BaseEmployee


def update_model(client: 'Personio', *globals_dicts: Dict):
    """Updates the model based on the state of the specified client instance.

    Note that this will create static references that will be overwritten when the next Personio
    client instance is created.

    :param client: the Personio client instance to use for the model update
    :param globals_dicts: override Employee in the specified globals dicts
      (useful to update other modules)
    """
    # update the client reference
    g.client = client
    # create a subclass of BaseEmployee that contains all custom attributes
    if client.client_id not in employee_classes:
        cls = BaseEmployee._get_subclass_for_client(client, client.employee_aliases)
        employee_classes[client.client_id] = cls
    cls = employee_classes[client.client_id]
    # set the Employee subclass for this Personio instance as the new default
    global Employee
    Employee = cls
    # replace the Employee class in the specified globals dict (if available)
    if globals_dicts:
        for gd in globals_dicts:
            gd['Employee'] = cls
    # additionally, we replace the class definition in sys.modules,
    # so that from personio_py import Employee works as expected
    sys.modules['personio_py'].Employee = cls
