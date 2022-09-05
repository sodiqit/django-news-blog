from functools import reduce
import json
from typing import Literal, TypedDict
from rest_framework.request import Request

from app.fp import curry

class Field(TypedDict):
    name: str
    lookups: list[str] | Literal['__all__'] | None

class QueryFilter:
    def __init__(self) -> None:
        self._fields: list[str] = []

    @curry(3)
    def filter_by_fields(self, queryset, request: Request):
        params = [self._parse_param(name, value) if self._is_valid(name) else None for name, value in request.query_params.items()]
        params = filter(lambda x: x is not None, params) #type: ignore
        params = reduce(lambda x,y: {**x, **y}, params, {}) #type: ignore
        return queryset.filter(**params)

    '''Define which query fields must be support in filtering'''
    @property
    def fields(self):
        return self._fields

    @fields.setter
    def fields(self, fields: list[str]):
        self._fields = fields

    # def _is_valid(self, name: str) -> bool:
    #     field_name, *args = name.split('__')
    
    #     try:
    #         field = list(filter(lambda x: x['name'] == field_name, self._fields))[0]

    #         def validate_lookup(lookup: str):
    #             return lookup in args

    #         if field['lookups'] == '__all__' or field['lookups'] is None:
    #             return False

    #         return any([True if validate_lookup(lookup) else False for lookup in field['lookups']])
    #     except:
    #         return False

    def _is_valid(self, name: str) -> bool:
        field_name = name.split('__')[0]

        if field_name in self._fields:
            return True

        return False

    def _parse_param(self, name: str, value: str | list[object]):

        try:
            value = json.loads(value) #type:ignore
        except:
            pass

        return { name: value } 