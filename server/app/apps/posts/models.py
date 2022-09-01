import os
from django.db import models
from app.apps.core.models import Author, Category, Tag

# Create your models here.


class MODERATE_STATUSES(models.TextChoices):
    APPROVED = 'APPROVED'
    DECLINED = 'DECLINED'
    PENDING = 'PENDING'
    NEED_CHANGES = 'NEED_CHANGES'


def get_preview_upload_path(instance, _: str) -> str:
    return os.path.join(f"posts/post_{instance.id}", 'preview.jpg')


def get_post_photos_upload_path(instance, filename: str) -> str:
    return os.path.join(f"posts/post_{instance.post.id}/photos", filename)


class PostImage(models.Model):
    image = models.ImageField(upload_to=get_post_photos_upload_path)
    post = models.ForeignKey(
        'Post', related_name='images', on_delete=models.CASCADE, blank=True, null=True)


class PostDraft(models.Model):
    post = models.OneToOneField(
        'Post', related_name="+", on_delete=models.CASCADE)
    moderate_status = models.TextField(choices=MODERATE_STATUSES.choices)


class Post(models.Model):
    title = models.CharField(max_length=150, default='')
    short_description = models.TextField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    content = models.TextField()
    categories = models.ManyToManyField(Category)
    tags = models.ManyToManyField(Tag)
    created_date = models.DateField(auto_now_add=True)
    preview = models.ImageField(
        upload_to=get_preview_upload_path, null=True, blank=True)
    draft = models.ForeignKey(
        PostDraft, related_name="+", on_delete=models.CASCADE, blank=True, null=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        draft = PostDraft(post=self, moderate_status=MODERATE_STATUSES.PENDING)
        draft.save()
        self.draft = draft
        super().save(update_fields=["draft"])

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_date']
