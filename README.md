# kincog-learner-agent

一个基于Qwen模型的智能学习助手项目，使用langchain和langgraph构建。

## 功能特性

- 🤖 集成Qwen大语言模型（通过langchain）
- 💬 支持智能对话和学习指导
- 🔄 支持流式响应
- 🛠️ 使用langchain的链、工具、Agent等功能
- 🌐 提供REST API接口
- 📚 支持自定义系统提示和角色设定

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

### 3. 运行测试

```bash
# 基础测试
python test_qwen_langchain.py

# 使用示例
python example_langchain_qwen.py
```

### 4. 启动服务

```bash
python main.py
```

服务将在 `http://localhost:8000` 启动。

## 使用langchain集成Qwen模型

### 基础使用

```python
from agent.qwen_simple import chat_with_qwen

# 简单对话
response = chat_with_qwen(
    message="你好，请介绍一下你自己",
    system_message="你是一个智能学习助手，请用中文回答。"
)
print(response)
```

### Agent工作流

```python
from agent.qwen_simple import run_qwen_agent

# 使用Agent处理用户消息
result = run_qwen_agent(
    user_id="user123",
    message="请帮我制定一个Python学习计划"
)
print(result['response'])
```

### 自定义角色

```python
# 数学老师角色
math_response = chat_with_qwen(
    message="请解释一下什么是微积分",
    system_message="你是一个数学老师，请用简单易懂的方式解释数学概念。"
)

# 编程导师角色
coding_response = chat_with_qwen(
    message="如何优化Python代码的性能？",
    system_message="你是一个编程导师，请提供实用的编程建议和最佳实践。"
)
```

## API接口

### 流式聊天接口

```bash
curl -X POST "http://localhost:8000/chat/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "message": "请帮我制定一个Python学习计划"
  }'
```

### 普通聊天接口

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123", 
    "message": "什么是机器学习？"
  }'
```

## 项目结构

```
kincog-learner-agent/
├── agent/
│   ├── __init__.py
│   ├── qwen_simple.py        # 简化的Qwen模型集成
│   ├── qwen_langchain.py     # 完整的langchain集成
│   ├── workflow.py           # 原始workflow（使用Claude）
│   ├── intent.py             # 意图识别
│   ├── memory.py             # 记忆管理
│   ├── rag.py               # 检索增强生成
│   └── tools.py              # 工具调用
├── main.py                   # FastAPI主服务
├── test_qwen_langchain.py   # langchain Qwen测试
├── example_langchain_qwen.py # 使用示例
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
from agent.qwen_simple import create_qwen_llm

llm = create_qwen_llm(
    api_key="your-api-key",
    model="qwen-plus"  # 可选: qwen-plus, qwen-turbo, qwen-max
)
```

## langchain集成特性

### 1. 链式调用

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 创建LLM
llm = ChatOpenAI(
    model="qwen-plus",
    api_key="your-api-key",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

# 创建链
template = ChatPromptTemplate.from_messages([
    ("system", "你是一个智能学习助手，请用中文回答。"),
    ("human", "{input}")
])
chain = template | llm | StrOutputParser()

# 使用链
response = chain.invoke({"input": "什么是机器学习？"})
```

### 2. 工具集成

```python
from langchain_core.tools import tool

@tool
def search_knowledge(query: str) -> str:
    """搜索知识库"""
    return f"搜索知识库结果: {query}"

@tool
def calculate(expression: str) -> str:
    """计算数学表达式"""
    try:
        result = eval(expression)
        return f"计算结果: {result}"
    except:
        return f"无法计算表达式: {expression}"
```

### 3. Agent工作流

```python
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict

# 定义状态
class AgentState(TypedDict):
    input: str
    response: str

# 创建workflow
workflow = StateGraph(AgentState)
# ... 添加节点和边
compiled_workflow = workflow.compile()
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
