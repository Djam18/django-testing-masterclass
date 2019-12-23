"""Tests for Celery tasks using CELERY_TASK_ALWAYS_EAGER=True."""
from unittest.mock import patch, call
import pytest
from .factories import PostFactory, UserFactory


@pytest.mark.django_db
class TestSendPostNotification:
    """Test the send_post_notification task."""

    def test_task_runs_synchronously_with_always_eager(self, settings):
        """With CELERY_TASK_ALWAYS_EAGER=True, tasks execute inline."""
        settings.CELERY_TASK_ALWAYS_EAGER = True
        post = PostFactory(published=True)

        with patch('django.core.mail.send_mail') as mock_mail:
            from blog.tasks import send_post_notification
            result = send_post_notification.delay(
                post_id=post.id,
                recipient_emails=["user1@example.com", "user2@example.com"]
            )

            assert result.result["sent"] == 2
            assert mock_mail.call_count == 2

    def test_task_sends_correct_subject(self, settings):
        """Notification email contains the post title."""
        settings.CELERY_TASK_ALWAYS_EAGER = True
        post = PostFactory(published=True, title="My Amazing Post")

        with patch('django.core.mail.send_mail') as mock_mail:
            from blog.tasks import send_post_notification
            send_post_notification.delay(
                post_id=post.id,
                recipient_emails=["user@example.com"]
            )

            subject = mock_mail.call_args[1].get('subject') or mock_mail.call_args[0][0]
            assert "My Amazing Post" in subject

    def test_task_returns_error_for_missing_post(self, settings):
        """Task handles non-existent post gracefully."""
        settings.CELERY_TASK_ALWAYS_EAGER = True

        from blog.tasks import send_post_notification
        result = send_post_notification.delay(post_id=99999, recipient_emails=[])

        assert result.result["error"] == "post not found"
        assert result.result["sent"] == 0

    def test_task_sends_no_emails_for_empty_list(self, settings):
        """Task with empty recipient list sends zero emails."""
        settings.CELERY_TASK_ALWAYS_EAGER = True
        post = PostFactory(published=True)

        with patch('django.core.mail.send_mail') as mock_mail:
            from blog.tasks import send_post_notification
            result = send_post_notification.delay(
                post_id=post.id,
                recipient_emails=[]
            )

            assert result.result["sent"] == 0
            mock_mail.assert_not_called()


@pytest.mark.django_db
class TestGeneratePostStats:
    """Test the generate_post_stats task."""

    def test_returns_stats_for_existing_post(self, settings):
        """Stats task returns correct data for a valid post."""
        settings.CELERY_TASK_ALWAYS_EAGER = True
        post = PostFactory(published=True)

        from blog.tasks import generate_post_stats
        result = generate_post_stats.delay(post_id=post.id)

        assert result.result["post_id"] == post.id
        assert result.result["title"] == post.title
        assert "comment_count" in result.result

    def test_returns_error_for_missing_post(self, settings):
        """Stats task handles non-existent post."""
        settings.CELERY_TASK_ALWAYS_EAGER = True

        from blog.tasks import generate_post_stats
        result = generate_post_stats.delay(post_id=99999)

        assert result.result["error"] == "post not found"

    def test_comment_count_is_zero_for_new_post(self, settings):
        """Newly created post has zero comments."""
        settings.CELERY_TASK_ALWAYS_EAGER = True
        post = PostFactory(published=True)

        from blog.tasks import generate_post_stats
        result = generate_post_stats.delay(post_id=post.id)

        assert result.result["comment_count"] == 0


@pytest.mark.django_db
class TestCleanupOldDrafts:
    """Test the cleanup_old_drafts task."""

    def test_deletes_old_drafts(self, settings):
        """Old unpublished posts are deleted."""
        from datetime import timedelta
        from django.utils import timezone
        settings.CELERY_TASK_ALWAYS_EAGER = True

        old_post = PostFactory(published=False)
        # Manually age the post
        old_post.created_at = timezone.now() - timedelta(days=31)
        old_post.save()

        from blog.tasks import cleanup_old_drafts
        result = cleanup_old_drafts.delay()

        assert result.result["deleted"] >= 1

    def test_keeps_recent_drafts(self, settings):
        """Recent unpublished posts are not deleted."""
        settings.CELERY_TASK_ALWAYS_EAGER = True
        recent_draft = PostFactory(published=False)

        from blog.models import Post
        count_before = Post.objects.filter(published=False).count()

        from blog.tasks import cleanup_old_drafts
        cleanup_old_drafts.delay()

        count_after = Post.objects.filter(published=False).count()
        assert count_after == count_before

    def test_does_not_delete_published_posts(self, settings):
        """Published posts are never deleted by cleanup."""
        from datetime import timedelta
        from django.utils import timezone
        settings.CELERY_TASK_ALWAYS_EAGER = True

        old_published = PostFactory(published=True)
        old_published.created_at = timezone.now() - timedelta(days=60)
        old_published.save()

        from blog.models import Post
        from blog.tasks import cleanup_old_drafts
        cleanup_old_drafts.delay()

        assert Post.objects.filter(id=old_published.id).exists()
