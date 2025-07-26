from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.analytics_views import EmailEventViewSet

router = DefaultRouter()
router.register(r'events', EmailEventViewSet, basename='emailevent')

app_name = 'mailing_analytics_core'
urlpatterns = [path('', include(router.urls))]
