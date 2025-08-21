from django.contrib import admin

from .models import Asset, AssetType, Content, Farm, Location, Material, AssetEvents

admin.site.register(Asset)
admin.site.register(AssetType)
admin.site.register(Content)
admin.site.register(Farm)
admin.site.register(Location)
admin.site.register(Material)
admin.site.register(AssetEvents)
