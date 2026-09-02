"""
Definition of ORMs for objects that are available in the Personio API.

The models are `pydantic <https://docs.pydantic.dev/>`_ models: parsing, validation and
serialization are handled by pydantic. Objects that are returned by a :class:`Personio` client
are bound to that client instance (see :meth:`PersonioResource._bind_client`), which enables the
convenience methods like ``employee.update()`` or ``absence.create()`` to make API calls without
requiring an explicit client reference.
"""

import inspect
import json
import logging
import operator
import unicodedata
from datetime import date, datetime, time, timedelta
from typing import TYPE_CHECKING, Annotated, Any, ClassVar, Optional, TypeVar, get_args

from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    PrivateAttr,
    create_model,
    field_validator,
)

from personio_py.errors import PersonioError
from personio_py.util import ReadOnlyDict, log_once

if TYPE_CHECKING:
    # the Personio client is only imported for type checkers to avoid a circular import
    from personio_py.client import Personio

logger = logging.getLogger("personio_py")
PersonioResourceType = TypeVar("PersonioResourceType", bound="PersonioResource", covariant=True)


class PersonioResource(BaseModel):
    # for class vars & private attributes, see
    # https://docs.pydantic.dev/latest/concepts/models/#private-model-attributes
    _api_type_name: ClassVar[str | None] = None
    """the name of this resource type in the Personio API"""
    _flat_dict: ClassVar[bool] = True
    """Indicates if this class has a flat dictionary representation in the Personio API"""

    # Model Config https://docs.pydantic.dev/latest/concepts/config/
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True, populate_by_name=True)

    _client: "Personio | None" = PrivateAttr(default=None)
    """the Personio client this object is bound to (set by the client for objects it returns)"""

    def __init__(self, **kwargs):
        if self._is_api_dict(kwargs):
            # smells like a parsed Personio API dict -> extract data
            kwargs = self._get_kwargs_from_api_dict(kwargs)
        super().__init__(**kwargs)

    @classmethod
    def _is_api_dict(cls, d: dict) -> bool:
        """Detect parsed Personio API data.

        If this smells like a Personio API response, return True, otherwise False.
        We assume it is a Personio API response, if we have only two keys: "type" and "attributes"

        :param d: the dict to inspect
        :return: True, iff the dict has just the keys "type" and "attributes"
        """
        return "type" in d and "attributes" in d and (len(d) == 2 or (len(d) == 3 and "id" in d))

    @classmethod
    def _get_kwargs_from_api_dict(cls, d: dict) -> dict:
        # handle 'type' & 'attributes', if available
        if "type" in d and "attributes" in d:
            cls._check_api_type(d)
            d = d["attributes"]
        # transform the non-flat form of the input dictionary to a simple key-value dict
        if not cls._flat_dict:
            d = {k: v["value"] for k, v in d.items()}
        return d

    @classmethod
    def _check_api_type(cls, d: dict[str, Any]):
        api_type_name = d["type"]
        if api_type_name != cls._api_type_name:
            log_once(
                logging.WARNING,
                f"Unexpected API type '{api_type_name}' for class {cls.__name__}, "
                f"expected '{cls._api_type_name}' instead",
            )

    @classmethod
    def _add_api_dict_field(
        cls,
        resource: "PersonioResource",
        d: dict,
        field: str | tuple[str, str],
        required=False,
    ):
        if isinstance(field, tuple):
            key_get, key_set = field
        else:
            key_get = key_set = field
        try:
            value = operator.attrgetter(key_get)(resource)
        except AttributeError:
            value = None
        if value is not None:
            if isinstance(value, (datetime, date)):
                value = value.isoformat()[:10]
            d[key_set] = value
        elif required:
            raise PersonioError(f"required field {field} has no value")

    @field_validator("*", mode="before")
    @classmethod
    def _empty_to_none(cls, v, info):
        """Convert empty values from the Personio API to None.

        The Personio API sometimes returns an empty string ``""`` or an empty list ``[]`` instead
        of ``null`` for a field that has no value. Empty strings are always mapped to None. Empty
        lists are only mapped to None for *object* fields (e.g. an empty ``work_schedule`` returned
        as ``[]``); for genuine list fields (e.g. ``cost_centers``) an empty list is preserved.
        Without this, validation of the target type (or serialization) would fail.
        """
        if v == "":
            return None
        if v == [] and cls._is_object_field(info.field_name):
            return None
        return v

    @classmethod
    def _is_object_field(cls, field_name: str) -> bool:
        """Return True if the given field holds a single nested :class:`PersonioResource`.

        List fields (e.g. ``list[CostCenter]``) and scalar fields return False; only fields typed
        as an (optional) nested resource object return True.
        """
        field = cls.model_fields.get(field_name)
        if field is None:
            return False
        ann = field.annotation
        args = get_args(ann)
        if args:
            # unwrap Optional[...] (a Union that contains NoneType) to its single non-None type;
            # anything else (a real Union or a generic like list[...]) is not a plain object field
            non_none = [a for a in args if a is not type(None)]
            if len(non_none) == 1 and type(None) in args:
                ann = non_none[0]
            else:
                return False
        return isinstance(ann, type) and issubclass(ann, PersonioResource)

    def _bind_client(self, client: "Personio") -> "PersonioResource":
        """Attach a Personio client to this resource and all nested resources.

        The client sets itself on every object it returns, so that convenience methods like
        ``create()``/``update()``/``delete()``/``resolve()`` can make API calls. The binding is
        applied recursively to nested :class:`PersonioResource` fields (e.g. ``absence.employee``).

        :param client: the Personio client to bind
        :return: this object (to allow ``return Employee(**d)._bind_client(self)``)
        """
        self._client = client
        for value in self.__dict__.values():
            if isinstance(value, PersonioResource):
                value._bind_client(client)
            elif isinstance(value, (list, tuple)):
                for item in value:
                    if isinstance(item, PersonioResource):
                        item._bind_client(client)
        return self

    def _get_client(self) -> "Personio":
        """Return the bound Personio client or raise a helpful error if there is none."""
        if self._client is None:
            raise PersonioError(
                "This object is not bound to a Personio client. Convenience methods like "
                "create()/update()/delete() are only available on objects that were returned by "
                "a Personio client. Use the corresponding method on the client instead."
            )
        return self._client

    def __eq__(self, other):
        """Two resources are equal if they have the same type and the same field values.

        The bound client (``_client``, a private attribute) is intentionally ignored, so that two
        objects with identical data compare equal regardless of which client fetched them (or
        whether they are bound to a client at all).
        """
        if self is other:
            return True
        if not isinstance(other, PersonioResource):
            return NotImplemented
        return type(self) is type(other) and self.__dict__ == other.__dict__

    def __hash__(self):
        list_fields = [(k, tuple(v)) for k, v in self.__dict__.items() if isinstance(v, list)]
        if list_fields:
            list_field_keys, list_field_values = zip(*list_fields)
            other_values = [v for k, v in self.__dict__.items() if k not in list_field_keys]
            field_tuple = tuple(list_field_values) + tuple(other_values)
        else:
            field_tuple = tuple(self.__dict__.values())
        return hash((type(self),) + field_tuple)


