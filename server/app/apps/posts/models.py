import os
import shutil
from django.conf import settings
from django.db import models
from django.forms import ImageField
from app.apps.core.models import Author, Category, Tag

# Create your models here.


class MODERATE_STATUSES(models.TextChoices):
    APPROVED = 'APPROVED'
    DECLINED = 'DECLINED'
    PENDING = 'PENDING'
    NEED_CHANGES = 'NEED_CHANGES'


def get_preview_upload_path(instance, filename: str) -> str:
    _, ext = filename.split('.')
    return os.path.join(f"posts/post_{instance.id}", f'preview.{ext}')


def get_post_photos_upload_path(instance, filename: str) -> str:
    return os.path.join(f"posts/post_{instance.post.id}/photos", filename)


class PostImage(models.Model):
    image = models.ImageField(upload_to=get_post_photos_upload_path)
    post = models.ForeignKey(
        'Post', related_name='images', on_delete=models.CASCADE, blank=True, null=True)

    def delete(self, *args, **kwargs):
        if os.path.exists(os.path.abspath(f'{settings.MEDIA_ROOT}/{self.image.name}')):
            os.remove(os.path.abspath(f'{settings.MEDIA_ROOT}/{self.image.name}'))
        else:
            print("The file does not exist")
        
        super().delete(*args, **kwargs)


class PostDraft(models.Model):
    post = models.OneToOneField(
        'Post', related_name="+", on_delete=models.CASCADE)
    moderate_status = models.TextField(blank=True, choices=MODERATE_STATUSES.choices)
    message = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.post.__str__()

class Post(models.Model):
    title = models.CharField(max_length=150, default='')
    short_description = models.TextField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE, blank=True)
    content = models.TextField(blank=True)
    categories = models.ManyToManyField(Category)
    tags = models.ManyToManyField(Tag)
    created_date = models.DateField(auto_now_add=True)
    preview = models.ImageField(
        upload_to=get_preview_upload_path, null=True, blank=True)
    draft = models.ForeignKey(
        PostDraft, related_name="+", on_delete=models.CASCADE, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.id is None:
            saved_preview: ImageField = self.preview #type: ignore
            self.preview = None
            super().save(*args, **kwargs)
            self.preview = saved_preview
            draft = PostDraft(post=self, moderate_status=MODERATE_STATUSES.PENDING)
            draft.save()
            self.draft = draft
            super().save(update_fields=['draft', 'preview'])
        else:
            super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if os.path.exists(os.path.abspath(f'{settings.MEDIA_ROOT}/posts/post_{self.id}')):
            shutil.rmtree(os.path.abspath(f'{settings.MEDIA_ROOT}/posts/post_{self.id}'))
        
        super().delete(*args, **kwargs)



    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_date']
