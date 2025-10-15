# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

YouTube Download Server - An async FastAPI service for managing YouTube video downloads with a worker-based architecture.

## Development Commands

### Starting the Application
```bash
# Start all services (API server, worker, MongoDB, MinIO)
docker-compose up --build

# Start in detached mode
docker-compose up -d

# View logs
docker-compose logs -f
docker-compose logs -f yt-download-server  # API server only
docker-compose logs -f download-worker      # Worker only
```

### Running the API Server Locally
```bash
# Install dependencies
pip install -r requirements.txt

# Run API server with hot reload
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Running the Download Worker Locally
```bash
# Run worker with auto-reload on file changes
watchfiles "python -m app.download_worker.main" /app
```

## Architecture

### Two-Service Pattern
The application uses a **decoupled request/worker pattern**:

1. **API Server** (`yt-download-server`) - FastAPI application that:
   - Accepts download requests via REST API
   - Validates URLs
   - Creates records in MongoDB with `REGISTERED` status
   - Returns immediately to client

2. **Download Worker** (`download-worker`) - Background process that:
   - Uses MongoDB Change Streams to watch for new inserts
   - Listens for records with `status: REGISTERED` and `deleted: false`
   - Processes downloads asynchronously using yt-dlp
   - Updates status to `IN_PROGRESS` → `COMPLETED`/`FAILED`

This pattern ensures the API remains responsive while downloads happen asynchronously.

### Data Flow
```
Client → POST /api/v1/download-requests → MongoDB (REGISTERED)
                                              ↓
                                        Change Stream
                                              ↓
                                     Download Worker → yt-dlp → MinIO
                                              ↓
                                     MongoDB (IN_PROGRESS → COMPLETED)
```

### MongoDB Change Streams
The worker uses MongoDB Change Streams (`app/download_worker/main.py:9-26`) to react to new download requests in real-time. The pipeline filters for:
- `operationType: "insert"`
- `status: "registered"`
- `deleted: false`

**Important**: Change Streams require MongoDB replica set mode (configured in docker-compose.yml with `rs0`).

### Entity Pattern
All entities inherit from `BaseEntity` (`app/download_requests/models/base_entity.py`) which provides:
- **Soft deletion**: `deleted` flag + `deletedAt` timestamp
- **Automatic timestamps**: `createdAt`, `updatedAt`
- **Active filtering**: `find_active()` method excludes soft-deleted records
- Repository pattern uses `find_active()` to respect soft deletes

### Database Layer
Uses Beanie ODM (async MongoDB ODM for Pydantic):
- Document models inherit from `BaseEntity` → `Document`
- Initialization in `app/config/database.py:init_db()`
- Database name: `yt_downloads`
- Collection: `download_requests`

### Repository Pattern
Static methods in `DownloadRequestRepository`:
- `create()` - Sets initial status to `REGISTERED`
- `find_by_id()` / `find_all()` - Use `find_active()` to exclude deleted
- `update()` - Updates entity fields
- `delete()` - Soft delete via `entity.soft_delete()`

### Status Lifecycle
Download requests flow through statuses (`app/download_requests/enums/download_status.py`):
1. `REGISTERED` - Created by API, waiting for worker
2. `IN_PROGRESS` - Worker picked up and processing
3. `COMPLETED` - Successfully downloaded
4. `FAILED` - Error during download

## Project Structure

```
app/
├── main.py                          # FastAPI app entry point
├── config/
│   ├── database.py                  # MongoDB/Beanie initialization
│   └── config.py                    # Global config (API_BASE_PATH)
├── services/
│   └── s3_client.py                 # MinIO/S3 client
├── download_requests/               # Main domain module
│   ├── controllers/v1/routes.py     # REST endpoints
│   ├── repositories/                # Data access layer
│   ├── models/                      # Beanie document models
│   │   ├── base_entity.py          # Base class with soft delete
│   │   └── download_request_entity.py
│   ├── schemas/                     # Pydantic request/response schemas
│   ├── DTOs/                        # Data transfer objects
│   └── enums/download_status.py     # Status enum
└── download_worker/
    ├── main.py                      # Worker entry point with change stream
    └── services/
        └── youtube_download_service.py  # yt-dlp integration
```

## Key Dependencies

- **FastAPI + Uvicorn**: Web framework and ASGI server
- **Beanie**: Async MongoDB ODM built on Pydantic
- **yt-dlp**: YouTube download engine (requires ffmpeg)
- **boto3**: AWS SDK for MinIO/S3 storage
- **pymongo**: MongoDB driver (used for change streams)
- **watchfiles**: Auto-reload for development

## Environment Variables

Required in `.env`:
- `MONGO_URI` - MongoDB connection string
- `MONGO_ROOT_USERNAME`, `MONGO_ROOT_PASSWORD` - MongoDB auth
- `MONGO_DATABASE` - Database name
- `MINIO_ROOT_USER`, `MINIO_ROOT_PASSWORD` - MinIO credentials

## API Endpoints

Base path: `/api/v1/download-requests`

- `GET /` - List all active download requests
- `GET /{id}` - Get single request by ID
- `POST /` - Create new download request (validates URL)
- `DELETE /{id}` - Soft delete request

## Development Notes

- **Soft Deletes**: Always use repository methods, never query directly to respect `deleted` flag
- **Change Streams**: Require replica set - don't disable in docker-compose
- **Status Indexing**: `status` field is indexed for change stream performance
- **Worker Pattern**: Worker is stateless - safe to scale horizontally
- **API Versioning**: Routes use `/v1/` prefix for future API versioning
