# backend/onboarding_invitations/urls.py
from django.urls import path
from . import views

app_name = 'onboarding_invitations'

urlpatterns = [
    path('send/', views.send_user_invitation, name='send_invitation'),
    path('accept/', views.accept_user_invitation, name='accept_invitation'),
    path('status/<uuid:token>/', views.invitation_status, name='invitation_status'),
    path('resend/<int:invitation_id>/', views.resend_user_invitation, name='resend_invitation'),
    path('list/', views.list_company_invitations, name='list_invitations'),
    path('validate-slots/', views.validate_invitation_slots, name='validate_slots'),
]