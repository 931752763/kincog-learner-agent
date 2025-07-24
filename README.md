# kincog-learner-agent

一个基于Qwen模型的智能学习助手项目，使用langchain和langgraph构建。

## 功能特性

- 🤖 集成Qwen大语言模型（通过langchain）
- 💬 支持智能对话和学习指导
- 🔄 支持流式响应
- 🛠️ 使用langchain的链、工具、Agent等功能
- 🌐 提供REST API接口
- 📚 支持自定义系统提示和角色设定
- 🔍 集成RAG（检索增强生成）能力

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置API Key

设置环境变量（可选）：
```bash
export QWEN_API_KEY="your-api-key-here"
```

或者直接使用代码中的默认API Key。

### 3. 启动服务

```bash
uvicorn main:app --reload
```

服务将在 `http://127.0.0.1:8000` 启动。

## API接口

### 流式聊天接口

```bash
curl -X POST "http://127.0.0.1:8000/chat/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "message": "你的名字是什么？"
  }'
```

## 项目结构

```
kincog-learner-agent/
├── agent/
│   ├── __init__.py
│   ├── intent.py             # 意图识别
│   ├── llm.py                # LLM初始化
│   ├── memory.py             # 记忆管理
│   ├── rag.py                # 检索增强生成
│   ├── tools.py              # 工具调用
│   └── workflow.py           # LangGraph工作流
├── main.py                   # FastAPI主服务
└── requirements.txt          # 依赖包
```

## 支持的模型

- `qwen-plus`: 通义千问Plus模型
- `qwen-turbo`: 通义千问Turbo模型  
- `qwen-max`: 通义千问Max模型

## 配置说明

### API Key配置

1. 从阿里云获取API Key: https://help.aliyun.com/zh/model-studio/developer-reference/get-api-key
2. 设置环境变量: `export QWEN_API_KEY="your-api-key"`
3. 或在代码中直接指定API Key

### 模型配置

可以在创建LLM实例时指定不同的模型：

```python
from agent.llm import llm

# llm在agent/llm.py中已初始化
```

## 开发说明

- 项目使用langchain框架集成Qwen模型
- 支持OpenAI兼容模式调用Qwen API
- 使用FastAPI框架提供Web服务
- 支持流式响应，提供更好的用户体验
- 模块化设计，便于添加新功能
- 完整的错误处理和日志记录

## 许可证

MIT License