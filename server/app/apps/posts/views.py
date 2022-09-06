from dataclasses import dataclass
from rest_framework import viewsets, serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS, BasePermission

from app.apps.core.converter import CategoryConverter
from app.apps.core.models import Category
from app.injector import inject
from app.fp import pipe
from app.apps.core.filter import QueryFilter
from django.db.models import QuerySet

from app.apps.core.sort import Sort

from .serializers import PostSerializer
from .models import MODERATE_STATUSES, Post

# Create your views here.


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return obj.author.user == request.user


@dataclass
class PostViewContainer:
    query_filter: QueryFilter
    sort: Sort
    category_converter: CategoryConverter


class PostView(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    queryset = Post.objects.filter(
        draft__moderate_status=MODERATE_STATUSES.APPROVED)
    serializer_class = PostSerializer

    @inject('PostView', QueryFilter, Sort, CategoryConverter)
    def __init__(self, **kwargs) -> None:
        self.container: PostViewContainer = kwargs.pop('container')
        self.query_filter = self.container.query_filter
        self.query_filter.fields = [
            'id', 'title', 'author', 'categories', 'tags', 'created_date']
        self.sort = self.container.sort
        self.sort.fields = ['id', 'categories', 'images']
        super().__init__(**kwargs)

    def list(self, request):
        queryset: QuerySet = pipe(self.get_queryset(), self.filter_queryset,
                                  self.query_filter.filter_by_fields(request=request), self.sort.sort_by_fields(request=request))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(self._add_categories_tree(serializer))

        result = pipe(self.get_serializer(queryset, many=True),
                      self._add_categories_tree)
        return Response(result)

    def _add_categories_tree(self, serializer: serializers.BaseSerializer):
        for post in serializer.data:
            categories = [Category.objects.get(
                id=c['id']) for c in post['categories']]
            category_tree = self.container.category_converter.convert_categories_to_tree(
                categories)
            post['categories'] = category_tree

        return serializer.data
