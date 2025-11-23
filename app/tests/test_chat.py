from types import SimpleNamespace


def test_chat(client):
    # ---- モックレスポンス用の簡易クラス群（Flask版と同じ構造） ----
    class MockMessage:
        def __init__(self, content: str):
            self.content = content

    class MockChoice:
        def __init__(self, message):
            self.message = message

    class MockResponse:
        def __init__(self, content: str):
            self.choices = [MockChoice(MockMessage(content))]

    # ---- openai_client.chat.completions.create(...) をモックする ----
    mock_client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(
                create=lambda model, messages: MockResponse("モック応答")
            )
        )
    )

    # conftest.py で作った FastAPI app に差し込む
    # Flaskのとき: client.application.config["AZ_OPENAI_CLIENT"] = ...
    # FastAPIでは app.state に置いておく
    client.app.state.openai_client = mock_client

    # ---- 実行 ----
    resp = client.post(
        "/chat",
        json={
            "messages": [
                {"role": "user", "content": "こんにちは。今日は何曜日？"}
            ]
        },
    )

    assert resp.status_code == 200
    data = resp.json()
    assert "message" in data
    assert data["message"] == "モック応答"
