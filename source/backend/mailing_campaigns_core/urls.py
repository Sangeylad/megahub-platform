from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.campaign_views import CampaignViewSet

router = DefaultRouter()
router.register(r'', CampaignViewSet, basename='campaign')

app_name = 'mailing_campaigns_core'
urlpatterns = [path('', include(router.urls))]
