# backend/public_tools/urls.py
from django.urls import path
from .views import document_views, web_views, real_estate_views, optimization_views
from .ecommerce.views import ecommerce_views

app_name = 'public_tools'

urlpatterns = [
    # Document tools - Convertisseur
    path('document/converter/render/', document_views.render_converter, name='converter_render'),
    path('document/converter/process/', document_views.process_conversion, name='converter_process'),
    path('document/converter/process-batch/', document_views.process_batch_conversion, name='converter_process_batch'),
    path('document/converter/process-server/', document_views.process_conversion_server, name='converter_process_server'),
    
    # Statut et téléchargement
    path('document/status/<uuid:conversion_id>/', document_views.conversion_status, name='conversion_status'),
    path('document/download/<uuid:download_token>/', document_views.download_converted_file, name='download_file'),
    
    # Debug endpoint (dev seulement)
    path('document/debug/', document_views.debug_conversions, name='debug_conversions'),
    
    # Web tools
    path('web/shortener/render/', web_views.render_shortener, name='shortener_render'),
    path('web/shortener/process/', web_views.process_url_shortening, name='shortener_process'),
    
    # Real estate tools
    path('real-estate/simulator/render/', real_estate_views.render_simulator, name='simulator_render'),
    path('real-estate/simulator/process/', real_estate_views.process_simulation, name='simulator_process'),
    
    # File optimization tools
    path('file/optimizer/render/', optimization_views.render_optimizer, name='optimizer_render'),
    path('file/optimizer/process/', optimization_views.process_optimization, name='optimizer_process'),
    path('file/optimizer/status/<uuid:optimization_id>/', optimization_views.optimization_status, name='optimization_status'),
    path('file/optimizer/download/<uuid:download_token>/', optimization_views.download_optimized_file, name='download_optimized'),
    path('file/optimizer/', optimization_views.render_optimizer_template, name='optimizer_template'),
    path('file/optimizer/process-server/', optimization_views.render_optimizer_server, name='optimizer_process_server'),
    
    # ✅ E-commerce tools - ROAS Calculator (CORRIGÉ pour suivre le pattern)
    path('ecommerce/roas-calculator/render/', ecommerce_views.render_roas_calculator, name='roas_calculator_render'),
    
    # ✅ Endpoints futurs si tu en as besoin (optionnels)
    # path('ecommerce/roas-calculator/process/', ecommerce_views.process_roas_calculation, name='roas_calculator_process'),
    # path('ecommerce/roas-calculator/export/', ecommerce_views.export_roas_scenario, name='roas_calculator_export'),
]