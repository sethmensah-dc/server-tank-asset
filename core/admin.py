from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.management import call_command
from django import forms

from .models import Asset, AssetType, Content, Farm, Location, Material, AssetEvents, Company, EventType, AssetModel


class CsvImportForm(forms.Form):
    csv_file = forms.FileField(
        label='Select CSV File',
        help_text='Upload a CSV file containing asset data'
    )


class AssetAdmin(admin.ModelAdmin):
    list_display = ['asset_id', 'name', 'asset_type', 'status', 'farm', 'location', 'has_model_file']
    list_filter = ['status', 'asset_type', 'farm']
    search_fields = ['asset_id', 'name', 'description']
    list_per_page = 50
    
    fields = ['asset_id', 'company_id', 'location', 'farm', 'name', 'asset_type', 'description',
              'installation_date', 'manufactured_date', 'commission_date', 'decommission_date', 
              'status', 'latitude', 'longitude', 'health',
              'capacity', 'model_id', 'current_volume', 'diameter', 'height',
              'model_file', 'model_file_name', 'model_uploaded_at',
              'material', 'content']
    readonly_fields = ['asset_id', 'model_uploaded_at']
    
    def has_model_file(self, obj):
        return bool(obj.model_file)
    has_model_file.boolean = True
    has_model_file.short_description = 'Has 3D Model'
    
    def save_model(self, request, obj, form, change):
        if 'model_file' in form.changed_data and obj.model_file:
            from django.utils import timezone
            obj.model_file_name = obj.model_file.name
            obj.model_uploaded_at = timezone.now()
        super().save_model(request, obj, form, change)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'upload-csv/',
                self.admin_site.admin_view(self.upload_csv),
                name='core_asset_upload_csv',
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


class FarmAdmin(admin.ModelAdmin):
    list_display = ['farm_id', 'name', 'company_id', 'status', 'location', 'has_site_model']
    list_filter = ['status', 'company_id']
    search_fields = ['farm_id', 'name', 'description']
    
    fields = ['farm_id', 'company_id', 'location', 'name', 'description', 'status', 
              'operational_since', 'layout_pdf', 'site_model_file', 'site_model_file_name', 'site_model_uploaded_at']
    readonly_fields = ['farm_id', 'site_model_uploaded_at']
    
    def has_site_model(self, obj):
        return bool(obj.site_model_file)
    has_site_model.boolean = True
    has_site_model.short_description = 'Has Site Model'
    
    def save_model(self, request, obj, form, change):
        if 'site_model_file' in form.changed_data and obj.site_model_file:
            from django.utils import timezone
            obj.site_model_file_name = obj.site_model_file.name
            obj.site_model_uploaded_at = timezone.now()
        super().save_model(request, obj, form, change)


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


class AssetModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'asset_type', 'name', 'is_default', 'has_model_file', 'created_at']
    list_filter = ['asset_type', 'is_default', 'created_at']
    search_fields = ['name', 'asset_type__name', 'description']
    
    fields = ['asset_type', 'name', 'description', 'model_file', 'is_default']
    
    def has_model_file(self, obj):
        return bool(obj.model_file)
    has_model_file.boolean = True
    has_model_file.short_description = 'Has Model File'
    
    def save_model(self, request, obj, form, change):
        # If this is being set as default, unset other defaults for this asset type
        if obj.is_default:
            AssetModel.objects.filter(
                asset_type=obj.asset_type, 
                is_default=True
            ).exclude(id=obj.id).update(is_default=False)
        super().save_model(request, obj, form, change)


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
admin.site.register(AssetModel, AssetModelAdmin)

# Customize admin site
admin.site.site_header = "Tank Asset Management"
admin.site.site_title = "Tank Asset Admin"
admin.site.index_title = "Welcome to Tank Asset Management"
