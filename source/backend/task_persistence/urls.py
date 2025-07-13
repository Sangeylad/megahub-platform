# backend/task_persistence/urls.py

from rest_framework.routers import DefaultRouter
from .views import PersistentJobViewSet, JobCheckpointViewSet

router = DefaultRouter()
router.register(r'persistent-jobs', PersistentJobViewSet, basename='persistent-jobs')
router.register(r'checkpoints', JobCheckpointViewSet, basename='checkpoints')

urlpatterns = router.urls
