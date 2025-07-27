import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, HTMLResponse
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

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Kincog Learner Agent</title>
        <meta charset="utf-8">
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .chat-container {
                background: white;
                border-radius: 10px;
                padding: 20px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .chat-box {
                height: 400px;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
                margin-bottom: 10px;
                overflow-y: auto;
                background-color: #fafafa;
            }
            .input-container {
                display: flex;
                gap: 10px;
            }
            #messageInput {
                flex: 1;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 16px;
            }
            #sendButton {
                padding: 10px 20px;
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
            }
            #sendButton:hover {
                background-color: #0056b3;
            }
            .message {
                margin-bottom: 10px;
                padding: 10px;
                border-radius: 5px;
            }
            .user-message {
                background-color: #e3f2fd;
                text-align: right;
            }
            .agent-message {
                background-color: #f1f1f1;
            }
        </style>
    </head>
    <body>
        <div class="chat-container">
            <h1>🤖 Kincog Learner Agent</h1>
            <div class="chat-box" id="chatBox">
                <div class="message agent-message">
                    <strong>Agent:</strong> 你好！我是 kincog-learner-agent，一个智能学习助手。请告诉我你想了解什么？
                </div>
            </div>
            <div class="input-container">
                <input type="text" id="messageInput" placeholder="输入你的问题..." onkeypress="handleKeyPress(event)">
                <button id="sendButton" onclick="sendMessage()">发送</button>
            </div>
        </div>

        <script>
            async function sendMessage() {
                const input = document.getElementById('messageInput');
                const chatBox = document.getElementById('chatBox');
                const message = input.value.trim();
                
                if (!message) return;
                
                // Add user message
                chatBox.innerHTML += `<div class="message user-message"><strong>你:</strong> ${message}</div>`;
                input.value = '';
                chatBox.scrollTop = chatBox.scrollHeight;
                
                // Add loading message
                const loadingDiv = document.createElement('div');
                loadingDiv.className = 'message agent-message';
                loadingDiv.innerHTML = '<strong>Agent:</strong> 正在思考...';
                chatBox.appendChild(loadingDiv);
                chatBox.scrollTop = chatBox.scrollHeight;
                
                try {
                    const response = await fetch('/chat/stream', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({message: message})
                    });
                    
                    if (response.ok) {
                        const reader = response.body.getReader();
                        const decoder = new TextDecoder();
                        let fullResponse = '';
                        
                        // Remove loading message
                        chatBox.removeChild(loadingDiv);
                        
                        // Add agent message container
                        const agentDiv = document.createElement('div');
                        agentDiv.className = 'message agent-message';
                        agentDiv.innerHTML = '<strong>Agent:</strong> <span id="agentResponse"></span>';
                        chatBox.appendChild(agentDiv);
                        
                        while (true) {
                            const {done, value} = await reader.read();
                            if (done) break;
                            
                            const chunk = decoder.decode(value);
                            fullResponse += chunk;
                            document.getElementById('agentResponse').textContent = fullResponse;
                            chatBox.scrollTop = chatBox.scrollHeight;
                        }
                    } else {
                        loadingDiv.innerHTML = '<strong>Agent:</strong> 抱歉，发生了错误，请稍后重试。';
                    }
                } catch (error) {
                    loadingDiv.innerHTML = '<strong>Agent:</strong> 网络错误，请检查连接。';
                }
            }
            
            function handleKeyPress(event) {
                if (event.key === 'Enter') {
                    sendMessage();
                }
            }
        </script>
    </body>
    </html>
    """

@app.post("/chat/stream")
async def chat_stream(request: Request):
    data = await request.json()
    message = data.get("message")
    return StreamingResponse(agent_stream_response(message), media_type="text/event-stream") 