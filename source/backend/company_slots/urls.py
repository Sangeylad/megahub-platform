# backend/company_slots/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from company_slots.views.slots_views import CompanySlotsViewSet

router = DefaultRouter()
router.register(r'', CompanySlotsViewSet, basename='company-slots')

urlpatterns = [
    path('', include(router.urls)),
]