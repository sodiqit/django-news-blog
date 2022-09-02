from rest_framework import serializers

from app.apps.core.serializers import CategorySerializer, TagSerializer
from .models import Post, PostDraft, PostImage

class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ('id', 'image')

class PostSerializer(serializers.ModelSerializer):
    images = PostImageSerializer(many=True, read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ('id', 'title', 'author', 'categories', 'content', 'tags', 'created_date', 'preview', 'images')

class PostDraftSerializer(serializers.ModelSerializer):
    post = PostSerializer()

    class Meta:
        model = PostDraft
        fields = ('id', 'post', 'moderate_status')