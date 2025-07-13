# backend/users_core/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from users_core.views.user_views import CustomUserViewSet

router = DefaultRouter()
# ✅ Pas de préfixe car c'est géré dans django_app/urls.py
router.register(r'', CustomUserViewSet, basename='user')

urlpatterns = [
    # Router pour les users (capture /users/ et actions comme /users/{id}/change-password/)
    path('', include(router.urls)),
]