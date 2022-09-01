from rest_framework import serializers
from .models import Post, PostDraft, PostImage

class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ('id', 'image')

class PostSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    images = PostImageSerializer(many=True, read_only=True)
    class Meta:
        model = Post
        fields = ('title', 'author', 'preview', 'images')

class PostDraftSerializer(serializers.ModelSerializer):
    post = PostSerializer()

    class Meta:
        model = PostDraft
        fields = ('id', 'post', 'moderate_status')