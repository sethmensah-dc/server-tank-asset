from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.management import call_command
from django import forms
from django.http import HttpResponse
import zipfile
import os
import tempfile

from .models import Asset, AssetType, Content, Farm, Location, Material, AssetEvents, Company, EventType


class CsvImportForm(forms.Form):
    csv_file = forms.FileField(
        label='Select CSV File',
        help_text='Upload a CSV file containing asset data'
    )

class CsvDirectoryImportForm(forms.Form):
    csv_zip = forms.FileField(
        label='Upload ZIP file containing CSV files',
        help_text='Upload a ZIP file containing all CSV files (companies.csv, locations.csv, etc.)'
    )
    clear_existing = forms.BooleanField(
        required=False,
        label='Clear existing data',
        help_text='WARNING: This will delete all existing data before importing'
    )

class DataManagementForm(forms.Form):
    action = forms.ChoiceField(
        choices=[
            ('export', 'Export all data to CSV'),
            ('import', 'Import data from ZIP file')
        ],
        widget=forms.RadioSelect
    )


class AssetAdmin(admin.ModelAdmin):
    list_display = ['asset_id', 'name', 'asset_type', 'status', 'farm', 'location']
    list_filter = ['status', 'asset_type', 'farm']
    search_fields = ['asset_id', 'name', 'description']
    list_per_page = 50
    
    fields = ['asset_id', 'company_id', 'location', 'farm', 'name', 'asset_type', 'description',
              'installation_date', 'manufactured_date', 'commission_date', 'decommission_date', 
              'status', 'latitude', 'longitude', 'health',
              'capacity', 'model_id', 'current_volume', 'diameter', 'height',
              'material', 'content']
    readonly_fields = ['asset_id']

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'upload-csv/',
                self.admin_site.admin_view(self.upload_csv),
                name='core_asset_upload_csv',
            ),
            path(
                'data-management/',
                self.admin_site.admin_view(self.data_management),
                name='core_asset_data_management',
            ),
            path(
                'debug-production/',
                self.admin_site.admin_view(self.debug_production),
                name='core_asset_debug_production',
            ),
        ]
        return custom_urls + urls

    def upload_csv(self, request):
        if request.method == "POST":
            form = CsvImportForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = request.FILES["csv_file"]
                
                # Validate file type
                if not csv_file.name.endswith('.csv'):
                    messages.error(request, 'File must be a CSV file.')
                    return redirect("admin:core_asset_upload_csv")
                
                # Save uploaded file temporarily
                file_path = f'/tmp/{csv_file.name}'
                with open(file_path, 'wb+') as destination:
                    for chunk in csv_file.chunks():
                        destination.write(chunk)
                
                try:
                    # Call the management command to import CSV
                    call_command('import_csv_assets', csv_file=file_path)
                    messages.success(
                        request, 
                        f'Successfully imported assets from {csv_file.name}'
                    )
                except Exception as e:
                    messages.error(request, f'Error importing CSV: {str(e)}')
                
                return redirect("admin:core_asset_changelist")
        else:
            form = CsvImportForm()
        
        payload = {"form": form}
        return render(request, "admin/csv_form.html", payload)

    def data_management(self, request):
        if request.method == "POST":
            if 'export' in request.POST:
                return self.export_all_data(request)
            elif 'import' in request.POST:
                return self.import_csv_data(request)
        
        context = {
            'title': 'Data Management',
            'export_form': DataManagementForm(),
            'import_form': CsvDirectoryImportForm()
        }
        return render(request, "admin/data_management.html", context)

    def export_all_data(self, request):
        """Export all data to a ZIP file containing CSV files"""
        try:
            # Create temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                # Export data to CSV files
                call_command('export_to_csv', output_dir=temp_dir)
                
                # Create ZIP file
                zip_filename = 'tank_asset_data_export.zip'
                response = HttpResponse(content_type='application/zip')
                response['Content-Disposition'] = f'attachment; filename="{zip_filename}"'
                
                with zipfile.ZipFile(response, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    for filename in os.listdir(temp_dir):
                        if filename.endswith('.csv'):
                            file_path = os.path.join(temp_dir, filename)
                            zip_file.write(file_path, filename)
                
                messages.success(request, 'Data exported successfully!')
                return response
                
        except Exception as e:
            messages.error(request, f'Error exporting data: {str(e)}')
            return redirect("admin:core_asset_data_management")

    def import_csv_data(self, request):
        """Import data from uploaded ZIP file"""
        form = CsvDirectoryImportForm(request.POST, request.FILES)
        if form.is_valid():
            csv_zip = request.FILES["csv_zip"]
            clear_existing = form.cleaned_data['clear_existing']
            
            # Validate file type
            if not csv_zip.name.endswith('.zip'):
                messages.error(request, 'File must be a ZIP file.')
                return redirect("admin:core_asset_data_management")
            
            try:
                # Create temporary directory
                with tempfile.TemporaryDirectory() as temp_dir:
                    # Save and extract ZIP file
                    zip_path = os.path.join(temp_dir, 'upload.zip')
                    with open(zip_path, 'wb+') as destination:
                        for chunk in csv_zip.chunks():
                            destination.write(chunk)
                    
                    # Extract ZIP file
                    extract_dir = os.path.join(temp_dir, 'extracted')
                    with zipfile.ZipFile(zip_path, 'r') as zip_file:
                        zip_file.extractall(extract_dir)
                    
                    # Import CSV files
                    clear_flag = '--clear-existing' if clear_existing else ''
                    if clear_flag:
                        call_command('import_from_csv', csv_dir=extract_dir, clear_existing=True)
                    else:
                        call_command('import_from_csv', csv_dir=extract_dir)
                    
                    messages.success(
                        request, 
                        f'Successfully imported data from {csv_zip.name}'
                    )
                    
            except Exception as e:
                messages.error(request, f'Error importing data: {str(e)}')
        
        return redirect("admin:core_asset_data_management")

    def debug_production(self, request):
        """Debug production environment issues"""
        import traceback
        from django.db import connection
        
        debug_results = []
        
        # Test 1: Database Connection
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM core_company")
                count = cursor.fetchone()[0]
                debug_results.append(('✅ Database Connection', f'Companies: {count}'))
        except Exception as e:
            debug_results.append(('❌ Database Connection', str(e)))
        
        # Test 2: File Permissions
        try:
            import tempfile
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            temp_file.write(b'test')
            temp_file.close()
            os.unlink(temp_file.name)
            debug_results.append(('✅ File Permissions', 'Can create temp files'))
        except Exception as e:
            debug_results.append(('❌ File Permissions', str(e)))
        
        # Test 3: Settings Check
        try:
            from django.conf import settings
            file_limit = getattr(settings, 'FILE_UPLOAD_MAX_MEMORY_SIZE', 'Not set')
            debug_results.append(('📊 Upload Limit', f'{file_limit} bytes'))
        except Exception as e:
            debug_results.append(('❌ Settings Check', str(e)))
        
        # Test 4: Import Command Test
        try:
            from django.core.management import call_command
            debug_results.append(('✅ Import Command', 'Available'))
        except Exception as e:
            debug_results.append(('❌ Import Command', str(e)))
        
        context = {
            'title': 'Production Debug Report',
            'debug_results': debug_results
        }
        return render(request, "admin/debug_production.html", context)


class FarmAdmin(admin.ModelAdmin):
    list_display = ['farm_id', 'name', 'company_id', 'status', 'location']
    list_filter = ['status', 'company_id']
    search_fields = ['farm_id', 'name', 'description']
    
    fields = ['farm_id', 'company_id', 'location', 'name', 'description', 'status', 'operational_since']
    readonly_fields = ['farm_id']


class LocationAdmin(admin.ModelAdmin):
    list_display = ['location_id', 'name', 'city', 'country', 'latitude', 'longitude']
    list_filter = ['country', 'city']
    search_fields = ['name', 'city', 'address']


class AssetTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description', 'code']
    search_fields = ['name', 'description', 'code']


class MaterialAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description']
    search_fields = ['name', 'description']


class ContentAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description']
    search_fields = ['name', 'description']


class AssetEventsAdmin(admin.ModelAdmin):
    list_display = ['event_id', 'asset', 'event_type', 'event_status', 'start_date', 'end_date']
    list_filter = ['event_status', 'event_type', 'start_date']
    search_fields = ['event_id', 'description', 'performed_by']


class CompanyAdmin(admin.ModelAdmin):
    list_display = ['company_id', 'name', 'industry', 'created_at']
    list_filter = ['industry']
    search_fields = ['company_id', 'name', 'industry']


class EventTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description']
    search_fields = ['name', 'description']




# Register models with custom admin
admin.site.register(Asset, AssetAdmin)
admin.site.register(Farm, FarmAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(AssetType, AssetTypeAdmin)
admin.site.register(Material, MaterialAdmin)
admin.site.register(Content, ContentAdmin)
admin.site.register(AssetEvents, AssetEventsAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(EventType, EventTypeAdmin)

# Customize admin site
admin.site.site_header = "Tank Asset Management"
admin.site.site_title = "Tank Asset Admin"
admin.site.index_title = "Welcome to Tank Asset Management"
