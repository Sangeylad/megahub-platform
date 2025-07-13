# backend/billing_core/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from billing_core.views.billing_views import (
    PlanViewSet, SubscriptionViewSet, InvoiceViewSet, UsageAlertViewSet
)

router = DefaultRouter()
router.register(r'plans', PlanViewSet, basename='plan')
router.register(r'subscriptions', SubscriptionViewSet, basename='subscription')
router.register(r'invoices', InvoiceViewSet, basename='invoice')
router.register(r'alerts', UsageAlertViewSet, basename='usage-alert')

urlpatterns = [
    path('', include(router.urls)),
]
