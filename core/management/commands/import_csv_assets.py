import csv
import os
from datetime import datetime
from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import Company, Location, Farm, AssetType, Material, Content, Asset


class Command(BaseCommand):
    help = 'Import assets from CSV file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--csv-file',
            type=str,
            required=True,
            help='Path to CSV file to import'
        )
        parser.add_argument(
            '--update-existing',
            action='store_true',
            help='Update existing assets if they already exist'
        )

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']
        
        if not os.path.exists(csv_file_path):
            self.stdout.write(
                self.style.ERROR(f'CSV file not found at: {csv_file_path}')
            )
            return

        try:
            with transaction.atomic():
                imported_count = self.import_assets(csv_file_path, options['update_existing'])
                
            self.stdout.write(
                self.style.SUCCESS(f'Successfully imported {imported_count} assets from CSV!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Import failed: {str(e)}')
            )

    def parse_date(self, date_str):
        """Parse date string in various formats"""
        if not date_str or date_str.strip() == '':
            return None
            
        # Try different date formats
        date_formats = [
            '%m/%d/%Y',  # 5/22/2024
            '%Y-%m-%d',  # 2024-05-22
            '%m-%d-%Y',  # 05-22-2024
            '%d/%m/%Y',  # 22/05/2024
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt).date()
            except ValueError:
                continue
        
        self.stdout.write(f'Warning: Could not parse date: {date_str}')
        return None

    def parse_datetime(self, datetime_str):
        """Parse datetime string"""
        if not datetime_str or datetime_str.strip() == '':
            return None
            
        # Handle the weird format in the CSV like "45:23.0"
        if ':' in datetime_str and '.' in datetime_str:
            return datetime.now()  # Use current time as fallback
            
        return None

    def import_assets(self, csv_file_path, update_existing):
        imported_count = 0
        
        with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                try:
                    # Skip rows with empty asset_id
                    if not row.get('asset_id', '').strip():
                        continue
                    
                    asset_id = row['asset_id'].strip()
                    
                    # Check if asset already exists
                    existing_asset = Asset.objects.filter(asset_id=asset_id).first()
                    if existing_asset and not update_existing:
                        self.stdout.write(f'Asset {asset_id} already exists, skipping...')
                        continue
                    
                    # Get or create related objects
                    company = self.get_or_create_company(row)
                    location = self.get_or_create_location(row)
                    farm = self.get_or_create_farm(row, company, location)
                    asset_type = self.get_or_create_asset_type(row)
                    material = self.get_or_create_material(row)
                    content = self.get_or_create_content(row)
                    
                    # Parse dates
                    installation_date = self.parse_date(row.get('installation_date', ''))
                    manufactured_date = self.parse_date(row.get('manufactured_date', ''))
                    commission_date = self.parse_date(row.get('commission_date', ''))
                    decommission_date = self.parse_date(row.get('decommission_date', ''))
                    created_at = self.parse_datetime(row.get('created_at', ''))
                    
                    # Create or update asset
                    asset_data = {
                        'company_id': company.company_id if company else row.get('company_id', ''),
                        'location': location,
                        'farm': farm,
                        'name': row.get('name', '').strip(),
                        'asset_type': asset_type,
                        'description': row.get('description', '').strip(),
                        'installation_date': installation_date,
                        'manufactured_date': manufactured_date,
                        'commission_date': commission_date,
                        'decommission_date': decommission_date,
                        'status': row.get('status', 'active').strip(),
                        'created_at': created_at or datetime.now(),
                        'latitude': float(row['latitude']) if row.get('latitude') else None,
                        'longitude': float(row['longitude']) if row.get('longitude') else None,
                        'health': 100,  # Default health for new assets
                        'capacity': float(row['capacity']) if row.get('capacity') else None,
                        'model_id': row.get('model_id', '').strip(),
                        'current_volume': float(row['current_volume']) if row.get('current_volume') else None,
                        'diameter': float(row['diameter']) if row.get('diameter') else None,
                        'height': float(row['height']) if row.get('height') else None,
                        'material': material,
                        'content': content,
                    }
                    
                    if existing_asset:
                        # Update existing asset
                        for key, value in asset_data.items():
                            setattr(existing_asset, key, value)
                        existing_asset.save()
                        self.stdout.write(f'Updated asset: {asset_id}')
                    else:
                        # Create new asset
                        asset_data['asset_id'] = asset_id
                        Asset.objects.create(**asset_data)
                        self.stdout.write(f'Created asset: {asset_id}')
                    
                    imported_count += 1
                    
                except Exception as e:
                    self.stdout.write(f'Error importing row {row.get("asset_id", "unknown")}: {str(e)}')
                    continue
        
        return imported_count

    def get_or_create_company(self, row):
        company_id = row.get('company_id', '').strip()
        if not company_id:
            return None
            
        company, created = Company.objects.get_or_create(
            company_id=company_id,
            defaults={
                'name': f'Company {company_id}',
                'industry': 'Oil & Gas'
            }
        )
        if created:
            self.stdout.write(f'Created company: {company_id}')
        return company

    def get_or_create_location(self, row):
        location_id = row.get('location_id', '').strip()
        if not location_id:
            return None
            
        try:
            location_id = int(location_id)
        except ValueError:
            return None
            
        location, created = Location.objects.get_or_create(
            location_id=location_id,
            defaults={
                'name': f'Location {location_id}',
                'city': 'Unknown City',
                'country': 'Unknown Country',
                'latitude': float(row['latitude']) if row.get('latitude') else None,
                'longitude': float(row['longitude']) if row.get('longitude') else None,
            }
        )
        if created:
            self.stdout.write(f'Created location: {location_id}')
        return location

    def get_or_create_farm(self, row, company, location):
        farm_id = row.get('farm_id', '').strip()
        if not farm_id:
            return None
            
        farm, created = Farm.objects.get_or_create(
            farm_id=farm_id,
            defaults={
                'company_id': company.company_id if company else row.get('company_id', ''),
                'location': location,
                'name': f'Farm {farm_id}',
                'description': f'Auto-created farm for {farm_id}',
                'status': 'active'
            }
        )
        if created:
            self.stdout.write(f'Created farm: {farm_id}')
        return farm

    def get_or_create_asset_type(self, row):
        asset_type_id = row.get('asset_type_id', '').strip()
        if not asset_type_id:
            return None
            
        try:
            asset_type_id = int(asset_type_id)
        except ValueError:
            return None
            
        asset_type, created = AssetType.objects.get_or_create(
            id=asset_type_id,
            defaults={
                'name': 'Compressor',  # Based on the CSV data
                'description': 'Gas compression system'
            }
        )
        if created:
            self.stdout.write(f'Created asset type: {asset_type_id}')
        return asset_type

    def get_or_create_material(self, row):
        material_id = row.get('material_id', '').strip()
        if not material_id:
            return None
            
        try:
            material_id = int(material_id)
        except ValueError:
            return None
            
        material, created = Material.objects.get_or_create(
            id=material_id,
            defaults={
                'name': f'Material {material_id}',
                'description': 'Auto-created material'
            }
        )
        if created:
            self.stdout.write(f'Created material: {material_id}')
        return material

    def get_or_create_content(self, row):
        content_id = row.get('content_id', '').strip()
        if not content_id:
            return None
            
        try:
            content_id = int(content_id)
        except ValueError:
            return None
            
        content, created = Content.objects.get_or_create(
            id=content_id,
            defaults={
                'name': f'Content {content_id}',
                'description': 'Auto-created content'
            }
        )
        if created:
            self.stdout.write(f'Created content: {content_id}')
        return content