import logging
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, NamedTuple, TYPE_CHECKING, Type, TypeVar, Union

if TYPE_CHECKING:
    from personio_py.models import PersonioResourceType

logger = logging.getLogger('personio_py')

T = TypeVar('T')


class FieldMapping:

    def __init__(self, api_field: str, class_field: str, field_type: Type[T]):
        self.api_field = api_field
        self.class_field = class_field
        self.field_type = field_type

    def serialize(self, value: T) -> Union[str, Dict]:
        return str(value)

    def deserialize(self, value: Union[str, Dict]) -> T:
        return self.field_type(value)

    def __str__(self):
        return f"{self.__class__.__name__} {self.__dict__}"


class NumericFieldMapping(FieldMapping):
    # don't touch numeric types, unless they are strings...

    def __init__(self, api_field: str, class_field: str, field_type=float):
        super().__init__(api_field, class_field, field_type=field_type)

    def serialize(self, value: Union[int, float, str]) -> Union[int, float, str]:
        return value

    def deserialize(self, value: Union[int, float, str]) -> Union[int, float, str]:
        return self.field_type(value) if isinstance(value, str) else value


class DateFieldMapping(FieldMapping):

    def __init__(self, api_field: str, class_field: str):
        super().__init__(api_field, class_field, field_type=datetime)

    def serialize(self, value: datetime) -> str:
        return value.isoformat()[:10]

    def deserialize(self, value: str) -> datetime:
        return datetime.fromisoformat(value)


class ObjectFieldMapping(FieldMapping):

    def __init__(self, api_field: str, class_field: str, field_type: Type['PersonioResourceType']):
        super().__init__(api_field, class_field, field_type)

    def serialize(self, value: 'PersonioResourceType') -> Dict:
        return value.to_dict()

    def deserialize(self, value: Dict) -> 'PersonioResourceType':
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
        # TODO find out which types we need to handle here
        api_field = f'dynamic_{self.field_id}'
        if self.data_type == str:
            return FieldMapping(api_field, self.alias, str)
        elif self.data_type in (int, float, Decimal):
            return NumericFieldMapping(api_field, self.alias, self.data_type)
        elif self.data_type == datetime:
            return DateFieldMapping(api_field, self.alias)
        else:
            logger.warning(f"unexpected type {self.data_type} for dynamic field {self.field_id}")
            return FieldMapping(api_field, self.alias, self.data_type)
