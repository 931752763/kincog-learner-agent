from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import AsyncGenerator
from agent.qwen_simple import run_qwen_agent

app = FastAPI()

class ChatRequest(BaseModel):
    user_id: str
    message: str

async def agent_stream_response(user_id: str, message: str) -> AsyncGenerator[str, None]:
    # 运行Qwen agent，获取结果
    result = run_qwen_agent(user_id, message)
    # 返回结果
    yield result.get("response", "[无结果]")

@app.post("/chat/stream")
async def chat_stream(request: Request):
    data = await request.json()
    user_id = data.get("user_id")
    message = data.get("message")
    return StreamingResponse(agent_stream_response(user_id, message), media_type="text/event-stream") 