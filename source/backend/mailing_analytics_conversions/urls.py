# /var/www/megahub/backend/mailing_analytics_conversions/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter

# TODO: Importer les ViewSets quand ils seront créés
# from .views import YourViewSet

router = DefaultRouter()
# TODO: Enregistrer les ViewSets
# router.register(r'', YourViewSet, basename='your-model')

app_name = 'mailing_analytics_conversions'
urlpatterns = [
    # TODO: Endpoints REST à implémenter
    # Suivra le même pattern que les apps core :
    # - GET/POST /analytics_conversions/ → CRUD principal
    # - Actions spécialisées avec @action
    
    # Router DRF (vide pour l'instant)
    path('', include(router.urls)),
]
