from __future__ import annotations

import uuid
from random import randint
from django.db import models
from django.utils.timezone import now


# Serializable defaults --------------------------------------------------------

def random_health() -> int:
    """Top-level callable so migrations can serialize the default.
    Replaces `lambda: randint(0, 100)` which Django cannot serialize.
    """
    return randint(0, 100)


# --- Core reference models ----------------------------------------------------

class Company(models.Model):
    class Meta:
        db_table = "companies"

    company_id = models.CharField(max_length=200, primary_key=True, editable=False)
    name = models.CharField(max_length=100)
    logo = models.CharField(max_length=255, blank=True, null=True)
    industry = models.CharField(max_length=100, blank=True, null=True)
    location_id = models.CharField(max_length=200, blank=True, null=True)
    established_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(default=now)

    def save(self, *args, **kwargs):
        if not self.company_id:
            unique_part = str(uuid.uuid4()).split("-")[0][:8].upper()
            self.company_id = f"COMP-{unique_part}"
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class EventType(models.Model):
    class Meta:
        db_table = "event_types"

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }

    def __str__(self) -> str:
        return self.name

class Location(models.Model):
    class Meta:
        db_table = "locations"

    location_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    zip_code = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(default=now)

    def to_dict(self):
        return {
            "id": self.location_id,
            "name": self.name,
            "address": self.address,
            "city": self.city,
            "country": self.country,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "state": self.state,
        }

    def __str__(self) -> str:
        return f"{self.name} ({self.city or ''})".strip()


class AssetType(models.Model):
    class Meta:
        db_table = "asset_types"

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    code = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self) -> str:
        return self.name


class Material(models.Model):
    class Meta:
        db_table = "materials"

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return self.name


class Content(models.Model):
    class Meta:
        db_table = "contents"

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return self.name


class AssetModel(models.Model):
    """
    Generic 3D models for asset types - used as templates/placeholders
    """
    class Meta:
        db_table = "asset_models"
        unique_together = ['asset_type', 'is_default']  # Only one default per asset type
    
    id = models.AutoField(primary_key=True)
    asset_type = models.ForeignKey(
        AssetType, on_delete=models.CASCADE, related_name="models"
    )
    name = models.CharField(max_length=100, help_text="Display name (e.g., 'Standard Fixed Roof Tank')")
    model_file = models.FileField(upload_to='model_categories/', help_text="3D model file (.glb format)")
    is_default = models.BooleanField(default=False, help_text="Default model for this asset type")
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=now)
    
    def __str__(self) -> str:
        return f"{self.asset_type.name} - {self.name}"


# --- Farm + Asset domain ------------------------------------------------------

class Farm(models.Model):
    class Meta:
        db_table = "farms"

    farm_id = models.CharField(max_length=200, primary_key=True, editable=False)
    company_id = models.CharField(max_length=200)  # keep as CharField; can be FK later
    location = models.ForeignKey(
        Location, on_delete=models.SET_NULL, null=True, related_name="farms"
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50)  # active, inactive, under construction
    created_at = models.DateTimeField(default=now)
    operational_since = models.DateField(blank=True, null=True)
    
    # Farm layout files (site overview, not individual asset models)
    layout_pdf = models.FileField(
        upload_to='farm_layouts/', 
        blank=True, 
        null=True,
        help_text="2D farm layout diagram (PDF format)"
    )
    site_model_file = models.FileField(
        upload_to='farm_site_models/', 
        blank=True, 
        null=True,
        help_text="3D site model showing overall farm layout (.glb format)"
    )
    site_model_file_name = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        help_text="Original filename of the site model"
    )
    site_model_uploaded_at = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        # Mimic SQLAlchemy before_insert: <company_id>-F-<5char>
        if not self.farm_id:
            unique_part = str(uuid.uuid4()).split("-")[0][:5].upper()
            self.farm_id = f"{self.company_id}-F-{unique_part}"
        super().save(*args, **kwargs)

    def to_dict(self):  # kept for parity with Flask; DRF serializers will be used
        return {
            "id": self.farm_id,
            "company_id": self.company_id,
            "location_id": self.location.location_id if self.location else None,
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None,
            "location": self.location.to_dict() if self.location else None,
        }

    def __str__(self) -> str:
        return f"{self.name} ({self.farm_id})"


class Asset(models.Model):
    class Meta:
        db_table = "assets"

    asset_id = models.CharField(max_length=200, primary_key=True, editable=False)
    company_id = models.CharField(max_length=200)  # keep as CharField; can be FK later
    location = models.ForeignKey(
        Location, on_delete=models.SET_NULL, null=True, related_name="assets"
    )
    farm = models.ForeignKey(
        Farm, on_delete=models.SET_NULL, null=True, blank=True, related_name="assets"
    )  # optional association
    name = models.CharField(max_length=100)
    asset_type = models.ForeignKey(
        AssetType, on_delete=models.SET_NULL, null=True, related_name="assets"
    )
    description = models.TextField(blank=True, null=True)

    # NOTE: Flask stored these as strings with datetime default. We model them as datetimes.
    # If your existing DB has string values, you can switch these to CharField(max_length=50).
    installation_date = models.DateTimeField(blank=True, null=True)
    manufactured_date = models.DateTimeField(blank=True, null=True)
    commission_date = models.DateTimeField(blank=True, null=True)
    decommission_date = models.DateTimeField(blank=True, null=True)

    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(default=now)

    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    health = models.IntegerField(default=random_health)

    # Tank-specific properties
    capacity = models.FloatField(blank=True, null=True)
    model_id = models.CharField(max_length=100, blank=True, null=True)
    current_volume = models.FloatField(blank=True, null=True)
    diameter = models.FloatField(blank=True, null=True)
    height = models.FloatField(blank=True, null=True)
    
    # Individual asset 3D model file
    model_file = models.FileField(
        upload_to='asset_models/', 
        blank=True, 
        null=True,
        help_text="3D model file (.glb format) for this specific asset"
    )
    model_file_name = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        help_text="Original filename of the 3D model"
    )
    model_uploaded_at = models.DateTimeField(blank=True, null=True)

    material = models.ForeignKey(
        Material, on_delete=models.SET_NULL, null=True, related_name="assets"
    )
    content = models.ForeignKey(
        Content, on_delete=models.SET_NULL, null=True, related_name="assets"
    )

    def save(self, *args, **kwargs):
        # Mimic SQLAlchemy before_insert: <farm_id>-A-<5char>
        if not self.asset_id:
            unique_part = str(uuid.uuid4()).split("-")[0][:5].upper()
            # Use farm_id if available; fall back to company-based prefix
            prefix = (self.farm.farm_id if self.farm else self.company_id) or "X"
            self.asset_id = f"{prefix}-A-{unique_part}"
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.name} ({self.asset_id})"


class AssetEvents(models.Model):
    class Meta:
        db_table = "asset_events"

    event_id = models.CharField(max_length=200, primary_key=True)
    asset = models.ForeignKey(
        Asset,
        to_field="asset_id",
        db_column="asset_id",
        on_delete=models.CASCADE,
        related_name="events",
    )
    title = models.CharField(max_length=120)

    event_type = models.ForeignKey(
        EventType, on_delete=models.SET_NULL, null=True, related_name="events"
    )

    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    event_status = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    performed_by = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(default=now)
    cost = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.title} ({self.event_id})"
