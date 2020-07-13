"""
mappings from Personio API fields to Python data types and vice versa are defined in this module
"""
import logging
import re
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, NamedTuple, Optional, TYPE_CHECKING, Type, TypeVar, Union

if TYPE_CHECKING:
    from personio_py import Personio
    from personio_py.models import PersonioResourceType

logger = logging.getLogger('personio_py')

T = TypeVar('T')


class FieldMapping:
    """
    A generic mapping from a Personio API field to a Python object.
    The default implementation works great for strings, but for more complex types,
    please refer to the subclasses of ``FieldMapping``.

    :param api_field: name of the field in the Personio API
    :param class_field: name of the attribute in the target Python object
    :param field_type: data type of the field
    """

    def __init__(self, api_field: str, class_field: str, field_type: Type[T]):
        self.api_field = api_field
        self.class_field = class_field
        self.field_type = field_type

    def serialize(self, value: T) -> Union[str, Dict]:
        """
        Serialize the parsed value to the format that the Personio API expects.

        :param value: the value to serialize
        :return: the serialized value
        """
        return str(value)

    def deserialize(self, value: Union[str, Dict], **kwargs) -> T:
        """
        Deserialize the Personio API value to a more useful Python data type.

        :param value: the value as provided by the Personio API
        :param kwargs: additional parameters (to be used by subclasses)
        :return: the deserialized value
        """
        return self.field_type(value)

    def __str__(self):
        return f"{self.__class__.__name__} {self.__dict__}"


class NumericFieldMapping(FieldMapping):
    # don't touch numeric types, unless they are strings...

    def __init__(self, api_field: str, class_field: str, field_type=float):
        super().__init__(api_field, class_field, field_type=field_type)

    def serialize(self, value: Union[int, float, str]) -> Union[int, float, str]:
        return value

    def deserialize(self, value: Union[int, float, str], **kwargs) -> Union[int, float, str]:
        return self.field_type(value) if isinstance(value, str) else value


class DateTimeFieldMapping(FieldMapping):

    def __init__(self, api_field: str, class_field: str):
        super().__init__(api_field, class_field, field_type=datetime)

    def serialize(self, value: datetime) -> str:
        return value.isoformat()

    def deserialize(self, value: str, **kwargs) -> datetime:
        return datetime.fromisoformat(value)


class DateFieldMapping(FieldMapping):

    def __init__(self, api_field: str, class_field: str):
        super().__init__(api_field, class_field, field_type=date)

    def serialize(self, value: datetime) -> str:
        return value.isoformat()

    def deserialize(self, value: str, **kwargs) -> date:
        return date.fromisoformat(value[:10])


class DurationFieldMapping(FieldMapping):

    pattern = re.compile(r"\d\d?:\d\d")

    def __init__(self, api_field: str, class_field: str):
        super().__init__(api_field, class_field, field_type=timedelta)

    def serialize(self, value: timedelta) -> str:
        mm, ss = divmod(value.total_seconds(), 60)
        hh, mm = divmod(mm, 60)
        return f"{int(hh):02d}:{int(mm):02d}"

    def deserialize(self, value: str, **kwargs) -> timedelta:
        return self.str_to_timedelta(value)

    @classmethod
    def str_to_timedelta(cls, s: str) -> timedelta:
        if not isinstance(s, str):
            raise TypeError(f"expected a string, but got {type(s)}")
        trimmed = s.strip()
        if cls.pattern.fullmatch(trimmed):
            hh, mm = trimmed.split(':')
            return timedelta(hours=int(hh), minutes=int(mm))
        else:
            raise ValueError(f"the string '{s}' does not represent a valid duration. "
                             f"Expected format is 'hh:mm', e.g. '06:30'.")


class MultiTagFieldMapping(FieldMapping):

    def __init__(self, api_field: str, class_field: str):
        super().__init__(api_field, class_field, field_type=list)

    def serialize(self, values: List[str]) -> str:
        for value in values:
            if ',' in value:
                raise ValueError(
                    f"Due to a restrictions at Personio, no commas are allowed in "
                    f"multi selection fields, please adjust '{value}'")
        return ','.join(values)

    def deserialize(self, value: str, **kwargs) -> List[str]:
        return [s.strip() for s in value.split(',')] if value else []


class ObjectFieldMapping(FieldMapping):

    def __init__(self, api_field: str, class_field: str, field_type: Type['PersonioResourceType']):
        super().__init__(api_field, class_field, field_type)

    def serialize(self, value: 'PersonioResourceType') -> Dict:
        if self.field_type._flat_dict:
            return value.to_dict()
        else:
            return {'type': self.field_type._api_type_name, 'attributes': value.to_dict()}

    def deserialize(self, value: Dict, client: 'Personio' = None) \
            -> Optional['PersonioResourceType']:
        if value and isinstance(value, dict):
            if not self.field_type._flat_dict:
                value = value['attributes']
            return self.field_type.from_dict(value, client=client)
        else:
            return None


class ListFieldMapping(FieldMapping):
    # wraps another field mapping, to handle list types
    # e.g. ``ListFieldMapping(ObjectFieldMapping('cost_centers', 'cost_centers', CostCenter))``

    def __init__(self, item_mapping: FieldMapping):
        super().__init__(item_mapping.api_field, item_mapping.class_field, field_type=List)
        self.item_mapping = item_mapping

    def serialize(self, values: List[Any]) -> List[Any]:
        return [self.item_mapping.serialize(item) for item in values]

    def deserialize(self, values: List[Any], client: 'Personio' = None) -> List[Any]:
        return [self.item_mapping.deserialize(item, client=client) for item in values]


FieldMappingType = TypeVar('FieldMappingType', bound=FieldMapping)


class DynamicMapping(NamedTuple):
    """
    Defines a mapping from a dynamic field to a more memorable name and its actual data type,
    so that it may be converted into a proper python type, if possible.
    """
    field_id: int
    """the id number of the dynamic field, e.g. for 'dynamic_123456', field_id=123456"""
    alias: str
    """a more memorable name than the field_id, will be used as dictionary key"""
    data_type: Type[T]
    """the data type of the field, for automatic conversion (e.g. str to datetime)"""

    def get_field_mapping(self) -> FieldMappingType:
        api_field = f'dynamic_{self.field_id}'
        if self.data_type == str:
            return FieldMapping(api_field, self.alias, str)
        elif self.data_type in (int, float, Decimal):
            return NumericFieldMapping(api_field, self.alias, self.data_type)
        elif self.data_type == date:
            return DateFieldMapping(api_field, self.alias)
        elif self.data_type == datetime:
            return DateTimeFieldMapping(api_field, self.alias)
        elif self.data_type == timedelta:
            return DurationFieldMapping(api_field, self.alias)
        elif self.data_type in (list, List):
            return MultiTagFieldMapping(api_field, self.alias)
        else:
            logger.warning(f"unexpected type {self.data_type} for dynamic field {self.field_id}")
            return FieldMapping(api_field, self.alias, self.data_type)
