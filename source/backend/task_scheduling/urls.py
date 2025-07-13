# backend/task_scheduling/urls.py

from django.urls import path, include
from rest_framework import routers
from .views import PeriodicTaskViewSet, CronJobViewSet, TaskCalendarViewSet

router = routers.DefaultRouter()
router.register(r'periodic-tasks', PeriodicTaskViewSet, basename='periodic-tasks')
router.register(r'cron-jobs', CronJobViewSet, basename='cron-jobs')
router.register(r'calendars', TaskCalendarViewSet, basename='calendars')

urlpatterns = [
    path('', include(router.urls)),
]