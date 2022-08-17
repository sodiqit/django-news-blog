from datetime import date
from django.db import models
from tomlkit import datetime
from app.apps.core.models import Category, Tag, User

# Create your models here.


class Post(models.Model):
    title = models.CharField(max_length=150, default='')
    short_description = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    categories = models.ManyToManyField(Category)
    tags = models.ManyToManyField(Tag)
    created_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_date']