class AbsenceEntitlement(PersonioResource):
    _api_type_name = "TimeOffType"

    id: int | None = None
    name: str | None = None
    entitlement: float | None = None


class AbsenceType(PersonioResource):
    _api_type_name = "TimeOffType"

    id: int | None = None
    name: str | None = None
    unit: str | None = None
    category: str | None = None
    half_day_requests_enabled: bool | None = None
    certification_required: bool | None = None
    certification_submission_timeframe: int | None = None
    substitute_option: str | None = None
    approval_required: bool | None = None


class Certificate(PersonioResource):
    status: str | None = None


class CostCenter(PersonioResource):
    _api_type_name = "CostCenter"

    id: int | None = None
    name: str | None = None
    percentage: float | None = None


class Department(PersonioResource):
    _api_type_name = "Department"

    id: int | None = None
    name: str | None = None


class HolidayCalendar(PersonioResource):
    _api_type_name = "HolidayCalendar"

    id: int | None = None
    name: str | None = None
    country: str | None = None
    state: str | None = None


class Office(PersonioResource):
    _api_type_name = "Office"

    id: int | None = None
    name: str | None = None


class ShortEmployee(PersonioResource):
    _api_type_name = "Employee"
    _flat_dict = False

    id: int | None = None
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None

    def resolve(self) -> "Employee":
        return self._get_client().get_employee(self.id)


class Team(PersonioResource):
    _api_type_name = "Team"

    id: int | None = None
    name: str | None = None


