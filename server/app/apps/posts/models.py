from django.db import models
from app.apps.core.models import Category, Tag, User

# Create your models here.


class Post(models.Model):
    short_description = models.TextField()
    created_date = models.DateField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    categories = models.ManyToManyField(Category)
    tags = models.ManyToManyField(Tag)
