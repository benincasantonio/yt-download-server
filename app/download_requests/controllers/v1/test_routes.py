import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.download_requests.repositories.download_request_repository import DownloadRequestRepository
from app.download_requests.models.download_request_entity import DownloadRequestEntity
from app.download_requests.enums.download_status import DownloadStatus
from beanie import PydanticObjectId
from unittest.mock import AsyncMock, patch

@pytest.fixture
def mock_repo_find_all(mocker):
    return mocker.patch.object(DownloadRequestRepository, "find_all", new_callable=AsyncMock)

@pytest.fixture
def mock_repo_find_by_id(mocker):
    return mocker.patch.object(DownloadRequestRepository, "find_by_id", new_callable=AsyncMock)

@pytest.fixture
def mock_repo_create(mocker):
    return mocker.patch.object(DownloadRequestRepository, "create", new_callable=AsyncMock)

@pytest.fixture
def mock_repo_delete(mocker):
    return mocker.patch.object(DownloadRequestRepository, "delete", new_callable=AsyncMock)

@pytest.mark.asyncio
async def test_get_download_requests(mock_repo_find_all):
    mock_repo_find_all.return_value = [
        DownloadRequestEntity.model_construct(id=PydanticObjectId(), url="http://example.com/video1", status=DownloadStatus.REGISTERED),
        DownloadRequestEntity.model_construct(id=PydanticObjectId(), url="http://example.com/video2", status=DownloadStatus.REGISTERED),
    ]
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/download-requests/")
        assert response.status_code == 200
        assert len(response.json()) == 2

@pytest.mark.asyncio
async def test_get_download_request(mock_repo_find_by_id):
    request_id = PydanticObjectId()
    mock_repo_find_by_id.return_value = DownloadRequestEntity.model_construct(id=request_id, url="http://example.com/video1", status=DownloadStatus.REGISTERED)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(f"/api/v1/download-requests/{request_id}")
        assert response.status_code == 200
        # PydanticObjectId needs to be converted to string for comparison
        response_json = response.json()
        assert response_json["id"] == str(request_id)

@pytest.mark.asyncio
async def test_get_download_request_not_found(mock_repo_find_by_id):
    request_id = PydanticObjectId()
    mock_repo_find_by_id.return_value = None
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(f"/api/v1/download-requests/{request_id}")
        assert response.status_code == 404

@pytest.mark.asyncio
async def test_create_download_request(mock_repo_create):
    request_data = {"url": "http://example.com/video1"}
    request_id = PydanticObjectId()
    mock_repo_create.return_value = DownloadRequestEntity.model_construct(id=request_id, url=request_data["url"], status=DownloadStatus.REGISTERED)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/v1/download-requests/", json=request_data)
        assert response.status_code == 200
        response_json = response.json()
        assert response_json["url"] == request_data["url"]
        assert "id" in response_json

@pytest.mark.asyncio
async def test_create_download_request_invalid_url():
    request_data = {"url": "invalid-url"}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/v1/download-requests/", json=request_data)
        assert response.status_code == 400

@pytest.mark.asyncio
async def test_delete_download_request(mock_repo_delete):
    request_id = PydanticObjectId()
    mock_repo_delete.return_value = True
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.delete(f"/api/v1/download-requests/{request_id}")
        assert response.status_code == 200
        assert response.json() == {"message": f"Download request with id {request_id} deleted successfully"}

@pytest.mark.asyncio
async def test_delete_download_request_not_found(mock_repo_delete):
    request_id = PydanticObjectId()
    mock_repo_delete.return_value = False
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.delete(f"/api/v1/download-requests/{request_id}")
        assert response.status_code == 404