class WorkSchedule(PersonioResource):
    _api_type_name = "WorkSchedule"

    id: int | None = None
    name: str | None = None
    valid_from: date | None = None
    monday: timedelta | None = None
    tuesday: timedelta | None = None
    wednesday: timedelta | None = None
    thursday: timedelta | None = None
    friday: timedelta | None = None
    saturday: timedelta | None = None
    sunday: timedelta | None = None

    @field_validator(
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
        mode="before",
    )
    @classmethod
    def _fix_time_format(cls, v):
        """The Personio API provides working hours as ``HH:MM`` strings (e.g. ``"08:00"``).

        pydantic's timedelta parser expects the seconds component (``HH:MM:SS``), so we append
        ``:00`` if it is missing.
        """
        if isinstance(v, str) and v.count(":") == 1:
            return v + ":00"
        return v


class Absence(PersonioResource):
    _api_type_name = "TimeOffPeriod"
    _api_fields_required: ClassVar[list] = [
        ("employee.id", "employee_id"),
        ("time_off_type.id", "time_off_type_id"),
        "start_date",
        "end_date",
        "half_day_start",
        "half_day_end",
    ]
    _api_fields_optional: ClassVar[list] = ["comment"]

    id: int | None = None
    status: str | None = None
    comment: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    days_count: float | None = None
    half_day_start: bool | None = None
    half_day_end: bool | None = None
    time_off_type: AbsenceType | None = None
    employee: ShortEmployee | None = None
    certificate: Certificate | None = None
    created_by: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @field_validator("start_date", "end_date", mode="before")
    @classmethod
    def _datetime_to_date(cls, v):
        if v and isinstance(v, str):
            return v[:10]
        return v

    @field_validator("employee", mode="before")
    @classmethod
    def short_employee_conversion(cls, v):
        if isinstance(v, BaseEmployee):
            return v.to_short_employee()
        return v

    def create(self) -> "Absence":
        return self._get_client().create_absence(self)

    def delete(self):
        return self._get_client().delete_absence(self)

    def get_employee(self) -> "Employee":
        return self.employee.resolve()

    def to_api_dict(self) -> dict:
        data = {}
        for field in self._api_fields_required:
            self._add_api_dict_field(self, data, field, required=True)
        for field in self._api_fields_optional:
            self._add_api_dict_field(self, data, field, required=False)
        return data


class Project(PersonioResource):
    _api_type_name = "Project"

    id: int | None = None
    name: str | None = None
    active: bool | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def create(self) -> "Project":
        return self._get_client().create_project(self)

    def delete(self):
        return self._get_client().delete_project(self)

    def update(self) -> "Project":
        return self._get_client().update_project(self)

    def to_body_params(self) -> dict:
        return {"name": self.name, "active": self.active}

    @classmethod
    def _get_kwargs_from_api_dict(cls, d: dict) -> dict:
        # unlike most resources, the project id lives at the top level and must be preserved
        id_ = d.get("id")
        if "type" in d and "attributes" in d:
            cls._check_api_type(d)
            d = d["attributes"]
            d["id"] = id_
        if not cls._flat_dict:
            d = {k: v["value"] for k, v in d.items()}
        return d


class Attendance(PersonioResource):
    _api_type_name = "AttendancePeriod"

    id: int | None = None
    employee: int | None = None
    day: date | None = Field(None, alias="date")
    start_time: time | None = None
    end_time: time | None = None
    break_duration: int | None = Field(None, alias="break")
    comment: str | None = None

    def create(self):
        return self._get_client().create_attendances([self])

    def update(self):
        return self._get_client().update_attendance(self)

    def delete(self):
        return self._get_client().delete_attendance(self)

    def get_employee(self) -> "Employee":
        return self._get_client().get_employee(self.employee)

    def to_body_params(self, patch_existing_attendance=False) -> dict:
        """
        Return the Attendance object in the representation expected by the Personio API

        For an attendance record to be created all values are required.
        For patch operations only the attendance id is required, but it is not
        included into the body params.

        :param patch_existing_attendance: Get patch body. If False a create body is returned.
        """
        if patch_existing_attendance:
            if self.id is None:
                raise ValueError("An attendance id is required")
            body_dict = {}
            if self.day is not None:
                body_dict["date"] = self.day.strftime("%Y-%m-%d")
            if self.start_time is not None:
                body_dict["start_time"] = str(self.start_time)
            if self.end_time is not None:
                body_dict["end_time"] = str(self.end_time)
            if self.break_duration is not None:
                body_dict["break"] = self.break_duration
            if self.comment is not None:
                body_dict["comment"] = self.comment
            return body_dict
        else:
            return {
                "employee": self.employee,
                "date": self.day.strftime("%Y-%m-%d"),
                "start_time": str(self.start_time),
                "end_time": str(self.end_time),
                "break": self.break_duration or 0,
                "comment": self.comment or "",
            }

    @classmethod
    def _get_kwargs_from_api_dict(cls, d: dict) -> dict:
        # unlike most resources, the attendance id lives at the top level and must be preserved
        id_ = d.get("id")
        if "type" in d and "attributes" in d:
            cls._check_api_type(d)
            d = d["attributes"]
            d["id"] = id_
        if not cls._flat_dict:
            d = {k: v["value"] for k, v in d.items()}
        return d


