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
        extracted_keys = self._omit_fields_by_all_filtering(params)
        return self._filter_by_all_key(queryset.filter(**params), extracted_keys)

    '''Define which query fields must be support in filtering'''
    @property
    def fields(self):
        return self._fields

    @fields.setter
    def fields(self, fields: list[str]):
        self._fields = fields

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

    def _omit_fields_by_all_filtering(self, params):
        result = {}
        cloned_params = params.copy()
        for name, value in cloned_params.items():
            field_name, *args = name.split('__')
            if 'all' in args:
                result[field_name] = value
                params.pop(name)

        return result

    def _filter_by_all_key(self, queryset, params: dict):
        res = queryset
        for field_name, value in params.items():
            for i in value:
                res = res.filter(**{f'{field_name}__id': i})

        return res
            
