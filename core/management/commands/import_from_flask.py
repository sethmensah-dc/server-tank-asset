#!/usr/bin/env python3
"""
Django management command to import data directly from Flask SQLite database
Usage: python manage.py import_from_flask --flask-db path/to/flask.db
"""

import sqlite3
from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import (
    Company, Location, AssetType, Material, Content, EventType,
    Farm, Asset, AssetEvents
)


class Command(BaseCommand):
    help = 'Import data directly from Flask SQLite database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--flask-db',
            type=str,
            required=True,
            help='Path to Flask SQLite database file'
        )
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Clear existing data before importing'
        )

    def handle(self, *args, **options):
        flask_db_path = options['flask_db']
        clear_existing = options['clear_existing']
        
        self.stdout.write('🚀 Starting Flask to Django data import...')
        
        if clear_existing:
            self.stdout.write('🗑️ Clearing existing data...')
            with transaction.atomic():
                AssetEvents.objects.all().delete()
                Asset.objects.all().delete()
                Farm.objects.all().delete()
                Company.objects.all().delete()
                Location.objects.all().delete()
                AssetType.objects.all().delete()
                Material.objects.all().delete()
                Content.objects.all().delete()
                EventType.objects.all().delete()
            self.stdout.write('✅ Existing data cleared')
        
        # Connect to Flask SQLite database
        flask_conn = sqlite3.connect(flask_db_path)
        flask_conn.row_factory = sqlite3.Row  # Access columns by name
        
        try:
            with transaction.atomic():
                self.import_companies(flask_conn)
                self.import_locations(flask_conn)
                self.import_asset_types(flask_conn)
                self.import_materials(flask_conn)
                self.import_contents(flask_conn)
                self.import_event_types(flask_conn)
                self.import_farms(flask_conn)
                self.import_assets(flask_conn)
                self.import_asset_events(flask_conn)
                
        finally:
            flask_conn.close()
        
        self.stdout.write('🎉 Import completed successfully!')

    def import_companies(self, flask_conn):
        self.stdout.write('📊 Importing companies...')
        cursor = flask_conn.execute('SELECT * FROM companies')
        
        for row in cursor:
            Company.objects.create(
                company_id=row['company_id'],
                name=row['name'],
                logo=row['logo'] or '',
                industry=row['industry'] or '',
                location_id=row['location_id'] or '',
                established_date=row['established_date'],
                created_at=row['created_at']
            )
        
        count = Company.objects.count()
        self.stdout.write(f'✅ Imported {count} companies')

    def import_locations(self, flask_conn):
        self.stdout.write('📍 Importing locations...')
        cursor = flask_conn.execute('SELECT * FROM locations')
        
        for row in cursor:
            Location.objects.create(
                location_id=row['location_id'],
                name=row['name'],
                address=row['address'] or '',
                city=row['city'] or '',
                state=row['state'] or '',
                zip_code=row['zip_code'] or '',
                country=row['country'] or '',
                latitude=row['latitude'],
                longitude=row['longitude'],
                created_at=row['created_at']
            )
        
        count = Location.objects.count()
        self.stdout.write(f'✅ Imported {count} locations')

    def import_asset_types(self, flask_conn):
        self.stdout.write('🏷️ Importing asset types...')
        cursor = flask_conn.execute('SELECT * FROM asset_types')
        
        for row in cursor:
            AssetType.objects.create(
                id=row['id'],
                name=row['name'],
                description=row['description'] or '',
                code=row['code'] or ''
            )
        
        count = AssetType.objects.count()
        self.stdout.write(f'✅ Imported {count} asset types')

    def import_materials(self, flask_conn):
        self.stdout.write('🔧 Importing materials...')
        cursor = flask_conn.execute('SELECT * FROM materials')
        
        for row in cursor:
            Material.objects.create(
                id=row['id'],
                name=row['name'],
                description=row['description'] or ''
            )
        
        count = Material.objects.count()
        self.stdout.write(f'✅ Imported {count} materials')

    def import_contents(self, flask_conn):
        self.stdout.write('🛢️ Importing contents...')
        cursor = flask_conn.execute('SELECT * FROM contents')
        
        for row in cursor:
            Content.objects.create(
                id=row['id'],
                name=row['name'],
                description=row['description'] or ''
            )
        
        count = Content.objects.count()
        self.stdout.write(f'✅ Imported {count} contents')

    def import_event_types(self, flask_conn):
        self.stdout.write('📅 Importing event types...')
        cursor = flask_conn.execute('SELECT * FROM event_types')
        
        for row in cursor:
            EventType.objects.create(
                id=row['id'],
                name=row['name'],
                description=row['description'] or ''
            )
        
        count = EventType.objects.count()
        self.stdout.write(f'✅ Imported {count} event types')

    def import_farms(self, flask_conn):
        self.stdout.write('🚜 Importing farms...')
        cursor = flask_conn.execute('SELECT * FROM farms')
        
        for row in cursor:
            # Get location if exists
            location = None
            if row['location_id']:
                try:
                    location = Location.objects.get(location_id=row['location_id'])
                except Location.DoesNotExist:
                    pass
            
            Farm.objects.create(
                farm_id=row['farm_id'],
                company_id=row['company_id'],
                location=location,
                name=row['name'],
                description=row['description'] or '',
                status=row['status'],
                created_at=row['created_at'],
                operational_since=row['operational_since']
            )
        
        count = Farm.objects.count()
        self.stdout.write(f'✅ Imported {count} farms')

    def import_assets(self, flask_conn):
        self.stdout.write('🏭 Importing assets...')
        cursor = flask_conn.execute('SELECT * FROM assets')
        
        for row in cursor:
            # Get foreign key objects
            location = None
            if row['location_id']:
                try:
                    location = Location.objects.get(location_id=row['location_id'])
                except Location.DoesNotExist:
                    pass
            
            farm = None
            if row['farm_id']:
                try:
                    farm = Farm.objects.get(farm_id=row['farm_id'])
                except Farm.DoesNotExist:
                    pass
            
            asset_type = None
            if row['asset_type_id']:
                try:
                    asset_type = AssetType.objects.get(id=row['asset_type_id'])
                except AssetType.DoesNotExist:
                    pass
            
            material = None
            if row['material_id']:
                try:
                    material = Material.objects.get(id=row['material_id'])
                except Material.DoesNotExist:
                    pass
            
            content = None
            if row['content_id']:
                try:
                    content = Content.objects.get(id=row['content_id'])
                except Content.DoesNotExist:
                    pass
            
            Asset.objects.create(
                asset_id=row['asset_id'],
                company_id=row['company_id'],
                location=location,
                farm=farm,
                name=row['name'],
                asset_type=asset_type,
                description=row['description'] or '',
                installation_date=row['installation_date'],
                manufactured_date=row['manufactured_date'],
                commission_date=row['commission_date'],
                decommission_date=row['decommission_date'],
                status=row['status'],
                created_at=row['created_at'],
                latitude=row['latitude'],
                longitude=row['longitude'],
                health=50,  # Default health value since Flask doesn't have this field
                capacity=row['capacity'],
                model_id=row['model_id'] or '',
                current_volume=row['current_volume'],
                diameter=row['diameter'],
                height=row['height'],
                material=material,
                content=content
            )
        
        count = Asset.objects.count()
        self.stdout.write(f'✅ Imported {count} assets')

    def import_asset_events(self, flask_conn):
        self.stdout.write('📋 Importing asset events...')
        cursor = flask_conn.execute('SELECT * FROM asset_events')
        
        for row in cursor:
            # Get foreign key objects
            asset = None
            if row['asset_id']:
                try:
                    asset = Asset.objects.get(asset_id=row['asset_id'])
                except Asset.DoesNotExist:
                    continue  # Skip if asset doesn't exist
            
            event_type = None
            if row['event_type_id']:
                try:
                    event_type = EventType.objects.get(id=row['event_type_id'])
                except EventType.DoesNotExist:
                    pass
            
            AssetEvents.objects.create(
                event_id=row['event_id'],
                asset=asset,
                title=row['title'] or '',
                event_type=event_type,
                start_date=row['start_date'],
                end_date=row['end_date'],
                event_status=row['event_status'] or '',
                description=row['description'] or '',
                performed_by=row['performed_by'] or '',
                created_at=row['created_at'],
                cost=row['cost'] or ''
            )
        
        count = AssetEvents.objects.count()
        self.stdout.write(f'✅ Imported {count} asset events')