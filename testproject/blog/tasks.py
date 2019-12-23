"""Celery tasks for the blog app."""
from celery import shared_task


@shared_task
def send_post_notification(post_id, recipient_emails):
    """Send email notifications when a post is published.

    Args:
        post_id: ID of the published post.
        recipient_emails: List of emails to notify.

    Returns:
        dict with sent count.
    """
    from django.core.mail import send_mail
    from blog.models import Post

    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return {"sent": 0, "error": "post not found"}

    sent = 0
    for email in recipient_emails:
        send_mail(
            subject=f"New post: {post.title}",
            message=f"Check out the new post: {post.title}",
            from_email="noreply@blog.com",
            recipient_list=[email],
        )
        sent += 1

    return {"sent": sent, "post_id": post_id}


@shared_task
def generate_post_stats(post_id):
    """Compute statistics for a post (view count, comment count).

    Args:
        post_id: ID of the post to compute stats for.

    Returns:
        dict with stats.
    """
    from blog.models import Post

    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return {"error": "post not found"}

    return {
        "post_id": post_id,
        "title": post.title,
        "comment_count": post.comments.count(),
    }


@shared_task
def cleanup_old_drafts():
    """Delete draft posts older than 30 days.

    Returns:
        dict with deleted count.
    """
    from django.utils import timezone
    from datetime import timedelta
    from blog.models import Post

    cutoff = timezone.now() - timedelta(days=30)
    old_drafts = Post.objects.filter(published=False, created_at__lt=cutoff)
    count = old_drafts.count()
    old_drafts.delete()
    return {"deleted": count}
