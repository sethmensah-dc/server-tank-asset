import os
from django.shortcuts import get_object_or_404
from django.conf import settings
from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from drf_spectacular.types import OpenApiTypes
from .models import Farm, Asset, AssetType, Location
from .serializers import (
    FarmSerializer, AssetDetailSerializer, FarmAssetSerializer,
    AssetSerializer
)


@extend_schema(
    tags=['API Root'],
    summary='API Root',
    description='Main entry point showing all available API endpoints and sample data for testing.',
    responses={200: OpenApiResponse(description='Available API endpoints and sample data')}
)
@api_view(['GET'])
def api_root(request, format=None):
    """
    API Root - Browse all available endpoints
    """
    return Response({
        'farms': {
            'farm_assets': 'Use: /farm/{farm_id}/assets',
            'farm_model': 'Use: /api/farm-model/{model_id}',
        },
        'assets': {
            'asset_details': 'Use: /api/asset/{asset_id}',
            'asset_by_name': 'Use: /api/asset-name/{asset_name}',
            'asset_by_model': 'Use: /api/asset-model/{model_id}',
            'assets_by_type': 'Use: /api/asset-type/{asset_type}',
        },
        'sample_data': {
            'sample_farm_id': 'SYS-1D3407DB-F-13083',
            'sample_asset_id': 'SYS-1D3407DB-F-13083-A-06527',
            'csv_farm_id': 'SYS-88627B0B-F-E304B',
            'csv_asset_id': 'SYS-88627B0B-F-E304B-A-6BDDD',
        },
        'browse': {
            'farms': reverse('farm-list', request=request, format=format),
            'assets': reverse('asset-list', request=request, format=format),
        },
        'documentation': {
            'swagger': reverse('swagger-ui', request=request, format=format),
            'redoc': reverse('redoc', request=request, format=format),
            'schema': reverse('schema', request=request, format=format),
        },
        'links': {
            'admin': reverse('admin:index', request=request, format=format),
            'api_auth': '/api-auth/',
        }
    })


@extend_schema(
    tags=['Farms'],
    summary='Get Farm Assets',
    description='Retrieve all assets associated with a specific farm, including their specifications, events, and location data.',
    parameters=[
        OpenApiParameter(
            name='farm_id',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            description='Unique farm identifier (e.g., SYS-1D3407DB-F-13083)',
            required=True
        )
    ],
    responses={
        200: OpenApiResponse(description='Farm assets retrieved successfully'),
        404: OpenApiResponse(description='Farm not found')
    }
)
@api_view(['GET'])
def get_farm_assets(request, farm_id):
    """
    Get all assets for a specific farm
    URL: /farm/{farm_id}/assets
    """
    farm = get_object_or_404(Farm, farm_id=farm_id)
    
    # Get all assets for this farm with related data
    assets = Asset.objects.filter(farm=farm).select_related(
        'location', 'asset_type', 'material', 'content'
    ).prefetch_related('events__event_type')
    
    # Serialize assets
    assets_serializer = FarmAssetSerializer(assets, many=True)
    
    # Check for PDF file
    pdf_url = None
    pdf_file_path = os.path.join(settings.BASE_DIR, 'static', 'uploads', 'farm_layouts', f'{farm.farm_id}.pdf')
    if os.path.exists(pdf_file_path):
        pdf_url = f"/static/uploads/farm_layouts/{farm.farm_id}.pdf"
    
    return Response({
        'farm_id': farm.farm_id,
        'farm_name': farm.name,
        'assets_count': len(assets),
        'assets': assets_serializer.data,
        'farm_description': farm.description,
        'pdf_url': pdf_url,
        'location': farm.location.to_dict() if farm.location else {}
    })


@extend_schema(
    tags=['Assets'],
    summary='Get Asset Details',
    description='Retrieve detailed information for a specific asset including specifications, events, and relationships.',
    parameters=[
        OpenApiParameter(
            name='asset_id',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            description='Unique asset identifier (e.g., SYS-1D3407DB-F-13083-A-06527)',
            required=True
        )
    ],
    responses={
        200: AssetDetailSerializer,
        404: OpenApiResponse(description='Asset not found')
    }
)
@api_view(['GET'])
def get_asset_details(request, asset_id):
    """
    Get detailed asset information by asset_id
    URL: /api/asset/{asset_id}
    """
    asset = get_object_or_404(Asset, asset_id=asset_id)
    serializer = AssetDetailSerializer(asset)
    return Response(serializer.data)


