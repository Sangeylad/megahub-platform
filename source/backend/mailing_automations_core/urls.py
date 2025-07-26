# /var/www/megahub/source/backend/mailing_automations_core/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter

# TODO: Importer les ViewSets quand ils seront créés
# from .views import YourViewSet

router = DefaultRouter()
# TODO: Enregistrer les ViewSets
# router.register(r'', YourViewSet, basename='your-model')

app_name = 'mailing_automations_core'
urlpatterns = [
    # TODO: Endpoints REST à implémenter
    # Router DRF (vide pour l'instant)
    path('', include(router.urls)),
]
