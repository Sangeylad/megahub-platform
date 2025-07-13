# backend/file_converter/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'formats', views.SupportedFormatViewSet, basename='supported-format')
router.register(r'conversions', views.FileConversionViewSet, basename='file-conversion')

app_name = 'file_converter'

urlpatterns = [
    path('', include(router.urls)),
]