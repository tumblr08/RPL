# Migration Guide: Graphene to Strawberry GraphQL

## Overview

Aplikasi Anda telah berhasil dimigrasikan dari Graphene ke Strawberry GraphQL dengan penambahan fitur upload dokumen. Berikut adalah panduan lengkap untuk menggunakan versi yang baru.

## Perubahan Utama

### 1. Framework GraphQL
- **Sebelum**: Graphene
- **Sesudah**: Strawberry GraphQL
- **Keuntungan**: Type hints yang lebih baik, sintaks modern, performance yang lebih baik

### 2. Model Structure
- Menggunakan Python `@dataclass` decorator
- Type hints yang konsisten
- Model baru: `Document` dan `ChecklistItem`

### 3. Fitur Baru: Upload Dokumen
- Upload file melalui REST endpoint `/upload`
- Download file via `/download/<document_id>`
- Integrasi dengan Projects dan Tasks
- Metadata lengkap untuk setiap dokumen

## Instalasi dan Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Struktur Direktori
```
project/
├── app.py                 # Flask application
├── schema.py             # Strawberry GraphQL schema
├── models.py             # Data models
├── data_store.py         # In-memory data storage
├── utils.py              # Utility functions
├── requirements.txt      # Dependencies
├── uploads/              # File upload directory (dibuat otomatis)
└── examples/
    ├── example_queries.md
    └── MIGRATION_GUIDE.md
```

### 3. Menjalankan Aplikasi
```bash
python app.py
```

Aplikasi akan berjalan di `http://localhost:5000`

## API Endpoints

### GraphQL Endpoint
- **URL**: `/graphql`
- **Methods**: GET (Playground), POST (Queries/Mutations)
- **Playground**: Buka `http://localhost:5000/graphql` di browser

### REST Endpoints
- **Upload**: `POST /upload`
- **Download**: `GET /download/<document_id>`
- **File Info**: `GET /files/<document_id>/info`
- **Health Check**: `GET /health`

## Perbedaan Sintaks

### Query/Mutation Syntax

#### Graphene (Lama)
```python
class CreateProject(graphene.Mutation):
    class Arguments:
        title = graphene.String()
        description = graphene.String()
        deadline = graphene.String()
        ownerId = graphene.ID()

    project = graphene.Field(ProjectType)

    def mutate(self, info, title, description, deadline, ownerId):
        # implementation
        pass
```

#### Strawberry (Baru)
```python
@strawberry.input
class CreateProjectInput:
    title: str
    description: str
    deadline: str
    owner_id: strawberry.ID

@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_project(self, input: CreateProjectInput) -> ProjectType:
        # implementation
        pass
```

### Type Definitions

#### Graphene (Lama)
```python
class ProjectType(graphene.ObjectType):
    id = graphene.ID()
    title = graphene.String()
    description = graphene.String()
```

#### Strawberry (Baru)
```python
@strawberry.type
class ProjectType:
    id: strawberry.ID
    title: str
    description: str
    
    @strawberry.field
    def documents(self) -> List[DocumentType]:
        return get_documents_by_project(int(self.id))
```

## Fitur Upload Dokumen

### Cara Upload File

#### Via REST API
```bash
curl -X POST http://localhost:5000/upload \
  -F "file=@document.pdf" \
  -F "project_id=1" \
  -F "uploaded_by=1"
```

#### Via HTML Form
```html
<form action="/upload" method="post" enctype="multipart/form-data">
  <input type="file" name="file" required>
  <input type="hidden" name="project_id" value="1">
  <input type="hidden" name="uploaded_by" value="1">
  <button type="submit">Upload</button>
</form>
```

#### Via JavaScript
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('project_id', '1');
formData.append('uploaded_by', '1');

fetch('/upload', {
  method: 'POST',
  body: formData
}).then(response => response.json())
  .then(data => console.log(data));
```

### Supported File Types
- Documents: PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX, TXT
- Images: PNG, JPG, JPEG, GIF
- Maximum size: 16MB

### GraphQL Queries untuk Dokumen

#### Mendapatkan dokumen project
```graphql
query GetProjectDocuments {
  allProjects {
    id
    title
    documents {
      id
      filename
      fileSize
      uploadedAt
      uploader {
        name
      }
    }
  }
}
```

#### Upload dokumen via GraphQL
```graphql
mutation UploadDocument {
  uploadDocument(input: {
    filename: "report.pdf"
    fileSize: 1024000
    contentType: "application/pdf"
    projectId: "1"
    uploadedBy: "1"
  }) {
    success
    message
    document {
      id
      filename
    }
  }
}
```

## Testing

### 1. Test Basic Functionality
```bash
# Health check
curl http://localhost:5000/health

# GraphQL introspection
curl -X POST http://localhost:5000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ __schema { types { name } } }"}'
```

### 2. Test File Upload
```bash
# Create a test file
echo "Test content" > test.txt

# Upload the file
curl -X POST http://localhost:5000/upload \
  -F "file=@test.txt" \
  -F "project_id=1" \
  -F "uploaded_by=1"
```

### 3. Test GraphQL Queries
Buka `http://localhost:5000/graphql` dan coba query berikut:
```graphql
query {
  allUsers {
    id
    name
    email
  }
}
```

## Troubleshooting

### Common Issues

#### 1. File Upload Error
```bash
# Pastikan direktori uploads ada
mkdir -p uploads
chmod 755 uploads
```

#### 2. GraphQL Schema Error
- Pastikan semua imports sudah benar
- Check type annotations di model

#### 3. CORS Issues (jika diakses dari frontend)
```python
from flask_cors import CORS
CORS(app)
```

#### 4. File Size Limit
Edit di `app.py`:
```python
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB
```

## Performance Tips

### 1. Database Integration
Saat ini menggunakan in-memory storage. Untuk production:
```python
# Ganti dengan database ORM seperti SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
```

### 2. File Storage
Untuk production, gunakan cloud storage:
```python
# AWS S3, Google Cloud Storage, atau Azure Blob
import boto3
```

### 3. Caching
```python
# Redis untuk caching GraphQL queries
import redis
```

## Migration Checklist

- [x] ✅ Migrasi dari Graphene ke Strawberry
- [x] ✅ Update semua type definitions
- [x] ✅ Update queries dan mutations
- [x] ✅ Tambah fitur upload dokumen
- [x] ✅ Tambah REST endpoints untuk file operations
- [x] ✅ Update data models dengan Document type
- [x] ✅ Tambah file validation dan security
- [x] ✅ Dokumentasi dan contoh penggunaan

## Next Steps

1. **Database Integration**: Migrate dari in-memory ke database
2. **Authentication**: Tambah JWT authentication
3. **File Processing**: Tambah preview untuk dokumen
4. **Real-time Updates**: WebSocket untuk notifikasi
5. **Testing**: Unit tests dan integration tests

## Support

Jika ada pertanyaan atau masalah, silakan check:
1. GraphQL Playground di `/graphql`
2. Health check endpoint di `/health`
3. Log errors di console aplikasi
4. File examples di folder `examples/`