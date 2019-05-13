import pytest
from rest_framework.test import APIClient
from .factories import UserFactory, PostFactory, CommentFactory, TagFactory


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def authenticated_user(db):
    user = UserFactory()
    return user


@pytest.fixture
def admin_user(db):
    user = UserFactory()
    user.is_staff = True
    user.is_superuser = True
    user.save()
    return user


@pytest.fixture
def auth_client(db):
    client = APIClient()
    user = UserFactory()
    client.force_authenticate(user=user)
    return client, user


@pytest.fixture(scope='session')
def django_db_setup():
    pass


@pytest.fixture
def sample_post(db, authenticated_user):
    return PostFactory(author=authenticated_user)


@pytest.fixture
def sample_posts(db, authenticated_user):
    return PostFactory.create_batch(5, author=authenticated_user)


@pytest.fixture
def sample_tags(db):
    return TagFactory.create_batch(3)

