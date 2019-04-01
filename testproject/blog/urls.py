from rest_framework.routers import DefaultRouter
from .views import PostViewSet, CommentViewSet, TagViewSet

router = DefaultRouter()
router.register('posts', PostViewSet)
router.register('comments', CommentViewSet)
router.register('tags', TagViewSet)

urlpatterns = router.urls
