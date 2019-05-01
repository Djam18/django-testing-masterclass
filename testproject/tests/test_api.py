import pytest
from rest_framework.test import APIClient
from .factories import PostFactory, UserFactory, TagFactory, CommentFactory


@pytest.mark.django_db
class TestPostAPI:

    def setup_method(self):
        self.client = APIClient()
        self.user = UserFactory()

    def teardown_method(self):
        pass

    def test_list_posts_unauthenticated(self):
        PostFactory.create_batch(3)
        response = self.client.get('/api/posts/')
        assert response.status_code == 200
        assert len(response.data) >= 3

    def test_list_posts_authenticated(self):
        self.client.force_authenticate(user=self.user)
        PostFactory.create_batch(2, author=self.user)
        response = self.client.get('/api/posts/')
        assert response.status_code == 200

    def test_create_post_authenticated(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'title': 'API Test Post',
            'content': 'Content from API test',
            'author': self.user.id,
            'published': False,
        }
        response = self.client.post('/api/posts/', data)
        assert response.status_code == 201
        assert response.data['title'] == 'API Test Post'

    def test_create_post_unauthenticated_fails(self):
        data = {'title': 'Should fail', 'content': 'nope', 'author': self.user.id}
        response = self.client.post('/api/posts/', data)
        assert response.status_code == 403

    def test_retrieve_post(self):
        post = PostFactory(author=self.user)
        response = self.client.get(f'/api/posts/{post.id}/')
        assert response.status_code == 200
        assert response.data['id'] == post.id

    def test_update_post_authenticated(self):
        post = PostFactory(author=self.user)
        self.client.force_authenticate(user=self.user)
        data = {
            'title': 'Updated',
            'content': 'Updated content',
            'author': self.user.id,
            'published': True,
        }
        response = self.client.put(f'/api/posts/{post.id}/', data)
        assert response.status_code == 200
        assert response.data['title'] == 'Updated'

    def test_partial_update_post(self):
        post = PostFactory(author=self.user)
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(f'/api/posts/{post.id}/', {'published': True})
        assert response.status_code == 200
        assert response.data['published'] == True

    def test_delete_post_authenticated(self):
        post = PostFactory(author=self.user)
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f'/api/posts/{post.id}/')
        assert response.status_code == 204

    def test_retrieve_nonexistent_post(self):
        response = self.client.get('/api/posts/99999/')
        assert response.status_code == 404

    def test_filter_posts_by_published(self):
        PostFactory(author=self.user, published=True)
        PostFactory(author=self.user, published=False)
        response = self.client.get('/api/posts/?published=true')
        assert response.status_code == 200

    def test_tag_list(self):
        TagFactory.create_batch(3)
        response = self.client.get('/api/tags/')
        assert response.status_code == 200
        assert len(response.data) >= 3

    def test_comment_create_authenticated(self):
        post = PostFactory(author=self.user)
        self.client.force_authenticate(user=self.user)
        data = {'post': post.id, 'author': self.user.id, 'content': 'Nice post!'}
        response = self.client.post('/api/comments/', data)
        assert response.status_code == 201

    def test_comment_list_for_post(self):
        post = PostFactory(author=self.user)
        CommentFactory.create_batch(3, post=post)
        response = self.client.get('/api/comments/')
        assert response.status_code == 200

    def test_delete_comment_unauthenticated(self):
        comment = CommentFactory()
        response = self.client.delete(f'/api/comments/{comment.id}/')
        assert response.status_code == 403

    def test_api_returns_json(self):
        response = self.client.get('/api/posts/')
        assert response.accepted_media_type == 'application/json'
