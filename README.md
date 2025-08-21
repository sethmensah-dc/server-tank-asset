# Tank Asset Management API

A comprehensive Django REST Framework API for managing tank farms, assets, and related infrastructure in oil & gas facilities. This project provides a robust backend system for tracking storage tanks, compressors, pumps, and other industrial assets across multiple facilities.

## 🚀 Features

- **Tank Farm Management**: Organize assets by farms and locations
- **Asset Tracking**: Detailed asset specifications, health monitoring, and status tracking
- **Event Management**: Track maintenance, inspections, and asset events
- **Location Services**: GPS coordinates and location-based asset mapping
- **Company Management**: Multi-tenant support for different organizations
- **Data Import**: CSV import capabilities for bulk asset data
- **Interactive Documentation**: Swagger UI and ReDoc for API exploration
- **Browsable API**: Web interface for testing and data exploration

## 📊 Data Overview

- **41 Farms** across multiple locations
- **405 Assets** including tanks, compressors, pumps, and control systems
- **2,289 Asset Events** with maintenance and inspection history
- **10 Companies** with multi-facility operations
- **Real Production Data** migrated from Flask application

## 🏗️ Architecture

### Technology Stack
- **Backend**: Django 5.2.5 + Django REST Framework 3.16.1
- **Database**: SQLite (easily configurable for PostgreSQL/MySQL)
- **Documentation**: DRF-Spectacular with Swagger UI/ReDoc
- **API Schema**: OpenAPI 3.0 specification

### Project Structure
```
tank-asset/
├── config/                 # Django configuration
│   ├── settings.py         # Main settings with DRF config
│   ├── urls.py            # Root URL configuration
│   └── wsgi.py            # WSGI application
├── core/                   # Main application
│   ├── models.py          # Data models (Farm, Asset, etc.)
│   ├── serializers.py     # DRF serializers
│   ├── views.py           # API views and viewsets
│   ├── urls.py            # API URL patterns
│   ├── admin.py           # Django admin configuration
│   └── management/        # Custom management commands
│       └── commands/
│           ├── migrate_flask_data.py  # Flask to Django migration
│           └── import_csv_assets.py   # CSV import utility
├── static/                 # Static files
│   └── uploads/
│       └── farm_layouts/   # Farm layout PDF files
├── db.sqlite3             # SQLite database
├── manage.py              # Django management script
└── README.md              # This file
```

## 🔧 Installation & Setup

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Git

### Quick Start

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd tank-asset
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install django djangorestframework drf-spectacular
   ```

4. **Run Migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create Superuser (Optional)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Start Development Server**
   ```bash
   python manage.py runserver
   ```

7. **Access the API**
   - API Root: http://localhost:8000/
   - Swagger Docs: http://localhost:8000/api/docs/
   - ReDoc: http://localhost:8000/api/redoc/
   - Django Admin: http://localhost:8000/admin/

## 📖 API Documentation

### Interactive Documentation
- **Swagger UI**: http://localhost:8000/api/docs/ - Interactive API testing
- **ReDoc**: http://localhost:8000/api/redoc/ - Beautiful documentation
- **OpenAPI Schema**: http://localhost:8000/api/schema/ - Machine-readable spec

### Core Endpoints

#### 🏭 Farm Management
- `GET /farm/{farm_id}/assets` - Get all assets for a specific farm
- `GET /api/farm-model/{model_id}` - Get farm details by model ID
- `GET /browse/farms/` - Browse all farms with pagination

#### 🏗️ Asset Management
- `GET /api/asset/{asset_id}` - Get detailed asset information
- `GET /api/asset-name/{asset_name}` - Find asset by name
- `GET /api/asset-model/{model_id}` - Get asset by model ID
- `GET /api/asset-type/{asset_type}` - Get assets by type
- `GET /browse/assets/` - Browse all assets with pagination

#### 📋 Browsing & Search
- `GET /browse/farms/` - Paginated farm listing with search
- `GET /browse/assets/` - Paginated asset listing with filters
- `GET /` - API root with navigation and sample data

### Sample API Calls

#### Get Farm Assets
```bash
curl -X GET "http://localhost:8000/farm/SYS-1D3407DB-F-13083/assets"
```

**Response:**
```json
{
  "farm_id": "SYS-1D3407DB-F-13083",
  "farm_name": "Baton Rouge Terminal",
  "assets_count": 57,
  "assets": [
    {
      "asset_id": "SYS-1D3407DB-F-13083-A-06527",
      "name": "HEA-9BA17B",
      "type": {
        "id": 3,
        "name": "Heat Exchanger",
        "description": "Heat transfer equipment"
      },
      "status": "active",
      "specifications": {
        "capacity": 15000.0,
        "current_volume": 12500.0,
        "diameter": 8.5,
        "height": 25.0
      }
    }
  ],
  "location": {
    "city": "Baton Rouge",
    "country": "USA",
    "latitude": 30.4515,
    "longitude": -91.1871
  }
}
```

#### Get Asset Details
```bash
curl -X GET "http://localhost:8000/api/asset/SYS-88627B0B-F-E304B-A-6BDDD"
```

**Response:**
```json
{
  "id": "SYS-88627B0B-F-E304B-A-6BDDD",
  "name": "Compressor 1",
  "type": {
    "id": 1,
    "name": "Fixed Roof Tank",
    "description": "Large capacity storage tank"
  },
  "status": "active",
  "health": 100,
  "farm": {
    "id": "SYS-88627B0B-F-E304B",
    "name": "Farm SYS-88627B0B-F-E304B"
  },
  "specifications": {
    "capacity": 15000.0,
    "current_volume": 3981.0,
    "diameter": 750.0,
    "height": 80.0
  },
  "coordinates": {
    "latitude": 58.8388854,
    "longitude": -3.121426417
  }
}
```

## 🗄️ Data Models

### Core Models

#### Farm Model
```python
class Farm(models.Model):
    farm_id = models.CharField(max_length=200, primary_key=True)
    company_id = models.CharField(max_length=200)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50)  # active, inactive, under_construction
    created_at = models.DateTimeField(default=now)
    operational_since = models.DateField(blank=True, null=True)
