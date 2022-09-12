import os
import shutil
from django import forms
from django.conf import settings
from django.contrib import admin
from django.http import HttpRequest
from django.urls import reverse
from django.utils.safestring import mark_safe
from django_stubs_ext.patch import QuerySet
from .models import Post, PostDraft, PostImage

# Register your models here.

class PostImageForm(forms.ModelForm):
    model = PostImage

class PostImageAdmin(admin.TabularInline):
    model = PostImage
    form = PostImageForm

class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'short_description', 'author_link', 'preview', 'get_categories', 'get_tags', 'created_date']
    readonly_fields = ['draft']
    list_display_links = ['id', 'title']
    search_fields = ['title', 'content']
    inlines = [PostImageAdmin]
    exclude = ['images']

    def delete_model(self, request, obj):
        if os.path.exists(os.path.abspath(f'{settings.MEDIA_ROOT}/posts/post_{obj.id}')):
            shutil.rmtree(os.path.abspath(f'{settings.MEDIA_ROOT}/posts/post_{obj.id}'))
        super().delete_model(request=request, obj=obj)

    def delete_queryset(self, request: HttpRequest, queryset: QuerySet) -> None:
        for post in queryset:
            if os.path.exists(os.path.abspath(f'{settings.MEDIA_ROOT}/posts/post_{post.id}')):
                shutil.rmtree(os.path.abspath(f'{settings.MEDIA_ROOT}/posts/post_{post.id}'))
        return super().delete_queryset(request, queryset)

    def get_categories(self, obj: Post):
        return ', '.join([f'{c.category_id} - {c.title}' for c in obj.categories.all()])

    get_categories.short_description = 'Category' #type: ignore

    def get_tags(self, obj: Post):
        return ', '.join([f'{c.title}' for c in obj.tags.all()])

    get_tags.short_description = 'Tags' #type: ignore

    def author_link(self, post: Post):
        url = reverse("admin:core_user_change", args=[post.author.user.id])
        link = f'<a href="{url}">{post.author}</a>'
        return mark_safe(link)

    author_link.short_description = 'Author' #type: ignore

class PostDraftAdmin(admin.ModelAdmin):
    list_display = ['id', 'post_link']
    readonly_fields = ['post']

    def post_link(self, draft: PostDraft):
        url = reverse("admin:posts_post_change", args=[draft.post.id])
        link = f'<a href="{url}">{draft.post.title}</a>'
        return mark_safe(link)

    post_link.short_description = 'Post' #type: ignore

admin.site.register(Post, PostAdmin)
admin.site.register(PostDraft, PostDraftAdmin)
