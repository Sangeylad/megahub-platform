# backend/auth_core/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from auth_core.views.auth_views import AuthViewSet

router = DefaultRouter()
# Pas de préfixe car c'est géré dans django_app/urls.py
router.register(r'', AuthViewSet, basename='auth')

urlpatterns = [
    # Router pour auth (/auth/ et actions comme /auth/login/, /auth/logout/)
    path('', include(router.urls)),
]
