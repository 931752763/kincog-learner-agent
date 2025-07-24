import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import AsyncGenerator
from agent.workflow import router_workflow

app = FastAPI()

class ChatRequest(BaseModel):
    user_id: str
    message: str

async def agent_stream_response(message: str) -> AsyncGenerator[str, None]:
    # Run the workflow and yield the result
    result = router_workflow.invoke({"input": message})
    output = result.get("output", "[无结果]")
    
    # Yield the output in chunks for streaming
    for i in range(0, len(output), 10):
        yield output[i:i+10]
        await asyncio.sleep(0.01)  # Small delay to simulate streaming

@app.post("/chat/stream")
async def chat_stream(request: Request):
    data = await request.json()
    message = data.get("message")
    return StreamingResponse(agent_stream_response(message), media_type="text/event-stream") 