@extend_schema(
    tags=['Assets'],
    summary='Get Asset by Name',
    description='Retrieve asset information using the asset name.',
    parameters=[
        OpenApiParameter(
            name='asset_name',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            description='Asset name (e.g., Tank A-001, Compressor 1)',
            required=True
        )
    ],
    responses={
        200: AssetDetailSerializer,
        404: OpenApiResponse(description='Asset not found')
    }
)
@api_view(['GET'])
def get_asset_by_name(request, asset_name):
    """
    Get asset by name
    URL: /api/asset/{asset_name}
    """
    asset = get_object_or_404(Asset, name=asset_name)
    serializer = AssetDetailSerializer(asset)
    return Response(serializer.data)


@extend_schema(
    tags=['Assets'],
    summary='Get Asset by Model ID',
    description='Retrieve asset information using the model ID.',
    parameters=[
        OpenApiParameter(
            name='model_id',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            description='Asset model identifier (e.g., oil_tank001, TANK-001)',
            required=True
        )
    ],
    responses={
        200: AssetDetailSerializer,
        404: OpenApiResponse(description='Asset not found')
    }
)
@api_view(['GET'])
def get_asset_by_model_id(request, model_id):
    """
    Get asset details by model_id (matches Flask /api/mokodel/{model_id})
    URL: /api/asset-model/{model_id}
    """
    asset = get_object_or_404(Asset, model_id=model_id)
    serializer = AssetDetailSerializer(asset)
    return Response(serializer.data)


@extend_schema(
    tags=['Assets'],
    summary='Get Assets by Type',
    description='Retrieve all assets of a specific type. Can search by type ID or name.',
    parameters=[
        OpenApiParameter(
            name='asset_type',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            description='Asset type ID or name (e.g., 1, "Fixed Roof Tank", "Compressor")',
            required=True
        )
    ],
    responses={
        200: AssetSerializer(many=True),
        200: OpenApiResponse(description='List of assets of the specified type')
    }
)
@api_view(['GET'])
def get_assets_by_type(request, asset_type):
    """
    Get assets by asset type
    URL: /api/asset-type/{asset_type}
    """
    # Try to find by asset type name or ID
    try:
        asset_type_id = int(asset_type)
        assets = Asset.objects.filter(asset_type__id=asset_type_id)
    except ValueError:
        assets = Asset.objects.filter(asset_type__name__icontains=asset_type)
    
    serializer = AssetSerializer(assets, many=True)
    return Response(serializer.data)


@extend_schema(
    tags=['Farms'],
    summary='Get Farm Model',
    description='Retrieve farm information by model/farm ID.',
    parameters=[
        OpenApiParameter(
            name='model_id',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            description='Farm model/farm identifier (e.g., SYS-1D3407DB-F-13083)',
            required=True
        )
    ],
    responses={
        200: FarmSerializer,
        404: OpenApiResponse(description='Farm not found')
    }
)
@api_view(['GET'])
def get_farm_model(request, model_id):
    """
    Get farm model details
    URL: /api/farm-model/{model_id}
    """
    # Assuming model_id refers to farm_id
    farm = get_object_or_404(Farm, farm_id=model_id)
    serializer = FarmSerializer(farm)
    return Response(serializer.data)


# Additional ViewSets for browsable API
@extend_schema(tags=['Browse'])
class FarmViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for browsing farms with pagination, search, and filtering capabilities.
    """
    queryset = Farm.objects.all()
    serializer_class = FarmSerializer
    lookup_field = 'farm_id'
    search_fields = ['name', 'description', 'company_id']
    ordering_fields = ['name', 'status', 'created_at']
    ordering = ['name']


@extend_schema(tags=['Browse'])
class AssetViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for browsing assets with pagination, search, and filtering capabilities.
    """
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer
    lookup_field = 'asset_id'
    search_fields = ['name', 'description', 'model_id']
    filterset_fields = ['status', 'asset_type', 'farm']
    ordering_fields = ['name', 'status', 'created_at', 'capacity']
    ordering = ['name']
