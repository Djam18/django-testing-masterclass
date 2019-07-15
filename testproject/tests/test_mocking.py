"""Tests demonstrating how to mock external services."""
import json
from unittest.mock import patch, MagicMock
import pytest
import responses as responses_lib
from .factories import PostFactory, UserFactory


class TestMockingRequests:
    """Mock external HTTP calls using unittest.mock.patch."""

    @pytest.mark.django_db
    def test_mock_external_api_call(self):
        """Mock an external weather API call."""
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"temp": 20.5, "city": "Paris"}
            mock_get.return_value = mock_response

            import requests
            result = requests.get("https://api.weather.com/Paris")

            assert result.status_code == 200
            assert result.json()["city"] == "Paris"
            mock_get.assert_called_once_with("https://api.weather.com/Paris")

    @pytest.mark.django_db
    def test_mock_external_api_timeout(self):
        """Test behavior when external API times out."""
        import requests as req
        with patch('requests.get') as mock_get:
            mock_get.side_effect = req.exceptions.Timeout("Connection timed out")

            with pytest.raises(req.exceptions.Timeout):
                req.get("https://api.weather.com/Paris", timeout=5)

    @pytest.mark.django_db
    def test_mock_email_sending(self):
        """Mock Django email backend."""
        with patch('django.core.mail.send_mail') as mock_mail:
            mock_mail.return_value = 1

            from django.core.mail import send_mail
            result = send_mail(
                subject="New post published",
                message="Check out the new post",
                from_email="noreply@example.com",
                recipient_list=["user@example.com"],
            )

            assert result == 1
            mock_mail.assert_called_once()
            call_kwargs = mock_mail.call_args
            assert call_kwargs[1]['subject'] == "New post published" or call_kwargs[0][0] == "New post published"

    @pytest.mark.django_db
    def test_mock_third_party_service(self):
        """Mock a third-party notification service."""
        with patch('blog.views.notify_subscribers') as mock_notify:
            mock_notify.return_value = {"sent": 5, "failed": 0}

            result = mock_notify(post_id=1)

            assert result["sent"] == 5
            mock_notify.assert_called_once_with(post_id=1)


class TestResponsesLibrary:
    """Mock HTTP calls using the `responses` library."""

    @pytest.mark.django_db
    @responses_lib.activate
    def test_mock_get_request(self):
        """Use responses library to intercept HTTP calls."""
        responses_lib.add(
            responses_lib.GET,
            "https://jsonplaceholder.typicode.com/posts/1",
            json={"id": 1, "title": "Test Post", "body": "Content here"},
            status=200,
        )

        import requests
        response = requests.get("https://jsonplaceholder.typicode.com/posts/1")

        assert response.status_code == 200
        assert response.json()["title"] == "Test Post"
        assert len(responses_lib.calls) == 1

    @pytest.mark.django_db
    @responses_lib.activate
    def test_mock_post_request(self):
        """Mock a POST request to external API."""
        responses_lib.add(
            responses_lib.POST,
            "https://api.example.com/webhook",
            json={"received": True, "id": "evt_123"},
            status=200,
        )

        import requests
        payload = {"event": "post_published", "post_id": 42}
        response = requests.post(
            "https://api.example.com/webhook",
            json=payload,
        )

        assert response.status_code == 200
        assert response.json()["received"] is True

    @pytest.mark.django_db
    @responses_lib.activate
    def test_mock_api_error_response(self):
        """Test that our code handles upstream API errors."""
        responses_lib.add(
            responses_lib.GET,
            "https://api.example.com/data",
            json={"error": "rate limit exceeded"},
            status=429,
        )

        import requests
        response = requests.get("https://api.example.com/data")

        assert response.status_code == 429
        assert "error" in response.json()


class TestPatchingDatabaseCalls:
    """Demonstrate patching at different levels."""

    @pytest.mark.django_db
    def test_patch_queryset(self):
        """Patch a specific queryset method."""
        mock_posts = [MagicMock(title="Post 1"), MagicMock(title="Post 2")]

        with patch('blog.models.Post.objects') as mock_manager:
            mock_manager.filter.return_value = mock_posts
            mock_manager.filter.return_value.__len__ = lambda self: 2

            from blog.models import Post
            result = Post.objects.filter(published=True)

            assert len(result) == 2

    @pytest.mark.django_db
    def test_mock_cache(self):
        """Mock Django cache backend."""
        with patch('django.core.cache.cache') as mock_cache:
            mock_cache.get.return_value = None
            mock_cache.set.return_value = True

            from django.core.cache import cache
            result = cache.get("some_key")
            assert result is None

            cache.set("some_key", {"data": "value"}, 300)
            mock_cache.set.assert_called_once_with("some_key", {"data": "value"}, 300)
