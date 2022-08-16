from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.response import Response
from app.apps.core.models import User

from .models import Post
# Create your tests here.

class PostTestCase(TestCase):
    client = APIClient()

    def setUp(self):
        User.objects.create(first_name="Daniil", last_name="Perto")
        user: User = User.objects.get(first_name="Daniil")
        Post.objects.create(title="Test title", short_description="short", author=user)

    def test_get_all_posts(self):
        response: Response = self.client.get('/api/v1/posts/')
        data = response.json()

        self.assertEqual(data[0]['title'], 'Test title')
        self.assertEqual(response.status_code, 200)