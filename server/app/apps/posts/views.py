from dataclasses import dataclass
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from app.apps.core.models import Author
from app.injector import inject
from app.fp import pipe
from app.apps.core.filter import QueryFilter

from app.apps.core.sort import Sort
from .permissions import IsOwnerOrReadOnly, IsOwner

from .serializers import CreateCommentSerializer, CreatePostSerializer, PostCommentSerializer, PostDraftSerializer, PostSerializer, UpdatePostSerializer
from .models import MODERATE_STATUSES, Post, PostComment, PostDraft

# Create your views here.


@dataclass
class PostViewContainer:
    query_filter: QueryFilter
    sort: Sort


class PostDraftView(mixins.DestroyModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.ListModelMixin,
                    viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated, IsOwner)
    queryset = PostDraft.objects.all()
    serializer_class = PostDraftSerializer

    @inject('PostView', QueryFilter)
    def __init__(self, **kwargs) -> None:
        self.container: PostViewContainer = kwargs.pop('container')
        self.query_filter = self.container.query_filter
        self.query_filter.fields = ['moderate_status']
        super().__init__(**kwargs)

    def get_queryset(self):
        queryset = PostDraft.objects.filter(
            post__author__user=self.request.user)  # type:ignore
        return self.query_filter.filter_by_fields(queryset, self.request)

    def update(self, request, *args, **kwargs):
        instance: PostDraft = self.get_object()

        if instance.moderate_status == MODERATE_STATUSES.DECLINED:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'detail': 'post is declined'})

        post_data: dict | None = request.data.pop('post', None)

        post_serializer = UpdatePostSerializer(instance.post, data=post_data)
        post_serializer.is_valid(raise_exception=True)
        post_serializer.save()

        serializer = self.get_serializer(instance)

        return Response(serializer.data)


class PostView(mixins.DestroyModelMixin,
               mixins.ListModelMixin,
               mixins.CreateModelMixin,
               mixins.RetrieveModelMixin,
               viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    queryset = Post.objects.filter(
        draft__moderate_status=MODERATE_STATUSES.APPROVED)
    serializer_class = PostSerializer

    @inject('PostView', QueryFilter, Sort)
    def __init__(self, **kwargs) -> None:
        self.container: PostViewContainer = kwargs.pop('container')
        self.query_filter = self.container.query_filter
        self.query_filter.fields = [
            'id', 'title', 'author', 'categories', 'tags', 'created_date']
        self.sort = self.container.sort
        self.sort.fields = ['id', 'images', 'created_date']
        super().__init__(**kwargs)

    def get_queryset(self):
        return pipe(super().get_queryset(), self.query_filter.filter_by_fields(request=self.request), self.sort.sort_by_fields(request=self.request))

    def create(self, request):
        if not Author.objects.filter(user=request.user).exists():
            return Response({'detail': 'author not exist'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = CreatePostSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save(user=request.user)

        data = PostSerializer(instance).data

        headers = self.get_success_headers(data)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

    def destroy(self, request, pk):
        instance = Post.objects.get(pk=pk)
        self.check_object_permissions(self.request, instance)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class PostCommentView(mixins.DestroyModelMixin,
                      mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated, )
    serializer_class = PostCommentSerializer
    lookup_url_kwarg = 'post_id'

    @inject('PostView', QueryFilter, Sort)
    def __init__(self, **kwargs) -> None:
        self.container: PostViewContainer = kwargs.pop('container')
        self.query_filter = self.container.query_filter
        self.query_filter.fields = ['id', 'text', 'user', 'created_at']
        self.sort = self.container.sort
        self.sort.fields = ['id', 'text', 'created_at']
        super().__init__(**kwargs)

    def get_queryset(self):
        queryset = PostComment.objects.filter(
            post__draft__moderate_status=MODERATE_STATUSES.APPROVED, post__id=self.kwargs.get(self.lookup_url_kwarg))

        return pipe(queryset, self.query_filter.filter_by_fields(
            request=self.request), self.sort.sort_by_fields(request=self.request))

    def create(self, request, post_id):
        if len(self.get_queryset()) == 0:
            return Response({'detail': 'post not found'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = CreateCommentSerializer(data=request.data, context={'request': request, 'post_id': post_id})
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        data = PostCommentSerializer(instance).data

        headers = self.get_success_headers(data)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)
