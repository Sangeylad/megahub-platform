# /var/www/megahub/backend/mailing_contacts_core/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.contact_views import EmailSubscriberViewSet

router = DefaultRouter()
router.register(r'', EmailSubscriberViewSet, basename='emailsubscriber')

app_name = 'mailing_contacts_core'
urlpatterns = [
    path('', include(router.urls)),
]
