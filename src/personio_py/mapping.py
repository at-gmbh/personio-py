from datetime import datetime
from typing import Any, Dict, List, TYPE_CHECKING, Type, TypeVar, Union

if TYPE_CHECKING:
    from personio_py.models import PersonioResourceType

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
