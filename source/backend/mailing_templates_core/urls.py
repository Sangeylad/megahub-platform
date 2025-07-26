from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.template_views import EmailTemplateViewSet

router = DefaultRouter()
router.register(r'', EmailTemplateViewSet, basename='emailtemplate')

app_name = 'mailing_templates_core'
urlpatterns = [path('', include(router.urls))]
