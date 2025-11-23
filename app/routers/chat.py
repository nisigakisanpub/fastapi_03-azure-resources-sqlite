# fastapi_app/routers/chat.py

import os
from typing import List, Literal, Optional

from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/chat", tags=["chat"])


# ---- リクエスト/レスポンスのモデル ----

class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]


class ChatResponse(BaseModel):
    message: str


# ---- LLM呼び出しのヘルパ ----

def get_response_from_llm(openai_client, messages: List[dict]) -> str:
    """
    Flask版の:
        openai_client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            messages=messages
        )
    をそのままFastAPI用にしたもの。
    """
    model_name = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    if not model_name:
        raise RuntimeError("AZURE_OPENAI_DEPLOYMENT is not set.")

    # openai==1.x / azure-openai のPython SDKの想定
    res = openai_client.chat.completions.create(
        model=model_name,
        messages=messages,
    )

    # Flask版と同じように先頭を返す
    return res.choices[0].message.content


# ---- ルート ----

@router.post("", response_model=ChatResponse)
async def chat(request: Request, body: ChatRequest):
    """
    POST /chat
    {
        "messages": [
            {"role": "user", "content": "こんにちは"}
        ]
    }
    → {"message": "こんにちは！"} のように返す。
    """
    # Flaskの current_app 相当: request.app
    app = request.app

    # bp_main.py から FastAPI 化した側で
    # app.state.openai_client = ...
    # を設定している前提
    openai_client = getattr(app.state, "openai_client", None)
    if openai_client is None:
        raise HTTPException(status_code=500, detail="OpenAI client is not configured.")

    # Pydanticモデル → OpenAIに渡す形式(dict)に変換
    messages = [m.model_dump() for m in body.messages]

    try:
        content = get_response_from_llm(openai_client, messages)
    except Exception as e:
        # Flask版で jsonify({"error": str(e)}) を返していたのと同じノリ
        raise HTTPException(status_code=500, detail=str(e))

    return ChatResponse(message=content)
