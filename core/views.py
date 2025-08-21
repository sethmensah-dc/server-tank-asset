import os
from django.shortcuts import get_object_or_404
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework.reverse import reverse
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from drf_spectacular.types import OpenApiTypes
from .models import Farm, Asset, AssetType, Location
from .serializers import AssetDetailSerializer, FarmAssetSerializer


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
            'asset_model': 'Use: /api/asset-model/{asset_type}',
        },
        'sample_data': {
            'sample_farm_id': 'SYS-1D3407DB-F-13083',
            'sample_asset_id': 'SYS-1D3407DB-F-13083-A-06527',
            'csv_farm_id': 'SYS-88627B0B-F-E304B',
            'csv_asset_id': 'SYS-88627B0B-F-E304B-A-6BDDD',
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
    tags=['Farms'],
    summary='Get Farm Model File',
    description='Retrieve 3D farm model file (.glb format) by farm ID.',
    parameters=[
        OpenApiParameter(
            name='farm_id',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            description='Farm identifier (e.g., SYS-1D3407DB-F-13083)',
            required=True
        )
    ],
    responses={
        200: OpenApiResponse(description='3D model file (.glb format)'),
        404: OpenApiResponse(description='Model file not found')
    }
)
@api_view(['GET'])
def get_farm_model(request, farm_id):
    """
    Get farm 3D model file
    URL: /api/farm-model/{farm_id}
    """
    # Simple static file serving like Flask
    models_directory = os.path.join(settings.BASE_DIR, 'static', 'uploads', 'farm_models')
    filename = f"{farm_id}.glb"
    file_path = os.path.join(models_directory, filename)
    
    if not os.path.exists(file_path):
        return Response({'error': 'Model not found'}, status=status.HTTP_404_NOT_FOUND)
    
    from django.http import FileResponse
    from django.utils.encoding import smart_str
    
    response = FileResponse(
        open(file_path, 'rb'),
        content_type='model/gltf-binary',
        filename=smart_str(filename)
    )
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    return response












@extend_schema(
    tags=['Assets'],
    operation_id='get_asset_type_model',
    summary='Get Asset Type Model',
    description='Retrieve generic 3D model for an asset type (e.g., Compressor, FixedRoofTank).',
    parameters=[
        OpenApiParameter(
            name='asset_type',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            description='Asset type name (e.g., "Compressor", "FixedRoofTank", "ProcessPump")',
            required=True
        )
    ],
    responses={
        200: OpenApiResponse(description='3D model file (.glb format)'),
        404: OpenApiResponse(description='Asset type model not found')
    }
)
@api_view(['GET'])
def get_asset_type_model(request, asset_type):
    """
    Get generic 3D model for an asset type
    URL: /api/asset-model/{asset_type}
    """
    # Simple static file serving like Flask
    models_directory = os.path.join(settings.BASE_DIR, 'static', 'uploads', 'model_categories')
    filename = f"{asset_type}.glb"
    file_path = os.path.join(models_directory, filename)
    
    if not os.path.exists(file_path):
        return Response({'error': 'Asset model not found'}, status=status.HTTP_404_NOT_FOUND)
    
    from django.http import FileResponse
    from django.utils.encoding import smart_str
    
    response = FileResponse(
        open(file_path, 'rb'),
        content_type='model/gltf-binary',
        filename=smart_str(filename)
    )
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    return response


