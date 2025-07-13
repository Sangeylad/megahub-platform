# backend/file_compressor/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'file-types', views.SupportedFileTypeViewSet, basename='supported-file-type')
router.register(r'optimizations', views.FileOptimizationViewSet, basename='file-optimization')

app_name = 'file_compressor'

urlpatterns = [
    path('', include(router.urls)),
    path('quota/', views.OptimizationQuotaView.as_view(), name='optimization-quota'),
    path('stats/', views.OptimizationStatsView.as_view(), name='optimization-stats'),
]