from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import AsyncGenerator
from agent.workflow import run_agent_workflow

app = FastAPI()

class ChatRequest(BaseModel):
    user_id: str
    message: str

async def agent_stream_response(user_id: str, message: str) -> AsyncGenerator[str, None]:
    # 运行agent workflow，获取结果
    result = run_agent_workflow(user_id, message)
    # 假设result['result']为最终输出
    # 这里可以根据实际情况分多步yield，实现更细粒度流式
    yield result.get("result", "[无结果]")

@app.post("/chat/stream")
async def chat_stream(request: Request):
    data = await request.json()
    user_id = data.get("user_id")
    message = data.get("message")
    return StreamingResponse(agent_stream_response(user_id, message), media_type="text/event-stream") 