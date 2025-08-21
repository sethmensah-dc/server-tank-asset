from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router for ViewSets
router = DefaultRouter()
router.register(r'browse/farms', views.FarmViewSet, basename='farm')
router.register(r'browse/assets', views.AssetViewSet, basename='asset')

urlpatterns = [
    # API Root
    path('', views.api_root, name='api_root'),
    
    # Browsable ViewSets
    path('', include(router.urls)),
    
    # Farm assets endpoint
    path('farm/<str:farm_id>/assets', views.get_farm_assets, name='farm_assets'),
    
    # Asset endpoints
    path('api/asset/<str:asset_id>', views.get_asset_details, name='asset_details'),
    path('api/asset-name/<str:asset_name>', views.get_asset_by_name, name='asset_by_name'),
    path('api/asset-model/<str:asset_type>', views.get_asset_type_model, name='asset_type_model'),
    path('api/asset-type/<str:asset_type>', views.get_assets_by_type, name='assets_by_type'),
    path('api/asset-by-model/<str:model_id>', views.get_asset_by_model_id, name='asset_by_model'),
    
    # Farm model endpoints
    path('api/farm-model/<str:farm_id>', views.get_farm_model, name='farm_model'),
    path('api/farm-site-model/<str:farm_id>/upload', views.upload_farm_site_model, name='farm_site_model_upload'),
    path('api/farm-layout-pdf/<str:farm_id>/upload', views.upload_farm_layout_pdf, name='farm_layout_pdf_upload'),
    path('api/farm-layout/<str:farm_id>', views.get_farm_layout_pdf, name='farm_layout_pdf'),
    
    # Asset model endpoints
    path('api/asset-model/<str:asset_id>/upload', views.upload_asset_model, name='asset_model_upload'),
    path('api/asset/<str:asset_id>/model', views.get_asset_model_file, name='asset_model_file'),
]