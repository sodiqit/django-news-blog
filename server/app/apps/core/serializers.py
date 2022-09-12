from rest_framework import serializers

from .models import Category, Tag


class CategorySerializer(serializers.ModelSerializer):
    category_id = serializers.CharField(max_length=100)
    title = serializers.CharField(max_length=200)

    class Meta:
        model = Category
        fields = ('id', 'category_id', 'title')


class TagSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=150, required=False)

    class Meta:
        model = Tag
        fields = ('id', 'title')
