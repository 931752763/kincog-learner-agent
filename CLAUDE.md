# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python project for an intelligent learning assistant based on the Qwen language model, using langchain and langgraph. It provides a REST API service with both regular and streaming chat endpoints.

## Project Structure

```
kincog-learner-agent/
├── agent/
│   ├── __init__.py
│   ├── intent.py             # Intent recognition
│   ├── memory.py             # Memory management
│   ├── rag.py               # Retrieval Augmented Generation
│   ├── tools.py              # Tool registration and calling
│   ├── llm.py                # LLM initialization
│   └── workflow.py           # LangGraph workflow (using Claude)
├── main.py                   # FastAPI main service
└── requirements.txt          # Dependencies
```

## Common Commands

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run Tests
```bash
# No specific test files found, but you can run:
python -m pytest  # if tests are added
```

### Start Development Server
```bash
python main.py
```

### API Usage
- Streaming chat endpoint: POST /chat/stream
- Regular chat endpoint: POST /chat

## Architecture Overview

The project follows a modular design:

1. **Main Service**: FastAPI application in `main.py` that exposes REST endpoints
2. **Agent Module**: Core logic is in the `agent/` directory
   - `llm.py`: Handles LLM initialization and configuration
   - `intent.py`: Simple keyword-based intent recognition
   - `memory.py`: In-memory user conversation history storage
   - `tools.py`: Placeholder for tool integration
   - `rag.py`: Placeholder for retrieval-augmented generation
   - `workflow.py`: LangGraph-based workflow implementation
3. **Integration**: Uses langchain and langgraph for LLM integration and workflow management

## Key Components

1. **LLM Integration**: Supports Qwen models through langchain with OpenAI-compatible API
2. **Intent Recognition**: Basic keyword-based intent detection in `intent.py`
3. **Memory Management**: Simple in-memory storage for user conversations in `memory.py`
4. **Workflow**: LangGraph-based workflow implementation in `workflow.py`
5. **API Service**: FastAPI service in `main.py` providing both streaming and regular chat endpoints

## Development Notes

- The project uses langchain framework for LLM integration
- Supports OpenAI-compatible mode for calling Qwen API
- Uses FastAPI framework for web services
- Supports streaming responses for better user experience
- Modular design makes it easy to add new features