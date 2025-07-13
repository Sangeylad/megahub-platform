# backend/billing_stripe/apps.py
from django.apps import AppConfig


class BillingStripeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'billing_stripe'