class AbsenceBalance(PersonioResource):
    id: int | None = None
    name: str | None = None
    balance: float | None = None


def _parse_tags(v: str | list[str] | None) -> list[str] | None:
    """
    The 'tags' type is a multiple choice field, where the user can select 0 or more fields from
    a list of values. The personio API provides this list of values as a single string with
    comma separated values. When we serialize this type, we store it as list of strings.
    Therefore we need this parsing function so that we can handle both the comma separated string
    and the list of string.

    :param v: value of the tags field (string, list of strings, or None)
    :return: the parsed tags value, as list of strings, or None
    """
    if isinstance(v, str):
        if v.startswith("[") and v.endswith("]"):
            # this is a json list, stored as string. Personio does that sometimes, apparently
            return json.loads(v)
        else:
            # otherwise Personio usually provides a comma-separated list of strings
            return [tag.strip() for tag in v.split(",")]
    elif isinstance(v, list):
        return v
    elif not v:
        return None
    else:
        raise ValueError(f"unexpected input type {type(v)}")


PersonioTags = Annotated[list[str], BeforeValidator(_parse_tags)]
"""The Personio 'tags' type, which is basically a multiple choice field"""


class CustomAttribute(BaseModel):
    _type_mapping: ClassVar[dict[str, Any]] = {
        # standard text field, no line breaks
        "standard": str,
        # a date field. the API provides date and time information as ISO 8601 string
        "date": datetime,
        # an integer field
        "integer": int,
        # a float field (limited precision)
        "decimal": float,
        # "list" refers to an option field, where only one item can be selected.
        # only the selected item is provided by the API, therefore this is a string.
        "list": str,
        # a hyperlink
        "link": str,
        # "tags" refers to a multiple choice field, where you can select 0 or more items from a
        # predefined list of items. The list of all selected items is provided by the API.
        "tags": PersonioTags,
        # a multiline text field, can contain line breaks
        "multiline": str,
    }

    key: str | None = None
    label: str | None = None
    type: str | None = None
    universal_id: str | None = None

    @property
    def py_type(self) -> Any:
        type_str = str(self.type).lower()
        if type_str in self._type_mapping:
            return self._type_mapping[type_str]
        else:
            raise PersonioError(f"unexpected custom attribute type {self.type}")


