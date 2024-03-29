from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Author, Category, Tag, User

# Register your models here.


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'category_id', 'title')

class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')


admin.site.register(User, UserAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Author)
