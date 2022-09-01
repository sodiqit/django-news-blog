from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS, BasePermission

from .serializers import PostSerializer
from .models import Post

# Create your views here.


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return obj.author == request.user


class PostView(mixins.UpdateModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    queryset = Post.objects.all()
    serializer_class = PostSerializer
