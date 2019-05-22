import pytest
from blog.serializers import PostSerializer, CommentSerializer, TagSerializer
from .factories import UserFactory, PostFactory


@pytest.mark.django_db
class TestPostSerializer:

    def setup_method(self):
        self.user = UserFactory()

    def teardown_method(self):
        pass

    def test_valid_post_data_is_valid(self):
        data = {
            'title': 'A valid post',
            'content': 'Content here',
            'author': self.user.id,
            'published': False,
        }
        serializer = PostSerializer(data=data)
        assert serializer.is_valid()

    def test_post_missing_title_invalid(self):
        data = {
            'content': 'Content here',
            'author': self.user.id,
        }
        serializer = PostSerializer(data=data)
        assert not serializer.is_valid()
        assert 'title' in serializer.errors

    def test_post_missing_content_invalid(self):
        data = {
            'title': 'Title',
            'author': self.user.id,
        }
        serializer = PostSerializer(data=data)
        assert not serializer.is_valid()
        assert 'content' in serializer.errors

    def test_post_id_is_read_only(self):
        post = PostFactory(author=self.user)
        serializer = PostSerializer(post)
        data = serializer.data
        assert 'id' in data
        # id should be present in output
        assert data['id'] == post.id

    def test_post_created_at_is_read_only(self):
        post = PostFactory(author=self.user)
        serializer = PostSerializer(post)
        assert 'created_at' in serializer.data

    def test_nested_post_has_all_fields(self):
        post = PostFactory(author=self.user)
        serializer = PostSerializer(post)
        data = serializer.data
        assert 'id' in data
        assert 'title' in data
        assert 'content' in data
        assert 'author' in data
        assert 'published' in data
        assert 'created_at' in data


@pytest.mark.django_db
class TestTagSerializer:

    def test_valid_tag_is_valid(self):
        data = {'name': 'python'}
        serializer = TagSerializer(data=data)
        assert serializer.is_valid()

    def test_empty_tag_name_invalid(self):
        data = {'name': ''}
        serializer = TagSerializer(data=data)
        assert not serializer.is_valid()
        assert 'name' in serializer.errors


@pytest.mark.django_db
class TestCommentSerializer:

    def setup_method(self):
        self.user = UserFactory()
        self.post = PostFactory(author=self.user)

    def test_valid_comment_is_valid(self):
        data = {
            'post': self.post.id,
            'author': self.user.id,
            'content': 'Great post!',
        }
        serializer = CommentSerializer(data=data)
        assert serializer.is_valid()

    def test_comment_missing_content_invalid(self):
        data = {
            'post': self.post.id,
            'author': self.user.id,
        }
        serializer = CommentSerializer(data=data)
        assert not serializer.is_valid()
        assert 'content' in serializer.errors
