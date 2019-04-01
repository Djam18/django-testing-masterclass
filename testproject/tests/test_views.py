import pytest
from django.test import Client, RequestFactory
from django.contrib.auth.models import User
from .factories import PostFactory, UserFactory


@pytest.mark.django_db
class TestPostViews:

    def setup_method(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.user = UserFactory()

    def teardown_method(self):
        pass

    def test_post_list_returns_200(self):
        response = self.client.get('/api/posts/')
        assert response.status_code == 200

    def test_post_detail_returns_200(self):
        post = PostFactory(author=self.user)
        response = self.client.get(f'/api/posts/{post.id}/')
        assert response.status_code == 200

    def test_post_create_requires_auth(self):
        data = {'title': 'Test', 'content': 'Content', 'author': self.user.id}
        response = self.client.post('/api/posts/', data)
        assert response.status_code == 403

    def test_post_create_authenticated(self):
        self.client.force_login(self.user)
        data = {
            'title': 'My New Post',
            'content': 'Some content here',
            'author': self.user.id,
            'published': False,
        }
        response = self.client.post('/api/posts/', data, content_type='application/json')
        assert response.status_code == 201

    def test_post_update_authenticated(self):
        post = PostFactory(author=self.user)
        self.client.force_login(self.user)
        data = {
            'title': 'Updated Title',
            'content': 'Updated content',
            'author': self.user.id,
            'published': False,
        }
        response = self.client.put(
            f'/api/posts/{post.id}/',
            data,
            content_type='application/json'
        )
        assert response.status_code == 200

    def test_post_delete_authenticated(self):
        post = PostFactory(author=self.user)
        self.client.force_login(self.user)
        response = self.client.delete(f'/api/posts/{post.id}/')
        assert response.status_code == 204

    def test_post_list_returns_all_posts(self):
        PostFactory.create_batch(3, author=self.user)
        response = self.client.get('/api/posts/')
        import json
        data = json.loads(response.content)
        assert len(data) >= 3

    def test_nonexistent_post_returns_404(self):
        response = self.client.get('/api/posts/99999/')
        assert response.status_code == 404

    def test_post_update_returns_404_for_unknown(self):
        self.client.force_login(self.user)
        data = {'title': 'x', 'content': 'y', 'author': self.user.id, 'published': False}
        response = self.client.put('/api/posts/99999/', data, content_type='application/json')
        assert response.status_code == 404

    def test_delete_returns_403_unauthenticated(self):
        post = PostFactory(author=self.user)
        response = self.client.delete(f'/api/posts/{post.id}/')
        assert response.status_code == 403

    def test_tag_list_returns_200(self):
        response = self.client.get('/api/tags/')
        assert response.status_code == 200

    def test_comment_list_returns_200(self):
        response = self.client.get('/api/comments/')
        assert response.status_code == 200
