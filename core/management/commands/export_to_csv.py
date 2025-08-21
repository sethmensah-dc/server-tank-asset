#!/usr/bin/env python3
"""
Django management command to export all data to CSV files for production import
Usage: python manage.py export_to_csv --output-dir /path/to/output/
"""

import os
import csv
from django.core.management.base import BaseCommand
from core.models import (
    Company, Location, AssetType, Material, Content, 
    Farm, Asset, EventType, AssetEvents
)


class Command(BaseCommand):
    help = 'Export all Django data to CSV files for production import'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output-dir',
            type=str,
            default='./csv_exports',
            help='Directory to save CSV files'
        )

    def handle(self, *args, **options):
        output_dir = options['output_dir']
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        self.stdout.write(f'Exporting data to: {output_dir}')
        
        # Export each model
        self.export_companies(output_dir)
        self.export_locations(output_dir)
        self.export_asset_types(output_dir)
        self.export_materials(output_dir)
        self.export_contents(output_dir)
        self.export_event_types(output_dir)
        self.export_farms(output_dir)
        self.export_assets(output_dir)
        self.export_asset_events(output_dir)
        
        self.stdout.write(
            self.style.SUCCESS('Successfully exported all data to CSV files!')
        )

    def export_companies(self, output_dir):
        filename = os.path.join(output_dir, 'companies.csv')
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Header
            writer.writerow([
                'company_id', 'name', 'logo', 'industry', 'location_id', 
                'established_date', 'created_at'
            ])
            
            # Data
            for company in Company.objects.all():
                writer.writerow([
                    company.company_id,
                    company.name,
                    company.logo,
                    company.industry,
                    company.location_id,
                    company.established_date.strftime('%Y-%m-%d') if company.established_date else '',
                    company.created_at.strftime('%Y-%m-%d %H:%M:%S') if company.created_at else ''
                ])
        
        self.stdout.write(f'Exported {Company.objects.count()} companies to companies.csv')

    def export_locations(self, output_dir):
        filename = os.path.join(output_dir, 'locations.csv')
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Header
            writer.writerow([
                'location_id', 'name', 'address', 'city', 'state', 'zip_code',
                'country', 'latitude', 'longitude', 'created_at'
            ])
            
            # Data
            for location in Location.objects.all():
                writer.writerow([
                    location.location_id,
                    location.name,
                    location.address,
                    location.city,
                    location.state,
                    location.zip_code,
                    location.country,
                    location.latitude,
                    location.longitude,
                    location.created_at.strftime('%Y-%m-%d %H:%M:%S') if location.created_at else ''
                ])
        
        self.stdout.write(f'Exported {Location.objects.count()} locations to locations.csv')

    def export_asset_types(self, output_dir):
        filename = os.path.join(output_dir, 'asset_types.csv')
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Header
            writer.writerow(['id', 'name', 'description', 'code'])
            
            # Data
            for asset_type in AssetType.objects.all():
                writer.writerow([
                    asset_type.id,
                    asset_type.name,
                    asset_type.description,
                    asset_type.code
                ])
        
        self.stdout.write(f'Exported {AssetType.objects.count()} asset types to asset_types.csv')

    def export_materials(self, output_dir):
        filename = os.path.join(output_dir, 'materials.csv')
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Header
            writer.writerow(['id', 'name', 'description'])
            
            # Data
            for material in Material.objects.all():
                writer.writerow([
                    material.id,
                    material.name,
                    material.description
                ])
        
        self.stdout.write(f'Exported {Material.objects.count()} materials to materials.csv')

    def export_contents(self, output_dir):
        filename = os.path.join(output_dir, 'contents.csv')
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Header
            writer.writerow(['id', 'name', 'description'])
            
            # Data
            for content in Content.objects.all():
                writer.writerow([
                    content.id,
                    content.name,
                    content.description
                ])
        
        self.stdout.write(f'Exported {Content.objects.count()} contents to contents.csv')

    def export_event_types(self, output_dir):
        filename = os.path.join(output_dir, 'event_types.csv')
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Header
            writer.writerow(['id', 'name', 'description'])
            
            # Data
            for event_type in EventType.objects.all():
                writer.writerow([
                    event_type.id,
                    event_type.name,
                    event_type.description
                ])
        
        self.stdout.write(f'Exported {EventType.objects.count()} event types to event_types.csv')

    def export_farms(self, output_dir):
        filename = os.path.join(output_dir, 'farms.csv')
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Header
            writer.writerow([
                'farm_id', 'company_id', 'location_id', 'name', 'description',
                'status', 'created_at', 'operational_since'
            ])
            
            # Data
            for farm in Farm.objects.all():
                writer.writerow([
                    farm.farm_id,
                    farm.company_id,
                    farm.location.location_id if farm.location else '',
                    farm.name,
                    farm.description,
                    farm.status,
                    farm.created_at.strftime('%Y-%m-%d %H:%M:%S') if farm.created_at else '',
                    farm.operational_since.strftime('%Y-%m-%d') if farm.operational_since else ''
                ])
        
        self.stdout.write(f'Exported {Farm.objects.count()} farms to farms.csv')

    def export_assets(self, output_dir):
        filename = os.path.join(output_dir, 'assets.csv')
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Header
            writer.writerow([
                'asset_id', 'company_id', 'location_id', 'farm_id', 'name',
                'asset_type_id', 'description', 'installation_date', 'manufactured_date',
                'commission_date', 'decommission_date', 'status', 'created_at',
                'latitude', 'longitude', 'health', 'capacity', 'model_id',
                'current_volume', 'diameter', 'height', 'material_id', 'content_id'
            ])
            
            # Data
            for asset in Asset.objects.all():
                writer.writerow([
                    asset.asset_id,
                    asset.company_id,
                    asset.location.location_id if asset.location else '',
                    asset.farm.farm_id if asset.farm else '',
                    asset.name,
                    asset.asset_type.id if asset.asset_type else '',
                    asset.description,
                    asset.installation_date.strftime('%Y-%m-%d %H:%M:%S') if asset.installation_date else '',
                    asset.manufactured_date.strftime('%Y-%m-%d %H:%M:%S') if asset.manufactured_date else '',
                    asset.commission_date.strftime('%Y-%m-%d %H:%M:%S') if asset.commission_date else '',
                    asset.decommission_date.strftime('%Y-%m-%d %H:%M:%S') if asset.decommission_date else '',
                    asset.status,
                    asset.created_at.strftime('%Y-%m-%d %H:%M:%S') if asset.created_at else '',
                    asset.latitude or '',
                    asset.longitude or '',
                    asset.health or '',
                    asset.capacity or '',
                    asset.model_id or '',
                    asset.current_volume or '',
                    asset.diameter or '',
                    asset.height or '',
                    asset.material.id if asset.material else '',
                    asset.content.id if asset.content else ''
                ])
        
        self.stdout.write(f'Exported {Asset.objects.count()} assets to assets.csv')

    def export_asset_events(self, output_dir):
        filename = os.path.join(output_dir, 'asset_events.csv')
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Header
            writer.writerow([
                'event_id', 'asset_id', 'title', 'event_type_id', 'start_date',
                'end_date', 'event_status', 'description', 'performed_by', 
                'created_at', 'cost'
            ])
            
            # Data
            for event in AssetEvents.objects.all():
                writer.writerow([
                    event.event_id,
                    event.asset.asset_id if event.asset else '',
                    event.title,
                    event.event_type.id if event.event_type else '',
                    event.start_date.strftime('%Y-%m-%d %H:%M:%S') if event.start_date else '',
                    event.end_date.strftime('%Y-%m-%d %H:%M:%S') if event.end_date else '',
                    event.event_status,
                    event.description,
                    event.performed_by,
                    event.created_at.strftime('%Y-%m-%d %H:%M:%S') if event.created_at else '',
                    event.cost
                ])
        
        self.stdout.write(f'Exported {AssetEvents.objects.count()} asset events to asset_events.csv')