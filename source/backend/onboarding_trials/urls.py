# backend/onboarding_trials/urls.py
from django.urls import path
from . import views

app_name = 'onboarding_trials'

urlpatterns = [
    path('status/', views.trial_status, name='trial_status'),
    path('extend/', views.extend_trial_period, name='extend_trial'),
    path('events/', views.trial_events, name='trial_events'),
    path('upgrade/', views.request_upgrade, name='request_upgrade'),
    path('upgrade-detection/', views.upgrade_detection, name='upgrade_detection'),
]  