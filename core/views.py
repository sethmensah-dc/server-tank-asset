import os
from django.shortcuts import get_object_or_404
from django.conf import settings
from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework.reverse import reverse
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from drf_spectacular.types import OpenApiTypes
from .models import Farm, Asset, AssetType, Location, AssetModel
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
    summary='Get Farm Model File',
    description='Retrieve 3D farm model file (.glb format) by model ID.',
    parameters=[
        OpenApiParameter(
            name='model_id',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            description='Farm model identifier (e.g., SYS-1D3407DB-F-13083)',
            required=True
        )
    ],
    responses={
        200: OpenApiResponse(description='3D model file (.glb format)'),
        404: OpenApiResponse(description='Model file not found')
    }
)
@api_view(['GET'])
def get_farm_model(request, model_id):
    """
    Get farm 3D model file
    URL: /api/farm-model/{model_id}
    """
    # First try to find farm by farm_id and check if it has a model_file
    try:
        farm = Farm.objects.get(farm_id=model_id)
        if farm.model_file and farm.model_file.name:
            # Serve from Django's file field (MEDIA_ROOT)
            from django.http import FileResponse
            from django.utils.encoding import smart_str
            
            response = FileResponse(
                farm.model_file.open('rb'),
                content_type='model/gltf-binary',
                filename=smart_str(farm.model_file_name or f"{model_id}.glb")
            )
            response['Content-Disposition'] = f'inline; filename="{farm.model_file_name or f"{model_id}.glb"}"'
            return response
    except Farm.DoesNotExist:
        pass
    
    # Fallback to legacy filesystem approach for backward compatibility
    models_directory = os.path.join(settings.BASE_DIR, 'static', 'uploads', 'farm_models')
    filename = f"{model_id}.glb"
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
    tags=['Farms'],
    summary='Get Farm Layout PDF',
    description='Download 2D farm layout diagram as PDF file.',
    parameters=[
        OpenApiParameter(
            name='farm_id',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            description='Farm identifier (e.g., SYS-1F057E08-F-93E85)',
            required=True
        )
    ],
    responses={
        200: OpenApiResponse(description='PDF layout file'),
        404: OpenApiResponse(description='Layout not found')
    }
)
@api_view(['GET'])
def get_farm_layout_pdf(request, farm_id):
    """
    Get farm layout PDF file
    URL: /api/farm-layout/{farm_id}
    """
    pdf_directory = os.path.join(settings.BASE_DIR, 'static', 'uploads', 'farm_layouts')
    filename = f"{farm_id}.pdf"
    file_path = os.path.join(pdf_directory, filename)
    
    if not os.path.exists(file_path):
        return Response({'error': 'Layout PDF not found'}, status=status.HTTP_404_NOT_FOUND)
    
    from django.http import FileResponse
    from django.utils.encoding import smart_str
    
    response = FileResponse(
        open(file_path, 'rb'),
        content_type='application/pdf',
        filename=smart_str(filename)
    )
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    return response


@extend_schema(
    tags=['Farms'],
    summary='Upload Farm Model',
    description='Upload a 3D model file (.glb) for a specific farm.',
    parameters=[
        OpenApiParameter(
            name='farm_id',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            description='Farm identifier (e.g., SYS-1D3407DB-F-13083)',
            required=True
        )
    ],
    request={
        'multipart/form-data': {
            'type': 'object',
            'properties': {
                'model_file': {'type': 'string', 'format': 'binary', 'description': '3D model file (.glb format)'}
            }
        }
    },
    responses={
        200: OpenApiResponse(description='Model uploaded successfully'),
        400: OpenApiResponse(description='Invalid file or farm not found'),
        404: OpenApiResponse(description='Farm not found')
    }
)
@api_view(['POST'])
def upload_farm_model(request, farm_id):
    """
    Upload 3D model file for a farm
    URL: /api/farm-model/{farm_id}/upload
    """
    try:
        farm = get_object_or_404(Farm, farm_id=farm_id)
    except Farm.DoesNotExist:
        return Response({'error': 'Farm not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if 'model_file' not in request.FILES:
        return Response({'error': 'No model file provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    model_file = request.FILES['model_file']
    
    # Validate file extension
    if not model_file.name.lower().endswith('.glb'):
        return Response({'error': 'Only .glb files are allowed'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Save the file to the farm
    from django.utils import timezone
    farm.model_file = model_file
    farm.model_file_name = model_file.name
    farm.model_uploaded_at = timezone.now()
    farm.save()
    
    return Response({
        'message': 'Model uploaded successfully',
        'farm_id': farm.farm_id,
        'farm_name': farm.name,
        'file_name': farm.model_file_name,
        'file_size': farm.model_file.size,
        'uploaded_at': farm.model_uploaded_at
    })


@extend_schema(
    tags=['Assets'],
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
    # First try to find in database by AssetModel
    try:
        asset_type_obj = AssetType.objects.get(name__icontains=asset_type)
        asset_model = AssetModel.objects.filter(
            asset_type=asset_type_obj, 
            is_default=True
        ).first()
        
        if asset_model and asset_model.model_file:
            from django.http import FileResponse
            from django.utils.encoding import smart_str
            
            response = FileResponse(
                asset_model.model_file.open('rb'),
                content_type='model/gltf-binary',
                filename=smart_str(f"{asset_type}.glb")
            )
            response['Content-Disposition'] = f'inline; filename="{asset_type}.glb"'
            return response
    except AssetType.DoesNotExist:
        pass
    
    # Fallback to legacy filesystem approach
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
