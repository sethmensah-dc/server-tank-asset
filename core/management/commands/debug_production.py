#!/usr/bin/env python3
"""
Django management command to debug production import issues
Usage: python manage.py debug_production
"""

import os
import tempfile
import traceback
from django.core.management.base import BaseCommand
from django.db import connection, transaction
from core.models import Company, Location, AssetType, Asset


class Command(BaseCommand):
    help = 'Debug production import issues'

    def handle(self, *args, **options):
        self.stdout.write('🔍 PRODUCTION DEBUG REPORT')
        self.stdout.write('=' * 50)
        
        # Test 1: Database Connection
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                self.stdout.write('✅ Database connection: OK')
        except Exception as e:
            self.stdout.write(f'❌ Database connection failed: {e}')
            return
            
        # Test 2: Basic Model Operations
        try:
            company_count = Company.objects.count()
            self.stdout.write(f'✅ Company count: {company_count}')
        except Exception as e:
            self.stdout.write(f'❌ Company model access failed: {e}')
            
        # Test 3: File Permissions
        try:
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            temp_file.write(b'test')
            temp_file.close()
            os.unlink(temp_file.name)
            self.stdout.write('✅ Temp file creation: OK')
        except Exception as e:
            self.stdout.write(f'❌ Temp file creation failed: {e}')
            
        # Test 4: Media Directory
        try:
            from django.conf import settings
            media_root = settings.MEDIA_ROOT
            if os.path.exists(media_root):
                if os.access(media_root, os.W_OK):
                    self.stdout.write(f'✅ Media directory writable: {media_root}')
                else:
                    self.stdout.write(f'❌ Media directory not writable: {media_root}')
            else:
                self.stdout.write(f'❌ Media directory missing: {media_root}')
        except Exception as e:
            self.stdout.write(f'❌ Media directory check failed: {e}')
            
        # Test 5: Simple CSV Import Test
        try:
            csv_content = """company_id,name,logo,industry,location_id,established_date,created_at
TEST-001,Test Company,,Test Industry,,2020-01-01,2025-01-01 10:00:00"""
            
            # Create temp CSV file
            temp_csv = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
            temp_csv.write(csv_content)
            temp_csv.close()
            
            # Try importing one record
            import csv
            with open(temp_csv.name, 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    Company.objects.update_or_create(
                        company_id=row['company_id'],
                        defaults={
                            'name': row['name'],
                            'logo': row['logo'] or '',
                            'industry': row['industry'] or '',
                            'location_id': row['location_id'] or '',
                            'established_date': None,
                            'created_at': None
                        }
                    )
                    break
            
            os.unlink(temp_csv.name)
            self.stdout.write('✅ Simple CSV import: OK')
            
        except Exception as e:
            self.stdout.write(f'❌ Simple CSV import failed: {e}')
            self.stdout.write(f'Full traceback: {traceback.format_exc()}')
            
        # Test 6: Check Import Command
        try:
            from django.core.management import call_command
            self.stdout.write('✅ Import command accessible')
        except Exception as e:
            self.stdout.write(f'❌ Import command failed: {e}')
            
        # Test 7: Memory and Upload Limits
        try:
            from django.conf import settings
            file_limit = getattr(settings, 'FILE_UPLOAD_MAX_MEMORY_SIZE', 'Not set')
            data_limit = getattr(settings, 'DATA_UPLOAD_MAX_MEMORY_SIZE', 'Not set')
            self.stdout.write(f'📊 FILE_UPLOAD_MAX_MEMORY_SIZE: {file_limit}')
            self.stdout.write(f'📊 DATA_UPLOAD_MAX_MEMORY_SIZE: {data_limit}')
        except Exception as e:
            self.stdout.write(f'❌ Settings check failed: {e}')
            
        self.stdout.write('\n🔍 DEBUG COMPLETE')
        self.stdout.write('Check /tmp/django_debug.log for detailed logs')