class BaseEmployee(PersonioResource):
    _api_type_name = "Employee"
    _flat_dict = False
    _custom_attribute_keys: ClassVar[list[str]] = []
    """the names of all known custom attributes (usually starting with 'dynamic_')"""
    _custom_attribute_aliases: ClassVar[dict[str, str]] = {}
    """mapping from all custom attribute names (starting with 'dynamic_') to their aliases"""
    _property_setters: ClassVar[dict[str, property]] = {}
    """a cache of setter functions for all custom attributes"""
    _picture: dict[int | None, bytes] = PrivateAttr(default_factory=dict)
    """the Employee's picture is cached in this attribute on first request
    (mapping from image width to image bytes)"""
    _api_fields_required: ClassVar[list] = ["email", "first_name", "last_name"]
    """these are the standard fields that are required by the Employee create/update API"""
    _api_fields_optional: ClassVar[list] = [
        "gender",
        "position",
        "subcompany",
        ("department.name", "department"),
        ("office.name", "office"),
        "hire_date",
        "weekly_working_hours",
    ]
    """these are the standard fields that are supported by the Employee create/update API,
    but optional. Any other standard fields besides those defined in `_api_fields_required` are
    not supported and will by ignored by the Personio API"""

    id: int | None = None
    """unique identifier by which Personio refers to this employee"""
    first_name: str | None = None
    """first name / given name of the employee"""
    last_name: str | None = None
    """last name / surname / family name of the employee"""
    email: str | None = None
    """the employee's email address"""
    gender: str | None = None
    """the employee's gender"""
    status: str | None = None
    """the employee's employment status (active, inactive, ...)"""
    position: str | None = None
    """the employee's position / job title"""
    supervisor: ShortEmployee | None = None
    """the employee's current supervisor"""
    employment_type: str | None = None
    """the employee's employment type (internal, external)"""
    weekly_working_hours: str | None = None
    """the employee's weekly working hours, as contracted"""
    hire_date: date | None = None
    """the date when this employee was hired"""
    contract_end_date: date | None = None
    """when specified, this employee's contract will end at this date"""
    termination_date: date | None = None
    """date when this employee's contract has been terminated"""
    termination_type: str | None = None
    """choice from a list of reasons for termination (retirement, temporary contract, etc.)"""
    termination_reason: str | None = None
    """free-text field where details about the termination can be stored"""
    probation_period_end: date | None = None
    """date at which this employee's probation period ends"""
    created_at: datetime | None = None
    """date at which this employee profile was created in Personio"""
    last_modified_at: datetime | None = None
    """date at which this employee profile was last updated in Personio"""
    subcompany: str | None = None
    """name of the subcompany this employee is working for"""
    office: Office | None = None
    """the office this employee is typically working from"""
    department: Department | None = None
    """the department this employee belongs to"""
    cost_centers: list[CostCenter] | None = None
    """list of cost centers this employee is assigned to"""
    holiday_calendar: HolidayCalendar | None = None
    """the holiday calender which is valid for this employee"""
    absence_entitlement: list[AbsenceEntitlement] | None = None
    """the list of absences this employee is entitled to (vacations, parental leave, etc.)"""
    work_schedule: WorkSchedule | None = None
    """the employee's work schedule (expected working hours per week day)"""
    fix_salary: float | None = None
    """the employee's fixed salary (without bonus payments)"""
    fix_salary_interval: str | None = None
    """the interval at which the fixed salary is paid (monthly, weekly, etc.)"""
    hourly_salary: float | None = None
    """the employee's hourly salary (as alternative to the fixed salary)"""
    vacation_day_balance: float | None = None
    """the employee's current vacation day balance (can be negative)"""
    last_working_day: date | None = None
    """the employee's last working day, in case the contract was terminated"""
    profile_picture: str | None = None
    """URL to this employee's profile picture"""
    team: Team | None = None
    """the team this employee is assigned to"""

    @field_validator(
        "hire_date",
        "contract_end_date",
        "termination_date",
        "probation_period_end",
        "last_working_day",
        mode="before",
    )
    @classmethod
    def _datetime_to_date(cls, v):
        if v and isinstance(v, str):
            return v[:10]
        return v

    def create(self, refresh=True) -> "Employee":
        return self._get_client().create_employee(self, refresh=refresh)

    def update(self, refresh=True) -> "Employee":
        return self._get_client().update_employee(self, refresh=refresh)

    def absence_balance(self) -> list[AbsenceBalance]:
        return self._get_client().get_absence_balance(self)

    def picture(self, width: int = None) -> bytes | None:
        """
        Get the profile picture of this employee as image file (usually png or jpg).
        The data will be cached locally, so subsequent requests of a profile picture
        of the same size will be fast.

        :param width: optionally scale the profile picture to this width.
               Defaults to the original width of the profile picture.
        :return: the profile picture as png or jpg file (bytes)
        """
        if width not in self._picture:
            self._picture[width] = self._get_client().get_employee_picture(self, width=width)
        return self._picture[width]

    def to_api_dict(self) -> dict:
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
            data["custom_attributes"] = custom_attributes
        return {"employee": data}

    def __setattr__(self, name, value):
        """
        Workaround that allows the use of property setters (used for custom attribute aliases).

        We override pydantic's ``BaseModel.__setattr__`` and catch the error that occurs when we
        try to set an attribute that is not one of pydantic's known fields. We then check if the
        field name is actually a property that has a setter function and make use of it. Otherwise
        we re-raise the original error. The property setters are discovered with python's
        ``inspect`` module and cached on the class.

        :param name: name of the attribute
        :param value: the value to set
        """
        try:
            super().__setattr__(name, value)
        except (ValueError, AttributeError) as e:
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
            cls, predicate=lambda x: isinstance(x, property) and x.fset is not None
        )
        cls._property_setters = {name: prop for name, prop in setters}

    @property
    def _custom_fields(self) -> dict[str, Any]:
        # return dynamic fields (keys and values) as ReadOnlyDict
        # to assign new values, use employee.dynamic_X directly
        return ReadOnlyDict((k, getattr(self, k)) for k in self._custom_attribute_keys)

    @classmethod
    def _get_subclass_for_client(
        cls, client: "Personio", aliases: dict[str, str] = None
    ) -> type["BaseEmployee"]:
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
        https://docs.pydantic.dev/latest/concepts/models/#dynamic-model-creation

        Note: this returns a fresh subclass; it does not mutate any global state. Each Personio
        client keeps its own subclass, so multiple clients with different custom attributes can
        be used at the same time.

        :param client: the Personio client instance to generate a dynamic model for
        :param aliases: custom aliases provided by the user (optional)
        :return: the class definition of the new Employee subclass
        """
        # get custom attributes, generate subclass
        attributes = client.get_custom_attributes()
        dynamic_attributes = [a for a in attributes if a.key.startswith("dynamic_")]
        # Optional[...] (rather than `py_type | None`) is used deliberately: py_type may be an
        # Annotated alias (e.g. the tags type), and Optional handles that robustly.
        pydantic_fields = {a.key: (Optional[a.py_type], None) for a in dynamic_attributes}
        employee_cls = create_model(
            "Employee",
            __base__=BaseEmployee,
            __module__="personio_py.models",
            **pydantic_fields,
        )
        # set class variables on the new subclass (not on BaseEmployee, to keep clients isolated)
        aliases = aliases or {}
        employee_cls._custom_attribute_keys = [a.key for a in dynamic_attributes]
        employee_cls._custom_attribute_aliases = {
            a.key: aliases.get(a.key) or cls._get_attribute_name_for(a.label)
            for a in dynamic_attributes
        }
        # add metadata to pydantic fields
        attributes_dict = {a.key: a for a in attributes}
        for key, field in employee_cls.model_fields.items():
            if key in attributes_dict:
                field.title = attributes_dict[key].label
        # add aliases as properties
        for attribute in dynamic_attributes:
            key = attribute.key
            alias = employee_cls._custom_attribute_aliases[key]
            if not alias:
                continue
            if hasattr(employee_cls, alias):
                logger.warning(
                    f"cannot add alias '{alias}' for '{key}' to the Employee class, because "
                    f"there is already an attribute with this name."
                )
            else:
                cls.__set_alias_property(employee_cls, key, alias, attribute.label)
        return employee_cls

    @staticmethod
    def __set_alias_property(cls: type, attr: str, alias: str, label: str):
        """Add a new property to a class which serves as an alias to an existing attribute.

        :param cls: add the new property to this class
        :param attr: the original attribute to reference
        :param alias: the alias for the original attribute
        :param label: a properly formatted name/label/title for the alias (used in the docstring)
        """
        prop = property(
            fget=lambda self: getattr(self, attr),
            fset=lambda self, value: setattr(self, attr, value),
            doc=f"{alias} ({label}) is an alias for {attr}",
        )
        setattr(cls, alias, prop)

    @classmethod
    def _get_attribute_name_for(cls, name: str) -> str | None:
        if not name or not name.strip():
            return None
        # we want a lowercase attribute name
        result = name.lower()
        # special handling of German non-ascii letters, because Personio is a German company ;)
        table = str.maketrans({"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss"})
        result = result.translate(table)
        # convert unicode chars to their closest ascii equivalents, ignoring the rest
        result = unicodedata.normalize("NFKD", result).encode("ascii", "ignore").decode()
        # keep only letters, digits and whitespace
        result = "".join(c for c in result if c.isalnum() or c.isspace())
        # remove consecutive whitespace and join tokens with underscores
        result = "_".join(result.split())
        # remove leading digits, since they are not allowed in python attribute names
        result = result.lstrip("0123456789_")
        return result

    def to_short_employee(self) -> ShortEmployee:
        return ShortEmployee(
            id=self.id,
            first_name=self.first_name,
            last_name=self.last_name,
            email=self.email,
        )


# Employee is an alias for BaseEmployee until a client generates a subclass that contains the
# custom attributes of the connected Personio account. Unlike the previous implementation, this
# alias is NOT reassigned at runtime and sys.modules is NOT patched: each Personio client keeps
# its own Employee subclass (client.Employee), which keeps multiple clients fully independent.
Employee = BaseEmployee
