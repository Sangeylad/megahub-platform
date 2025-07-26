# /var/www/megahub/source/backend/mailing_integrations_core/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

app_name = 'mailing_integrations_core'
urlpatterns = [
    path('', include(router.urls)),
]