```

#### Asset Model
```python
class Asset(models.Model):
    asset_id = models.CharField(max_length=200, primary_key=True)
    company_id = models.CharField(max_length=200)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True)
    farm = models.ForeignKey(Farm, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=100)
    asset_type = models.ForeignKey(AssetType, on_delete=models.SET_NULL, null=True)
    description = models.TextField(blank=True, null=True)
    
    # Operational dates
    installation_date = models.DateTimeField(blank=True, null=True)
    manufactured_date = models.DateTimeField(blank=True, null=True)
    commission_date = models.DateTimeField(blank=True, null=True)
    
    # Status and monitoring
    status = models.CharField(max_length=50)
    health = models.IntegerField(default=random_health)  # 0-100
    
    # Location data
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    
    # Tank specifications
    capacity = models.FloatField(blank=True, null=True)
    current_volume = models.FloatField(blank=True, null=True)
    diameter = models.FloatField(blank=True, null=True)
    height = models.FloatField(blank=True, null=True)
    
    # References
    material = models.ForeignKey(Material, on_delete=models.SET_NULL, null=True)
    content = models.ForeignKey(Content, on_delete=models.SET_NULL, null=True)
```

### Supporting Models
- **Location**: Geographic information with coordinates
- **Company**: Organization and contact details
- **AssetType**: Classification of asset types (tanks, compressors, etc.)
- **Material**: Construction materials (steel, aluminum, etc.)
- **Content**: Stored substances (crude oil, gasoline, etc.)
- **AssetEvents**: Maintenance and inspection events
- **EventType**: Categories of events (maintenance, inspection, etc.)

### Model Relationships
```
Company (1) ──→ (N) Farm ──→ (N) Asset
                   │           │
Location (1) ──────┴───────────┘
                               │
AssetType (1) ─────────────────┤
Material (1) ──────────────────┤
Content (1) ───────────────────┤
                               │
AssetEvents (N) ───────────────┘
```

## 🔄 Data Management

### CSV Import
Import asset data from CSV files:

```bash
python manage.py import_csv_assets --csv-file="/path/to/assets.csv"
```

**CSV Format:**
```csv
asset_id,company_id,location_id,farm_id,name,asset_type_id,description,capacity,latitude,longitude,...
SYS-123-A-001,SYS-123,1,SYS-123-F-001,Tank A-001,1,Storage tank,15000,29.7604,-95.3698,...
```

### Flask Migration
Migrate existing Flask data:

```bash
python manage.py migrate_flask_data --flask-db="/path/to/flask.db" --clear-existing
```

### Admin Interface
Access Django admin at http://localhost:8000/admin/ for:
- Data management and editing
- User and permission management
- Bulk operations and filtering
- Data export capabilities

## 🧪 Testing & Development

### API Testing
1. **Swagger UI**: Interactive testing at http://localhost:8000/api/docs/
2. **Browsable API**: Web interface at http://localhost:8000/
3. **cURL Examples**: See API documentation section
4. **Postman**: Import OpenAPI schema from http://localhost:8000/api/schema/

### Sample Data
The system includes real production data:
- **Farm ID**: `SYS-1D3407DB-F-13083` (Baton Rouge Terminal, 57 assets)
- **Asset ID**: `SYS-1D3407DB-F-13083-A-06527` (Heat Exchanger)
- **CSV Farm**: `SYS-88627B0B-F-E304B` (5 compressors from Varco Oil Well)

### Development Commands
```bash
# Run development server
python manage.py runserver

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Import CSV data
python manage.py import_csv_assets --csv-file="data.csv"

