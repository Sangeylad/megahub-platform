# /var/www/megahub/backend/mailing_deliverability_reputation/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter

# TODO: Importer les ViewSets quand ils seront créés
# from .views import YourViewSet

router = DefaultRouter()
# TODO: Enregistrer les ViewSets
# router.register(r'', YourViewSet, basename='your-model')

app_name = 'mailing_deliverability_reputation'
urlpatterns = [
    # TODO: Endpoints REST à implémenter
    # Suivra le même pattern que les apps core :
    # - GET/POST /deliverability_reputation/ → CRUD principal
    # - Actions spécialisées avec @action
    
    # Router DRF (vide pour l'instant)
    path('', include(router.urls)),
]
