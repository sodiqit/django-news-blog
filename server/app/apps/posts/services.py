import os

from django.conf import settings
from app.apps.posts.models import Post, PostImage
from app.apps.core.models import Category, Tag

class PostService:
    def fill_post_data(self, instance: Post, validated_data: dict) -> None:
        preview = validated_data.get('preview', None)
        tags_data = validated_data.get('tags', None)
        images = validated_data.get('images', None)
        category_data = validated_data.get('categories', None)

        if preview and os.path.exists(f'{settings.MEDIA_ROOT}/{instance.preview.name}'):
            os.remove(f'{settings.MEDIA_ROOT}/{instance.preview.name}')

        if tags_data:
            tags = [Tag.objects.get(id=tag_id) for tag_id in tags_data]
            instance.tags.set(tags)
        
        if category_data:
            categories = [Category.objects.get(id=category_id) for category_id in category_data]
            instance.categories.set(categories)

        if images:
            for image in instance.images.all():
                image.delete()

            images_result: list[PostImage] = []

            for image in images:
                res = PostImage(image=image, post=instance)
                res.save()
                images_result.append(res)

            instance.images.set(images_result)

