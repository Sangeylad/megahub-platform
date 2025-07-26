# /var/www/megahub/source/backend/mailing_deliverability_core/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

app_name = 'mailing_deliverability_core'
urlpatterns = [
    path('', include(router.urls)),
]