# Migrate Flask data
python manage.py migrate_flask_data --flask-db="flask.db"
```

## 🌐 Deployment

### Production Settings
For production deployment, update `config/settings.py`:

```python
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com']

# Use PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'tank_assets',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Security settings
SECRET_KEY = 'your-secret-key'
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### Docker Support
Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

## 📊 API Response Examples

### Farm Assets Response
```json
{
  "farm_id": "SYS-1D3407DB-F-13083",
  "farm_name": "Baton Rouge Terminal",
  "assets_count": 57,
  "farm_description": "Storage facility in Baton Rouge",
  "pdf_url": "/static/uploads/farm_layouts/SYS-1D3407DB-F-13083.pdf",
  "location": {
    "id": 13,
    "name": "Baton Rouge Terminal 1",
    "city": "Baton Rouge",
    "country": "USA",
    "latitude": 30.4515,
    "longitude": -91.1871
  },
  "assets": [
    {
      "asset_id": "SYS-1D3407DB-F-13083-A-06527",
      "name": "HEA-9BA17B",
      "latitude": null,
      "longitude": null,
      "description": "Heat Exchanger at Baton Rouge Terminal",
      "status": "active",
      "type": {
        "id": 3,
        "name": "Heat Exchanger",
        "description": "Heat transfer equipment"
      },
      "location": {
        "id": 13,
        "name": "Baton Rouge Terminal 1",
        "address": "1500 Government St",
        "city": "Baton Rouge",
        "country": "USA",
        "coordinates": {
          "latitude": 30.4515,
          "longitude": -91.1871
        }
      },
      "dates": {
        "installation": "2023-03-16T00:00:00Z",
        "manufactured": "2022-12-15T00:00:00Z",
        "commission": "2023-04-01T00:00:00Z",
        "decommission": null,
        "created": "2025-04-16T12:49:39.843415Z"
      },
      "specifications": {
        "capacity": 15000.0,
        "current_volume": 12500.0,
        "diameter": 8.5,
        "height": 25.0,
        "material": "Stainless Steel",
        "content": "Crude Oil"
      },
      "events": [
        {
          "id": "EVT-001",
          "type_id": 1,
          "status": "completed",
          "start_date": "2025-01-15T09:00:00Z",
          "end_date": "2025-01-15T17:00:00Z",
          "description": "Routine maintenance inspection",
          "performed_by": "John Smith",
          "created_at": "2025-01-15T08:30:00Z"
        }
      ]
    }
  ]
}
```

### Browse Assets Response
```json
{
  "count": 405,
  "next": "http://localhost:8000/browse/assets/?page=2",
  "previous": null,
  "results": [
    {
      "id": "SYS-4A549A15-F-80829-A-42818",
      "name": "FIX-03E9A2",
      "latitude": null,
      "longitude": null,
      "health": 85,
      "type": {
        "id": 1,
        "name": "Fixed Roof Tank",
        "description": "Large capacity storage tank"
      },
      "description": "Fixed Roof Tank at Beaumont Storage Facility",
      "status": "active",
      "model_id": "FIX-03E9A2",
      "capacity": null,
      "current_volume": null,
      "diameter": null,
      "height": null,
      "material_name": null,
      "content_name": null,
      "events": []
    }
  ]
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For questions and support:
- Check the API documentation at `/api/docs/`
- Review this README
- Open an issue on GitHub
- Contact the development team

## 🔗 Related Links

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [DRF-Spectacular](https://drf-spectacular.readthedocs.io/)
- [OpenAPI Specification](https://swagger.io/specification/)

---

**Tank Asset Management API** - Comprehensive solution for industrial asset tracking and management.