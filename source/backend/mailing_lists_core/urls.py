# /var/www/megahub/backend/mailing_lists_core/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.list_views import MailingListViewSet

router = DefaultRouter()
router.register(r'', MailingListViewSet, basename='mailinglist')

app_name = 'mailing_lists_core'
urlpatterns = [
    path('', include(router.urls)),
]
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.list_views import MailingListViewSet

router = DefaultRouter()
router.register(r'', MailingListViewSet, basename='mailinglist')

app_name = 'mailing_lists_core'
urlpatterns = [path('', include(router.urls))]
