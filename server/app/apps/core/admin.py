from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Category, Tag, User

# Register your models here.


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'category_id', 'title')


admin.site.register(User, UserAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag)
