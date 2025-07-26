# /var/www/megahub/source/backend/mailing_configuration_core/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

app_name = 'mailing_configuration_core'
urlpatterns = [
    path('', include(router.urls)),
]
