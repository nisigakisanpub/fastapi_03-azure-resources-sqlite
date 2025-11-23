# fastapi_app/tests/conftest.py

import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client(monkeypatch):
    # main.py 内の create_app() を呼んでFastAPIインスタンスを生成
    app = create_app()

    # Azureクライアントなどをモック化
    app.state.openai_client = MagicMock()
    app.state.index_client = MagicMock()
    app.state.indexer_client = MagicMock()
    app.state.blob_service_client = MagicMock()

    # FastAPI 用 TestClient
    with TestClient(app) as test_client:
        yield test_client
