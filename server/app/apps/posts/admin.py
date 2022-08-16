from django.contrib import admin
from .models import Post

# Register your models here.

class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'short_description', 'author', 'get_categories', 'created_date']
    list_display_links = ['id', 'title']
    search_fields = ['title', 'content']

    def get_categories(self, obj: Post):
        return ', '.join([f'{c.category_id} - {c.title}' for c in obj.categories.all()])

admin.site.register(Post, PostAdmin)
