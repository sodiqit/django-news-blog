from dataclasses import dataclass
from typing import Dict, TypedDict
from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from rest_framework.request import Request
from drf_yasg import openapi

from app.apps.core.serializers import CategorySerializer, TagSerializer
from app.apps.core.models import Author, Category, User
from app.injector import inject
from app.fp import pipe
from app.apps.core.converter import CategoryConverter
from app.utils import omit
from .exceptions import InvalidContext
from .services import PostService
from .models import MODERATE_STATUSES, Post, PostComment, PostDraft, PostImage


class ImageListField(serializers.ListField):
    child = Base64ImageField(required=False)


class IntegerListField(serializers.ListField):
    child = serializers.IntegerField()


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ('id', 'image')


@dataclass
class PostSerializerContainer:
    category_converter: CategoryConverter


@dataclass
class CreateAndUpdatePostSerializerContainer:
    post_service: PostService


class CreatePostPayload(TypedDict):
    user: User
    data: dict


class PostSerializer(serializers.ModelSerializer):
    images = PostImageSerializer(many=True)
    categories = CategorySerializer(many=True)
    tags = TagSerializer(many=True)

    @inject('PostSerializer', CategoryConverter)
    def __init__(self, *args, **kwargs) -> None:
        self.container: PostSerializerContainer = kwargs.pop('container')
        self.category_converter = self.container.category_converter
        super().__init__(*args, **kwargs)

    def to_representation(self, instance):
        return pipe(super().to_representation(instance), self._add_categories_tree)

    def _add_categories_tree(self, post: Dict):
        categories: list[Category] = [Category.objects.get(
            id=c['id']) for c in post['categories']]
        category_tree = self.category_converter.convert_categories_to_tree(
            categories)
        post['categories'] = category_tree

        return post

    class Meta:
        model = Post
        fields = ('id', 'title', 'author', 'categories', 'content',
                  'tags', 'created_date', 'preview', 'images')


class CategoriesField(serializers.JSONField):
    class Meta:
        category_schema = openapi.Schema(title='Category', type=openapi.TYPE_OBJECT, properties={
            "id": openapi.Schema(
                title="Category id",
                type=openapi.TYPE_STRING,
            ),
            "title": openapi.Schema(
                title="Category title",
                type=openapi.TYPE_STRING,
            ),
        })
        swagger_schema_fields = {
            "type": openapi.TYPE_ARRAY,
            "title": "Categories",
            "items": category_schema,
        }


class SwaggerPostSerializer(serializers.ModelSerializer):
    images = PostImageSerializer(many=True)
    categories = CategoriesField()
    tags = TagSerializer(many=True)

    class Meta:
        model = Post
        fields = ('id', 'title', 'author', 'categories', 'content',
                  'tags', 'created_date', 'preview', 'images')

class CreatePostSerializer(serializers.ModelSerializer):
    tags = IntegerListField()
    categories = IntegerListField()
    title = serializers.CharField(max_length=100)
    content = serializers.CharField()
    short_description = serializers.CharField()
    preview = Base64ImageField()
    images = ImageListField()

    @inject('CreatePostSerializer', PostService)
    def __init__(self, *args, **kwargs):
        self.container: CreateAndUpdatePostSerializerContainer = kwargs.pop(
            'container')

        super().__init__(*args, **kwargs)

    def create(self, validated_data: dict):
        user = validated_data.pop('user', None)
        omitted_validated_data = omit(
            ['tags', 'images', 'categories'], validated_data)
        instance = Post.objects.create(
            **{**omitted_validated_data, 'author': Author.objects.get(user=user)})
        self.container.post_service.fill_post_data(instance, validated_data)
        instance.preview = validated_data.get('preview')
        instance.save()

        return instance

    class Meta:
        model = Post
        fields = ('tags', 'categories', 'title', 'short_description',
                  'content', 'preview', 'images')


class UpdatePostSerializer(serializers.ModelSerializer):
    tags = IntegerListField(required=False)
    categories = IntegerListField(required=False)
    title = serializers.CharField(max_length=100, required=False)
    content = serializers.CharField(required=False)
    short_description = serializers.CharField(required=False)
    preview = Base64ImageField(required=False)
    images = ImageListField(required=False)

    @inject('UpdatePostSerializer', PostService)
    def __init__(self, *args, **kwargs):
        self.container: CreateAndUpdatePostSerializerContainer = kwargs.pop(
            'container')

        super().__init__(*args, **kwargs)

    def update(self, instance: Post, validated_data: dict):
        self.container.post_service.fill_post_data(instance, validated_data)
        instance.draft.moderate_status = MODERATE_STATUSES.PENDING  # type: ignore
        validated_data = omit(['tags', 'images', 'categories'], validated_data)

        return super().update(instance, validated_data)

    class Meta:
        model = Post
        fields = ('tags', 'categories', 'title', 'short_description',
                  'content', 'preview', 'images')


class PostDraftSerializer(serializers.ModelSerializer):
    post = PostSerializer()
    moderate_status = serializers.ChoiceField(
        choices=MODERATE_STATUSES.choices, read_only=True)

    class Meta:
        model = PostDraft
        fields = ('id', 'post', 'message', 'moderate_status')


class CommentUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email')


class CommentPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('id', 'title')


class PostCommentSerializer(serializers.ModelSerializer):
    user = CommentUserSerializer()
    post = CommentPostSerializer()

    class Meta:
        model = PostComment
        fields = ('id', 'post', 'user', 'text', 'created_at')


class CreateCommentSerializer(serializers.Serializer):
    text = serializers.CharField()

    def create(self, validated_data: dict):
        request: Request | None = self.context.get('request')
        post_id: int | None = self.context.get('post_id')

        if not request or not post_id:
            raise InvalidContext

        instance = PostComment.objects.create(
            **{**validated_data, 'user': request.user, 'post': Post.objects.get(id=post_id)})

        return instance


class SwaggerPostDraftSerializer(PostDraftSerializer):
    post = SwaggerPostSerializer()