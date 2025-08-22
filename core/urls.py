from django.urls import path
from . import views

urlpatterns = [
    # API Root (keep for documentation)
    path('', views.api_root, name='api_root'),
    
    # Core Flask-compatible endpoints
    path('farm/<str:farm_id>/assets', views.get_farm_assets, name='farm_assets'),
    path('api/asset/<str:asset_id>', views.get_asset_details, name='asset_details'),
    path('api/asset-model/<str:asset_type>', views.get_asset_type_model, name='asset_type_model'),
    path('api/farm-model/<str:farm_id>', views.get_farm_model, name='farm_model'),
    path('import-data/', views.import_flask_data, name='import_data'),  # TEMPORARY
]