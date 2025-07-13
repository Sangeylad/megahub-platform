# backend/onboarding_registration/urls.py
# onboarding_registration/urls.py
from django.urls import path
from . import views

app_name = 'onboarding_registration'

urlpatterns = [
    path('trigger-business-creation/', views.trigger_business_creation, name='trigger_business_creation'),
]