# backend/billing_stripe/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from billing_stripe.views.stripe_views import (
    StripeCustomerViewSet, StripeSubscriptionViewSet, StripeInvoiceViewSet,
    StripePaymentMethodViewSet, StripeWebhookEventViewSet, StripeCheckoutViewSet,
    StripeSyncViewSet
)
from billing_stripe.webhooks.stripe_webhooks import StripeWebhookView, stripe_webhook_handler

router = DefaultRouter()
router.register(r'customers', StripeCustomerViewSet, basename='stripe-customer')
router.register(r'subscriptions', StripeSubscriptionViewSet, basename='stripe-subscription')
router.register(r'invoices', StripeInvoiceViewSet, basename='stripe-invoice')
router.register(r'payment-methods', StripePaymentMethodViewSet, basename='stripe-payment-method')
router.register(r'webhook-events', StripeWebhookEventViewSet, basename='stripe-webhook-event')
router.register(r'checkout', StripeCheckoutViewSet, basename='stripe-checkout')
router.register(r'sync', StripeSyncViewSet, basename='stripe-sync')

urlpatterns = [
    path('', include(router.urls)),
    
    # Webhooks Stripe
    path('webhooks/', StripeWebhookView.as_view(), name='stripe_webhook'),
    path('webhooks/api/', stripe_webhook_handler, name='stripe_webhook_api'),
]
