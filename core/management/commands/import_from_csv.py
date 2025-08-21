#!/usr/bin/env python3
"""
Django management command to import data from CSV files
Usage: python manage.py import_from_csv --csv-dir /path/to/csv/files/
"""

import os
import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import (
    Company, Location, AssetType, Material, Content, 
    Farm, Asset, EventType, AssetEvents
)


class Command(BaseCommand):
    help = 'Import data from CSV files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--csv-dir',
            type=str,
            required=True,
            help='Directory containing CSV files'
        )
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Clear existing data before importing'
        )

    def handle(self, *args, **options):
        csv_dir = options['csv_dir']
        clear_existing = options['clear_existing']

        if not os.path.exists(csv_dir):
            self.stdout.write(
                self.style.ERROR(f'CSV directory not found: {csv_dir}')
            )
            return

        self.stdout.write(f'Importing data from: {csv_dir}')

        try:
            with transaction.atomic():
                if clear_existing:
                    self.clear_existing_data()
                
                # Import in dependency order
                self.import_companies(csv_dir)
                self.import_locations(csv_dir)
                self.import_asset_types(csv_dir)
                self.import_materials(csv_dir)
                self.import_contents(csv_dir)
                self.import_event_types(csv_dir)
                self.import_farms(csv_dir)
                self.import_assets(csv_dir)
                self.import_asset_events(csv_dir)
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Import failed: {str(e)}')
            )
            raise

        self.stdout.write(
            self.style.SUCCESS('Successfully imported all CSV data!')
        )

    def clear_existing_data(self):
        """Clear existing data from Django models"""
        self.stdout.write('Clearing existing data...')
        
        AssetEvents.objects.all().delete()
        Asset.objects.all().delete()
        Farm.objects.all().delete()
        EventType.objects.all().delete()
        Content.objects.all().delete()
        Material.objects.all().delete()
        AssetType.objects.all().delete()
        Location.objects.all().delete()
        Company.objects.all().delete()
        
        self.stdout.write('Existing data cleared.')

    def import_companies(self, csv_dir):
        filename = os.path.join(csv_dir, 'companies.csv')
        if not os.path.exists(filename):
            self.stdout.write('companies.csv not found, skipping...')
            return
            
        with open(filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            count = 0
            
            for row in reader:
                Company.objects.update_or_create(
                    company_id=row['company_id'],
                    defaults={
                        'name': row['name'],
                        'logo': row['logo'] or '',
                        'industry': row['industry'] or '',
                        'location_id': row['location_id'] or '',
                        'established_date': self.parse_date(row['established_date']),
                        'created_at': self.parse_datetime(row['created_at'])
                    }
                )
                count += 1
                
        self.stdout.write(f'Imported {count} companies')

    def import_locations(self, csv_dir):
        filename = os.path.join(csv_dir, 'locations.csv')
        if not os.path.exists(filename):
            self.stdout.write('locations.csv not found, skipping...')
            return
            
        with open(filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            count = 0
            
            for row in reader:
                Location.objects.update_or_create(
                    location_id=int(row['location_id']),
                    defaults={
                        'name': row['name'],
                        'address': row['address'] or '',
                        'city': row['city'] or '',
                        'state': row['state'] or '',
                        'zip_code': row['zip_code'] or '',
                        'country': row['country'] or '',
                        'latitude': float(row['latitude']) if row['latitude'] else None,
                        'longitude': float(row['longitude']) if row['longitude'] else None,
                        'created_at': self.parse_datetime(row['created_at'])
                    }
                )
                count += 1
                
        self.stdout.write(f'Imported {count} locations')

    def import_asset_types(self, csv_dir):
        filename = os.path.join(csv_dir, 'asset_types.csv')
        if not os.path.exists(filename):
            self.stdout.write('asset_types.csv not found, skipping...')
            return
            
        with open(filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            count = 0
            
            for row in reader:
                AssetType.objects.update_or_create(
                    id=int(row['id']),
                    defaults={
                        'name': row['name'],
                        'description': row['description'] or '',
                        'code': row['code'] or ''
                    }
                )
                count += 1
                
        self.stdout.write(f'Imported {count} asset types')

    def import_materials(self, csv_dir):
        filename = os.path.join(csv_dir, 'materials.csv')
        if not os.path.exists(filename):
            self.stdout.write('materials.csv not found, skipping...')
            return
            
        with open(filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            count = 0
            
            for row in reader:
                Material.objects.update_or_create(
                    id=int(row['id']),
                    defaults={
                        'name': row['name'],
                        'description': row['description'] or ''
                    }
                )
                count += 1
                
        self.stdout.write(f'Imported {count} materials')

    def import_contents(self, csv_dir):
        filename = os.path.join(csv_dir, 'contents.csv')
        if not os.path.exists(filename):
            self.stdout.write('contents.csv not found, skipping...')
            return
            
        with open(filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            count = 0
            
            for row in reader:
                Content.objects.update_or_create(
                    id=int(row['id']),
                    defaults={
                        'name': row['name'],
                        'description': row['description'] or ''
                    }
                )
                count += 1
                
        self.stdout.write(f'Imported {count} contents')

    def import_event_types(self, csv_dir):
        filename = os.path.join(csv_dir, 'event_types.csv')
        if not os.path.exists(filename):
            self.stdout.write('event_types.csv not found, skipping...')
            return
            
        with open(filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            count = 0
            
            for row in reader:
                EventType.objects.update_or_create(
                    id=int(row['id']),
                    defaults={
                        'name': row['name'],
                        'description': row['description'] or ''
                    }
                )
                count += 1
                
        self.stdout.write(f'Imported {count} event types')

    def import_farms(self, csv_dir):
        filename = os.path.join(csv_dir, 'farms.csv')
        if not os.path.exists(filename):
            self.stdout.write('farms.csv not found, skipping...')
            return
            
        with open(filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            count = 0
            
            for row in reader:
                location = None
                if row['location_id']:
                    try:
                        location = Location.objects.get(location_id=int(row['location_id']))
                    except Location.DoesNotExist:
                        pass
                        
                Farm.objects.update_or_create(
                    farm_id=row['farm_id'],
                    defaults={
                        'company_id': row['company_id'],
                        'location': location,
                        'name': row['name'],
                        'description': row['description'] or '',
                        'status': row['status'],
                        'created_at': self.parse_datetime(row['created_at']),
                        'operational_since': self.parse_date(row['operational_since'])
                    }
                )
                count += 1
                
        self.stdout.write(f'Imported {count} farms')

    def import_assets(self, csv_dir):
        filename = os.path.join(csv_dir, 'assets.csv')
        if not os.path.exists(filename):
            self.stdout.write('assets.csv not found, skipping...')
            return
            
        with open(filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            count = 0
            
            for row in reader:
                # Get related objects
                location = None
                if row['location_id']:
                    try:
                        location = Location.objects.get(location_id=int(row['location_id']))
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
                        asset_type = AssetType.objects.get(id=int(row['asset_type_id']))
                    except AssetType.DoesNotExist:
                        pass
                        
                material = None
                if row['material_id']:
                    try:
                        material = Material.objects.get(id=int(row['material_id']))
                    except Material.DoesNotExist:
                        pass
                        
                content = None
                if row['content_id']:
                    try:
                        content = Content.objects.get(id=int(row['content_id']))
                    except Content.DoesNotExist:
                        pass
                        
                Asset.objects.update_or_create(
                    asset_id=row['asset_id'],
                    defaults={
                        'company_id': row['company_id'],
                        'location': location,
                        'farm': farm,
                        'name': row['name'],
                        'asset_type': asset_type,
                        'description': row['description'] or '',
                        'installation_date': self.parse_datetime(row['installation_date']),
                        'manufactured_date': self.parse_datetime(row['manufactured_date']),
                        'commission_date': self.parse_datetime(row['commission_date']),
                        'decommission_date': self.parse_datetime(row['decommission_date']),
                        'status': row['status'],
                        'created_at': self.parse_datetime(row['created_at']),
                        'latitude': float(row['latitude']) if row['latitude'] else None,
                        'longitude': float(row['longitude']) if row['longitude'] else None,
                        'health': int(row['health']) if row['health'] else 100,
                        'capacity': float(row['capacity']) if row['capacity'] else None,
                        'model_id': row['model_id'] or '',
                        'current_volume': float(row['current_volume']) if row['current_volume'] else None,
                        'diameter': float(row['diameter']) if row['diameter'] else None,
                        'height': float(row['height']) if row['height'] else None,
                        'material': material,
                        'content': content
                    }
                )
                count += 1
                
        self.stdout.write(f'Imported {count} assets')

    def import_asset_events(self, csv_dir):
        filename = os.path.join(csv_dir, 'asset_events.csv')
        if not os.path.exists(filename):
            self.stdout.write('asset_events.csv not found, skipping...')
            return
            
        with open(filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            count = 0
            
            for row in reader:
                asset = None
                if row['asset_id']:
                    try:
                        asset = Asset.objects.get(asset_id=row['asset_id'])
                    except Asset.DoesNotExist:
                        continue
                        
                event_type = None
                if row['event_type_id']:
                    try:
                        event_type = EventType.objects.get(id=int(row['event_type_id']))
                    except EventType.DoesNotExist:
                        pass
                        
                AssetEvents.objects.update_or_create(
                    event_id=row['event_id'],
                    defaults={
                        'asset': asset,
                        'title': row['title'],
                        'event_type': event_type,
                        'start_date': self.parse_datetime(row['start_date']),
                        'end_date': self.parse_datetime(row['end_date']),
                        'event_status': row['event_status'] or '',
                        'description': row['description'] or '',
                        'performed_by': row['performed_by'] or '',
                        'created_at': self.parse_datetime(row['created_at']),
                        'cost': row['cost'] or ''
                    }
                )
                count += 1
                
        self.stdout.write(f'Imported {count} asset events')

    def parse_datetime(self, date_string):
        """Parse datetime string"""
        if not date_string or date_string == 'None' or date_string.strip() == '':
            # Return current time for required fields instead of None
            from django.utils import timezone
            return timezone.now()
            
        try:
            # Handle timezone-aware timestamps
            if '+' in date_string:
                # Remove timezone info for now (Django will handle it)
                date_string = date_string.split('+')[0]
            
            # Try different datetime formats
            for fmt in ['%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d']:
                try:
                    parsed_date = datetime.strptime(date_string, fmt)
                    # Make timezone-aware
                    from django.utils import timezone
                    if timezone.is_naive(parsed_date):
                        parsed_date = timezone.make_aware(parsed_date)
                    return parsed_date
                except ValueError:
                    continue
        except (ValueError, TypeError):
            pass
            
        # Fallback to current time for required fields
        from django.utils import timezone
        return timezone.now()

    def parse_date(self, date_string):
        """Parse date string"""
        if not date_string or date_string == 'None' or date_string.strip() == '':
            return None
            
        try:
            return datetime.strptime(date_string, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return None