"""server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers, permissions
from django.conf import settings
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from app.apps.posts.views import PostCommentView, PostDraftView, PostView
from app.apps.core.views import GoogleLogin

schema_view = get_schema_view(
    openapi.Info(
        title="News blog",
        default_version='v1',
        description="News blog API endpoints",
        contact=openapi.Contact(email="test@email.com"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny, ),
)

router = routers.DefaultRouter()
router.register(r'posts', PostView)
router.register(r'drafts', PostDraftView)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/auth/", include("dj_rest_auth.urls")),
    path("api/v1/social-auth/google/",
         GoogleLogin.as_view(), name="google_login"),
    path("api/v1/posts/<int:post_id>/comments/", PostCommentView.as_view({ 'get': 'list', 'post': 'create' }), name='comments'),
    path("api/v1/", include(router.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += [
        re_path(r'^api/v1/swagger(?P<format>\.json|\.yaml)$',
                schema_view.without_ui(cache_timeout=0), name='schema-json'),
        re_path(r'^api/v1/swagger/$', schema_view.with_ui('swagger',
                cache_timeout=0), name='schema-swagger-ui'),
    ]
