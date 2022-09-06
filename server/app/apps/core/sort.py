import json
from rest_framework.request import Request

from app.fp import curry

class Sort:
    def __init__(self) -> None:
        self._fields: list[str] = []

    @curry(3)
    def sort_by_fields(self, queryset, request: Request):
        sort = request.query_params.get('sort')
        if sort is None:
            return queryset
        
        sort_obj = self._parse_sort_obj(sort)

        params = [self._parse_param(name, value) if self._is_valid(name, value) else None for name, value in sort_obj.items()]

        filtered_params: list[str] = list(filter(lambda x: x is not None, params))
        if len(params) == 0:
            return queryset
    
        return queryset.order_by(*filtered_params)

    '''Define which query fields must be support in sorting'''
    @property
    def fields(self):
        return self._fields

    @fields.setter
    def fields(self, fields: list[str]):
        self._fields = fields

    def _is_valid(self, name: str, value: str | list[object]) -> bool:

        if name in self._fields and (value == 'desc' or value == 'asc'):
            return True

        return False

    def _parse_sort_obj(self, sort: str):
        try:
            return json.loads(sort)
        except:
            return {}

    def _parse_param(self, name: str, value: str | list[object]):
        return name if value == 'asc' else f'-{name}'
            
