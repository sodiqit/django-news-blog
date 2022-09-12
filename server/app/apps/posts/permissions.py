from rest_framework.permissions import SAFE_METHODS, BasePermission

class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return obj.author.user == request.user

class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.post.author.user == request.user