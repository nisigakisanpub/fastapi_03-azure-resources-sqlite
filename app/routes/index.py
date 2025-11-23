import os
from fastapi import APIRouter, Request, UploadFile, File, HTTPException
from pydantic import BaseModel
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchableField,
    SearchIndexerDataSourceConnection,
    SearchIndexerDataContainer,
    SearchIndexer,
)

router = APIRouter(prefix="/search", tags=["search"])

# ---- 定数 ----
AZURE_INDEX_NAME = "documents-index-01"
AZURE_INDEXER_NAME = "my-indexer-01"
AZURE_DATA_SOURCE_NAME = "my-datasource-01"
AZURE_STORAGE_CONTAINER_NAME = "mycontainer01"


# ---- モデル ----
class CreateIndexResponse(BaseModel):
    status: str
    name: str


class CreateIndexerResponse(BaseModel):
    status: str
    name: str


class UploadDocumentResponse(BaseModel):
    status: str
    filename: str


class RunIndexerResponse(BaseModel):
    status: str
    name: str


# ---- ヘルパ関数 ----
def _get(app, name):
    client = getattr(app.state, name, None)
    if client is None:
        raise HTTPException(status_code=500, detail=f"{name} not initialized")
    return client


# ---- 1. インデックス作成 ----
@router.post("/create_index", response_model=CreateIndexResponse)
async def create_index(request: Request):
    index_client = _get(request.app, "index_client")

    index_def = SearchIndex(
        name=AZURE_INDEX_NAME,
        fields=[
            SimpleField(name="id", type="Edm.String", key=True, filterable=True, sortable=True),
            SearchableField(name="title", type="Edm.String", filterable=True, sortable=True),
            SearchableField(name="content", type="Edm.String"),
            SearchableField(name="category", type="Edm.String", filterable=True, facetable=True),
            SimpleField(name="created_at", type="Edm.DateTimeOffset", filterable=True, sortable=True),
        ],
    )

    result = index_client.create_index(index_def)
    return CreateIndexResponse(status="created", name=result.name)


# ---- 2. インデクサ作成 ----
@router.get("/create_indexer", response_model=CreateIndexerResponse)
async def create_indexer(request: Request):
    app = request.app
    index_client = _get(app, "index_client")
    indexer_client = _get(app, "indexer_client")

    container = SearchIndexerDataContainer(name=AZURE_STORAGE_CONTAINER_NAME)
    data_source_connection = SearchIndexerDataSourceConnection(
        name=AZURE_DATA_SOURCE_NAME,
        type="azureblob",
        connection_string=os.getenv("AZURE_STORAGE_CONNECTION_STRING"),
        container=container,
    )

    indexer_client.create_or_update_data_source_connection(data_source_connection)

    indexer = SearchIndexer(
        name=AZURE_INDEXER_NAME,
        data_source_name=AZURE_DATA_SOURCE_NAME,
        target_index_name=AZURE_INDEX_NAME,
        schedule=None,
    )

    result = indexer_client.create_indexer(indexer)
    return CreateIndexerResponse(status="created", name=result.name)


# ---- 3. Blob へのドキュメントアップロード ----
@router.post("/upload_document", response_model=UploadDocumentResponse)
async def upload_document(request: Request, file: UploadFile = File(...)):
    blob_service_client = _get(request.app, "blob_service_client")
    blob_client = blob_service_client.get_blob_client(
        container=AZURE_STORAGE_CONTAINER_NAME, blob=file.filename
    )

    data = await file.read()
    blob_client.upload_blob(data, overwrite=True)

    return UploadDocumentResponse(status="uploaded", filename=file.filename)


# ---- 4. インデクサ実行 ----
@router.get("/run_indexer", response_model=RunIndexerResponse)
async def run_indexer(request: Request):
    indexer_client = _get(request.app, "indexer_client")
    indexer_client.run_indexer(AZURE_INDEXER_NAME)
    return RunIndexerResponse(status="indexer started", name=AZURE_INDEXER_NAME)
