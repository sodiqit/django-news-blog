from rest_framework import viewsets, serializers, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS, BasePermission

from app.apps.core.utils import convert_categories_to_tree
from app.apps.core.models import Category, User

from .serializers import PostSerializer
from .models import MODERATE_STATUSES, Post

# Create your views here.


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return obj.author.user == request.user


class PostView(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    queryset = Post.objects.filter(draft__moderate_status=MODERATE_STATUSES.APPROVED)
    serializer_class = PostSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(self._add_categories_tree(serializer))

        serializer = self.get_serializer(queryset, many=True)
        return Response(self._add_categories_tree(serializer))

    def _add_categories_tree(self, serializer: serializers.BaseSerializer):
        for post in serializer.data:
            categories = [Category.objects.get(id=c['id']) for c in post['categories']] 
            category_tree = convert_categories_to_tree(categories)
            post['categories'] = category_tree
    
        return serializer.data
