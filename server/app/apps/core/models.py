import os
from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


def get_upload_path(instance, filename: str) -> str:
    return os.path.join(f"users/avatars/user_{instance.id}", filename)


class Category(models.Model):
    category_id = models.CharField(max_length=128, blank=True)
    title = models.CharField(max_length=128, db_index=True)

    def save(self, *args, **kwargs):
        depend_ids: list[int] = kwargs.pop("depend_ids", [])
        super().save(*args, **kwargs)
        ids = ".".join([str(x) for x in depend_ids])
        self.category_id = f"{ids}.{self.id}" if len(depend_ids) > 0 else f"{self.id}"
        super().save(update_fields=["category_id"])

    def __str__(self) -> str:
        return f"{self.category_id} - {self.title}"

    class Meta:
        verbose_name_plural = 'Categories'
        ordering=['category_id']


class Tag(models.Model):
    title = models.CharField(max_length=128, db_index=True)

    def __str__(self):
        return self.title


class User(AbstractUser):
    first_name = models.CharField(max_length=250, default=None)
    last_name = models.CharField(max_length=250, default=None)
    avatar = models.ImageField(upload_to=get_upload_path, null=True, blank=True)
    banned = models.BooleanField(default=False)

class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return self.user.__str__()