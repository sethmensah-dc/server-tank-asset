import sqlite3
import os
from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import Company, Location, Farm, AssetType, Material, Content, EventType, Asset, AssetEvents


class Command(BaseCommand):
    help = 'Migrate data from Flask SQLite database to Django'

    def add_arguments(self, parser):
        parser.add_argument(
            '--flask-db',
            type=str,
            default='/home/iamcerebrocerberus/Dev/Workspace/DigiCoast/tank-asset/main_app (2)/main_app/instance/asset_warehouse_now.db',
            help='Path to Flask SQLite database'
        )
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Clear existing Django data before migration'
        )

    def handle(self, *args, **options):
        flask_db_path = options['flask_db']
        
        if not os.path.exists(flask_db_path):
            self.stdout.write(
                self.style.ERROR(f'Flask database not found at: {flask_db_path}')
            )
            return

        if options['clear_existing']:
            self.stdout.write('Clearing existing Django data...')
            with transaction.atomic():
                AssetEvents.objects.all().delete()
                Asset.objects.all().delete()
                Farm.objects.all().delete()
                Location.objects.all().delete()
                Company.objects.all().delete()
                AssetType.objects.all().delete()
                Material.objects.all().delete()
                Content.objects.all().delete()
                EventType.objects.all().delete()

        conn = sqlite3.connect(flask_db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            with transaction.atomic():
                self.migrate_companies(cursor)
                self.migrate_locations(cursor)
                self.migrate_farms(cursor)
                self.migrate_asset_types(cursor)
                self.migrate_materials(cursor)
                self.migrate_contents(cursor)
                self.migrate_event_types(cursor)
                self.migrate_assets(cursor)
                self.migrate_asset_events(cursor)

            self.stdout.write(
                self.style.SUCCESS('Successfully migrated Flask data to Django!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Migration failed: {str(e)}')
            )
        finally:
            conn.close()

    def migrate_companies(self, cursor):
        self.stdout.write('Migrating companies...')
        cursor.execute('SELECT * FROM companies')
        for row in cursor.fetchall():
            Company.objects.update_or_create(
                company_id=row['company_id'],
                defaults={
                    'name': row['name'],
                    'logo': row['logo'] or '',
                    'industry': row['industry'] or '',
                    'location_id': row['location_id'] or '',
                    'established_date': row['established_date'],
                    'created_at': row['created_at']
                }
            )
        self.stdout.write(f'Migrated {Company.objects.count()} companies')

    def migrate_locations(self, cursor):
        self.stdout.write('Migrating locations...')
        cursor.execute('SELECT * FROM locations')
        for row in cursor.fetchall():
            Location.objects.update_or_create(
                location_id=row['location_id'],
                defaults={
                    'name': row['name'],
                    'address': row['address'] or '',
                    'city': row['city'] or '',
                    'state': row['state'] or '',
                    'zip_code': row['zip_code'] or '',
                    'country': row['country'] or '',
                    'latitude': row['latitude'],
                    'longitude': row['longitude'],
                    'created_at': row['created_at']
                }
            )
        self.stdout.write(f'Migrated {Location.objects.count()} locations')

    def migrate_farms(self, cursor):
        self.stdout.write('Migrating farms...')
        cursor.execute('SELECT * FROM farms')
        for row in cursor.fetchall():
            location = None
            if row['location_id']:
                try:
                    location = Location.objects.get(location_id=row['location_id'])
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
                    'created_at': row['created_at'],
                    'operational_since': row['operational_since']
                }
            )
        self.stdout.write(f'Migrated {Farm.objects.count()} farms')

    def migrate_asset_types(self, cursor):
        self.stdout.write('Migrating asset types...')
        cursor.execute('SELECT * FROM asset_types')
        for row in cursor.fetchall():
            AssetType.objects.update_or_create(
                id=row['id'],
                defaults={
                    'name': row['name'],
                    'description': row['description'] or '',
                    'code': row['code'] or ''
                }
            )
        self.stdout.write(f'Migrated {AssetType.objects.count()} asset types')

    def migrate_materials(self, cursor):
        self.stdout.write('Migrating materials...')
        cursor.execute('SELECT * FROM materials')
        for row in cursor.fetchall():
            Material.objects.update_or_create(
                id=row['id'],
                defaults={
                    'name': row['name'],
                    'description': row['description'] or ''
                }
            )
        self.stdout.write(f'Migrated {Material.objects.count()} materials')

    def migrate_contents(self, cursor):
        self.stdout.write('Migrating contents...')
        cursor.execute('SELECT * FROM contents')
        for row in cursor.fetchall():
            Content.objects.update_or_create(
                id=row['id'],
                defaults={
                    'name': row['name'],
                    'description': row['description'] or ''
                }
            )
        self.stdout.write(f'Migrated {Content.objects.count()} contents')

    def migrate_event_types(self, cursor):
        self.stdout.write('Migrating event types...')
        cursor.execute('SELECT * FROM event_types')
        for row in cursor.fetchall():
            EventType.objects.update_or_create(
                id=row['id'],
                defaults={
                    'name': row['name'],
                    'description': row['description'] or ''
                }
            )
        self.stdout.write(f'Migrated {EventType.objects.count()} event types')

    def migrate_assets(self, cursor):
        self.stdout.write('Migrating assets...')
        cursor.execute('SELECT * FROM assets')
        for row in cursor.fetchall():
            try:
                # Get related objects
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

                # Handle missing health field - generate random value
                from random import randint
                health_value = randint(0, 100)

                Asset.objects.update_or_create(
                    asset_id=row['asset_id'],
                    defaults={
                        'company_id': row['company_id'],
                        'location': location,
                        'farm': farm,
                        'name': row['name'],
                        'asset_type': asset_type,
                        'description': row['description'] or '',
                        'installation_date': row['installation_date'],
                        'manufactured_date': row['manufactured_date'],
                        'commission_date': row['commission_date'],
                        'decommission_date': row['decommission_date'],
                        'status': row['status'],
                        'created_at': row['created_at'],
                        'latitude': row['latitude'],
                        'longitude': row['longitude'],
                        'health': health_value,
                        'capacity': row['capacity'],
                        'model_id': row['model_id'] or '',
                        'current_volume': row['current_volume'],
                        'diameter': row['diameter'],
                        'height': row['height'],
                        'material': material,
                        'content': content
                    }
                )
            except Exception as e:
                self.stdout.write(f'Error migrating asset {row["asset_id"]}: {str(e)}')
                continue
                
        self.stdout.write(f'Migrated {Asset.objects.count()} assets')

    def migrate_asset_events(self, cursor):
        self.stdout.write('Migrating asset events...')
        cursor.execute('SELECT * FROM asset_events')
        for row in cursor.fetchall():
            try:
                asset = Asset.objects.get(asset_id=row['asset_id'])
            except Asset.DoesNotExist:
                continue

            event_type = None
            if row['event_type_id']:
                try:
                    event_type = EventType.objects.get(id=row['event_type_id'])
                except EventType.DoesNotExist:
                    pass

            AssetEvents.objects.update_or_create(
                event_id=row['event_id'],
                defaults={
                    'asset': asset,
                    'title': row['title'] or '',
                    'event_type': event_type,
                    'start_date': row['start_date'],
                    'end_date': row['end_date'],
                    'event_status': row['event_status'] or '',
                    'description': row['description'] or '',
                    'performed_by': row['performed_by'] or '',
                    'created_at': row['created_at'],
                    'cost': row['cost'] or ''
                }
            )
        self.stdout.write(f'Migrated {AssetEvents.objects.count()} asset events')