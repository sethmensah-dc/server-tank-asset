from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from typing import Dict, List, Any, Optional
from .models import Farm, Asset, Location, AssetType, Material, Content, AssetEvents, EventType, Company


class LocationSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='location_id', read_only=True)
    
    class Meta:
        model = Location
        fields = ['id', 'name', 'address', 'city', 'country', 'latitude', 'longitude', 'state']


class AssetTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetType
        fields = ['id', 'name', 'description', 'code']


class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = ['id', 'name', 'description']


class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Content
        fields = ['id', 'name', 'description']


class EventTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventType
        fields = ['id', 'name', 'description']


class AssetEventSerializer(serializers.ModelSerializer):
    type_id = serializers.IntegerField(source='event_type.id', read_only=True)
    
    class Meta:
        model = AssetEvents
        fields = [
            'event_id', 'title', 'type_id', 'start_date', 'end_date', 
            'event_status', 'description', 'performed_by', 'created_at', 'cost'
        ]


class AssetSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='asset_id', read_only=True)
    type = AssetTypeSerializer(source='asset_type', read_only=True)
    location = LocationSerializer(read_only=True)
    events = AssetEventSerializer(many=True, read_only=True)
    material_name = serializers.CharField(source='material.name', read_only=True)
    content_name = serializers.CharField(source='content.name', read_only=True)
    
    class Meta:
        model = Asset
        fields = [
            'id', 'name', 'latitude', 'longitude', 'description', 'status', 
            'model_id', 'health', 'type', 'location', 'installation_date',
            'manufactured_date', 'commission_date', 'decommission_date',
            'created_at', 'capacity', 'current_volume', 'diameter', 'height',
            'material_name', 'content_name', 'events'
        ]


class FarmAssetSerializer(serializers.ModelSerializer):
    asset_id = serializers.CharField(read_only=True)
    type = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    dates = serializers.SerializerMethodField()
    specifications = serializers.SerializerMethodField()
    events = AssetEventSerializer(many=True, read_only=True)
    
    class Meta:
        model = Asset
        fields = [
            'asset_id', 'name', 'latitude', 'longitude', 'description', 
            'status', 'type', 'location', 'dates', 'specifications', 'events'
        ]
    
    @extend_schema_field(Dict[str, Any])
    def get_type(self, obj: Asset) -> Optional[Dict[str, Any]]:
        if obj.asset_type:
            return {
                'id': obj.asset_type.id,
                'name': obj.asset_type.name,
                'description': obj.asset_type.description
            }
        return None
    
    @extend_schema_field(Dict[str, Any])
    def get_location(self, obj: Asset) -> Optional[Dict[str, Any]]:
        if obj.location:
            return {
                'id': obj.location.location_id,
                'name': obj.location.name,
                'address': obj.location.address,
                'city': obj.location.city,
                'country': obj.location.country,
                'coordinates': {
                    'latitude': obj.location.latitude,
                    'longitude': obj.location.longitude
                }
            }
        return None
    
    @extend_schema_field(Dict[str, Any])
    def get_dates(self, obj: Asset) -> Dict[str, Any]:
        return {
            'installation': obj.installation_date,
            'manufactured': obj.manufactured_date,
            'commission': obj.commission_date,
            'decommission': obj.decommission_date,
            'created': obj.created_at
        }
    
    @extend_schema_field(Dict[str, Any])
    def get_specifications(self, obj: Asset) -> Dict[str, Any]:
        return {
            'capacity': obj.capacity,
            'current_volume': obj.current_volume,
            'diameter': obj.diameter,
            'height': obj.height,
            'material': obj.material.name if obj.material else None,
            'content': obj.content.name if obj.content else None
        }


class FarmSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='farm_id', read_only=True)
    location = LocationSerializer(read_only=True)
    
    class Meta:
        model = Farm
        fields = ['id', 'company_id', 'name', 'description', 'status', 'created_at', 'location']


class AssetDetailSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='asset_id', read_only=True)
    type = serializers.SerializerMethodField()
    farm = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    dates = serializers.SerializerMethodField()
    specifications = serializers.SerializerMethodField()
    events = serializers.SerializerMethodField()
    related_assets = serializers.SerializerMethodField()
    
    class Meta:
        model = Asset
        fields = [
            'id', 'name', 'latitude', 'longitude', 'health', 'type', 
            'description', 'status', 'model_id', 'farm', 'location', 
            'dates', 'specifications', 'events', 'related_assets'
        ]
    
    @extend_schema_field(Dict[str, Any])
    def get_type(self, obj: Asset) -> Optional[Dict[str, Any]]:
        if obj.asset_type:
            return {
                'id': obj.asset_type.id,
                'name': obj.asset_type.name,
                'description': obj.asset_type.description
            }
        return None
    
    @extend_schema_field(Dict[str, Any])
    def get_farm(self, obj: Asset) -> Optional[Dict[str, Any]]:
        if obj.farm:
            return {
                'id': obj.farm.farm_id,
                'name': obj.farm.name
            }
        return None
    
    @extend_schema_field(Dict[str, Any])
    def get_location(self, obj: Asset) -> Optional[Dict[str, Any]]:
        if obj.location:
            return {
                'id': obj.location.location_id,
                'name': obj.location.name,
                'address': obj.location.address,
                'city': obj.location.city,
                'country': obj.location.country,
                'coordinates': {
                    'latitude': obj.location.latitude,
                    'longitude': obj.location.longitude
                }
            }
        return None
    
    @extend_schema_field(Dict[str, Any])
    def get_dates(self, obj: Asset) -> Dict[str, Any]:
        return {
            'installation': obj.installation_date,
            'manufactured': obj.manufactured_date,
            'commission': obj.commission_date,
            'decommission': obj.decommission_date,
            'created': obj.created_at
        }
    
    @extend_schema_field(Dict[str, Any])
    def get_specifications(self, obj: Asset) -> Dict[str, Any]:
        return {
            'capacity': obj.capacity,
            'current_volume': obj.current_volume,
            'diameter': obj.diameter,
            'height': obj.height,
            'material': obj.material.name if obj.material else None,
            'content': obj.content.name if obj.content else None
        }
    
    @extend_schema_field(List[Dict[str, Any]])
    def get_events(self, obj: Asset) -> List[Dict[str, Any]]:
        events = []
        for event in obj.events.all():
            events.append({
                'id': event.event_id,
                'type_id': event.event_type.id if event.event_type else None,
                'status': event.event_status,
                'start_date': event.start_date,
                'end_date': event.end_date,
                'description': event.description,
                'performed_by': event.performed_by,
                'created_at': event.created_at
            })
        return events
    
    @extend_schema_field(List[Dict[str, Any]])
    def get_related_assets(self, obj: Asset) -> List[Dict[str, Any]]:
        # For now return empty list - implement AssetRelationship model if needed
        return []