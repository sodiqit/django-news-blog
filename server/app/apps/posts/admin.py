from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Post, PostDraft, PostImage

# Register your models here.

class PostImageAdmin(admin.StackedInline):
    model = PostImage

class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'short_description', 'author', 'preview', 'get_categories', 'created_date']
    readonly_fields = ['id', 'draft']
    list_display_links = ['id', 'title']
    search_fields = ['title', 'content']
    inlines = [PostImageAdmin]
    exclude = ['images']


    def get_categories(self, obj: Post):
        return ', '.join([f'{c.category_id} - {c.title}' for c in obj.categories.all()])

    get_categories.short_description = 'Category' #type: ignore

class PostDraftAdmin(admin.ModelAdmin):
    list_display = ['id', 'post_link']

    def post_link(self, draft: PostDraft):
        url = reverse("admin:posts_post_change", args=[draft.post.id])
        link = f'<a href="{url}">{draft.post.title}</a>'
        return mark_safe(link)

    post_link.short_description = 'Post' #type: ignore

admin.site.register(Post, PostAdmin)
admin.site.register(PostDraft, PostDraftAdmin)
