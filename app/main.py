# fastapi_app/main.py

import os

from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential
from azure.search.documents.indexes import SearchIndexClient, SearchIndexerClient
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
from fastapi import FastAPI
from openai import AzureOpenAI

from app.database.db import init_db
from app.routes.chat import router as chat_router
from app.routes.product import router as product_router
from app.routes.index import router as search_router

load_dotenv()


def create_app() -> FastAPI:
    app = FastAPI(title="FastAPI Azure App")

    # Azure clients setup
    credential = DefaultAzureCredential()

    openai_client = AzureOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_DEPLOYMENT_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_DEPLOYMENT_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    )

    index_client = SearchIndexClient(
        endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
        credential=AzureKeyCredential(os.environ["AZURE_SEARCH_API_KEY"]),
    )

    indexer_client = SearchIndexerClient(
        endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
        credential=AzureKeyCredential(os.environ["AZURE_SEARCH_API_KEY"]),
    )

    blob_service_client = BlobServiceClient.from_connection_string(
        os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    )

    # FastAPIのアプリケーション状態に格納
    app.state.openai_client = openai_client
    app.state.index_client = index_client
    app.state.indexer_client = indexer_client
    app.state.blob_service_client = blob_service_client
    app.state.credential = credential

    # DB初期化
    init_db()

    # ルーター登録
    app.include_router(chat_router)
    app.include_router(search_router)
    app.include_router(product_router)

    return app


app = create_app()
