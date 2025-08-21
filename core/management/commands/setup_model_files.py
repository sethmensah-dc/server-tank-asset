#!/usr/bin/env python3
"""
Django management command to set up 3D model files for production
Usage: python manage.py setup_model_files
"""

import os
import shutil
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Set up 3D model files for production environment'

    def add_arguments(self, parser):
        parser.add_argument(
            '--source-dir',
            type=str,
            default='/home/iamcerebrocerberus/Dev/Workspace/DigiCoast/tank-asset/static/uploads/model_categories',
            help='Source directory containing model files'
        )

    def handle(self, *args, **options):
        source_dir = options['source_dir']
        
        # Create target directories
        static_target = os.path.join(settings.BASE_DIR, 'static', 'uploads', 'model_categories')
        media_target = os.path.join(settings.BASE_DIR, 'media', 'model_categories')
        
        os.makedirs(static_target, exist_ok=True)
        os.makedirs(media_target, exist_ok=True)
        
        self.stdout.write(f'Source directory: {source_dir}')
        self.stdout.write(f'Static target: {static_target}')
        self.stdout.write(f'Media target: {media_target}')
        
        if not os.path.exists(source_dir):
            self.stdout.write(
                self.style.ERROR(f'Source directory not found: {source_dir}')
            )
            return
        
        # Copy .glb files
        copied_files = []
        for filename in os.listdir(source_dir):
            if filename.endswith('.glb'):
                source_file = os.path.join(source_dir, filename)
                
                # Copy to media directory (for file field uploads)
                media_dest = os.path.join(media_target, filename)
                if not os.path.exists(media_dest):
                    shutil.copy2(source_file, media_dest)
                
                # Static files are already in place
                
                copied_files.append(filename)
                self.stdout.write(f'Copied: {filename}')
        
        if copied_files:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully copied {len(copied_files)} model files')
            )
            
            # Show instructions
            self.stdout.write('\n' + '='*60)
            self.stdout.write('PRODUCTION SETUP INSTRUCTIONS:')
            self.stdout.write('='*60)
            self.stdout.write('')
            self.stdout.write('1. DATA MIGRATION:')
            self.stdout.write('   - Upload production_data_export.zip to production server')
            self.stdout.write('   - Use Django admin Data Management to import the ZIP file')
            self.stdout.write('')
            self.stdout.write('2. MODEL FILES:')
            self.stdout.write('   - Copy these files to production:')
            for filename in copied_files:
                self.stdout.write(f'     • {filename}')
            self.stdout.write('')
            self.stdout.write('   - Place them in both:')
            self.stdout.write('     • /path/to/production/static/uploads/model_categories/')
            self.stdout.write('     • /path/to/production/media/model_categories/')
            self.stdout.write('')
            self.stdout.write('3. VERIFY ENDPOINTS:')
            self.stdout.write('   - GET /api/asset-model/Compressor')
            self.stdout.write('   - GET /api/asset-model/FixedRoofTank')
            self.stdout.write('   - GET /api/asset-model/HeatExchanger')
            self.stdout.write('   - GET /api/asset/SYS-1D3407DB-F-13083-A-06527')
            self.stdout.write('')
            self.stdout.write('4. COLLECTSTATIC:')
            self.stdout.write('   - Run: python manage.py collectstatic')
            self.stdout.write('')
            
        else:
            self.stdout.write(
                self.style.WARNING('No .glb files found to copy')
            )