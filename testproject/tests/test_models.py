import pytest
from .factories import PostFactory, UserFactory, CommentFactory, TagFactory


@pytest.mark.django_db
class TestPostModel:

    def setup_method(self):
        self.user = UserFactory()

    def teardown_method(self):
        pass

    def test_post_str_returns_title(self):
        post = PostFactory(title="My test post", author=self.user)
        assert str(post) == "My test post"

    def test_post_default_published_is_false(self):
        post = PostFactory(author=self.user)
        assert post.published == False

    def test_post_can_be_published(self):
        post = PostFactory(author=self.user, published=True)
        assert post.published == True

    def test_post_has_created_at(self):
        post = PostFactory(author=self.user)
        assert post.created_at is not None

    def test_post_author_is_user(self):
        post = PostFactory(author=self.user)
        assert post.author == self.user

    def test_post_can_have_tags(self):
        post = PostFactory(author=self.user)
        tag = TagFactory()
        post.tags.add(tag)
        assert tag in post.tags.all()

    def test_comment_linked_to_post(self):
        post = PostFactory(author=self.user)
        comment = CommentFactory(post=post)
        assert comment.post == post
        assert comment in post.comments.all()

    def test_factory_creates_valid_post(self):
        post = PostFactory()
        assert post.id is not None
        assert len(post.title) > 0
