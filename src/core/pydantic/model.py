from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Optional, Union

import orjson
from pydantic import BaseModel as _BaseModel
from pydantic import StrictFloat, root_validator
from pydantic.fields import SHAPE_SINGLETON, ModelField
from pydantic_factories import ModelFactory as _ModelFactory

from .field import ISO8601Datetime, UTCDatetime

if TYPE_CHECKING:
    from pydantic.typing import AbstractSetIntStr, MappingIntStrAny, TupleGenerator


class BaseModel(_BaseModel):
    @staticmethod
    def is_optional(field: ModelField):
        if field.allow_none and (field.shape != SHAPE_SINGLETON or not field.sub_fields):
            return True

        return False

    @classmethod
    def get_properties(cls):
        return [
            prop
            for prop in dir(cls)
            if isinstance(getattr(cls, prop), property) and prop not in ('__values__', 'fields')
        ]

    @root_validator(pre=True)
    def check_nullable(cls, values):
        for k, field in cls.__fields__.items():
            if k not in values:
                continue

            nullable = field.field_info.extra.get('nullable')
            if nullable is False and values[k] is None:
                raise ValueError(f'{k} is not allowed to be null')

        return values

    @root_validator
    def transfer_datetime_format_to_utc(cls, values: dict):
        for name, field in cls.__fields__.items():
            if field.type_ is datetime and values.get(name) and values.get(name).tzinfo:
                values[name] = (values[name].astimezone(timezone.utc)).replace(tzinfo=None)

        return values

    def _iter(
        self,
        to_dict: bool = False,
        by_alias: bool = False,
        include: Optional[Union['AbstractSetIntStr', 'MappingIntStrAny']] = None,
        exclude: Optional[Union['AbstractSetIntStr', 'MappingIntStrAny']] = None,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
    ) -> 'TupleGenerator':
        yield from super()._iter(to_dict, by_alias, include, exclude, exclude_unset, exclude_defaults, exclude_none)

        props = self.get_properties()
        if include:
            props = (prop for prop in props if prop in include)
        if exclude:
            props = (prop for prop in props if prop not in exclude)

        if props:
            for prop in props:
                yield prop, getattr(self, prop)

    def jsonable_dict(
        self,
        by_alias: bool = False,
        skip_defaults: Optional[bool] = None,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        **kwargs,
    ) -> dict:
        json_ = self.json(
            by_alias=by_alias,
            skip_defaults=skip_defaults,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            **kwargs,
        )

        return orjson.loads(json_)  # pylint:disable=no-member


class ModelFactory(_ModelFactory[Any]):
    @classmethod
    def get_mock_value(cls, field_type: Any) -> Any:
        """
        Because of Symbolic link and relative import, if field_type is a custom class, it will check for errors

        error:
            from .._pydantic import ISO8601Datetime
            assert field_type is ISO8601Datetime
            #     field_type: <class 'models._pydantic.ISO8601Datetime'>
            #     ISO8601Datetime: <class 'sdk.models._pydantic.ISO8601Datetime'>

        solution1 - absolute import:
            from models._pydantic import ISO8601Datetime
            assert field_type is ISO8601Datetime
            #     field_type: <class 'models._pydantic.ISO8601Datetime'>
            #     ISO8601Datetime: <class 'models._pydantic.ISO8601Datetime'>

        solution2 - __name__:
            assert field_type.__name__ == ISO8601Datetime.__name__
            #     field_type: <class 'models._pydantic.ISO8601Datetime'>
            #     ISO8601Datetime: <class 'sdk.models._pydantic.ISO8601Datetime'>
        """

        faker = cls.get_faker()
        if field_type is UTCDatetime:
            return faker.date_time_between()
        elif field_type is ISO8601Datetime:
            return datetime.utcnow().isoformat() + 'Z'
        elif field_type in (float, StrictFloat):
            return faker.pyfloat(left_digits=6, right_digits=2, positive=True)
        elif field_type is Decimal:
            return faker.pydecimal(left_digits=6, right_digits=2, positive=True)
        elif field_type is dict:
            return faker.pydict(value_types=[int, str])

        return super().get_mock_value(field_type)
