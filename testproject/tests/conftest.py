import pytest
from rest_framework.test import APIClient
from .factories import UserFactory


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def authenticated_user(db):
    user = UserFactory()
    return user
