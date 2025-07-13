# -*- coding: utf-8 -*-
from langgraph.graph import StateGraph
from .intent import detect_intent
from .rag import rag_search
from .tools import tool_router
from .memory import get_user_memory
from .llm import get_llm

# 预留意图类型
INTENTS = ["qa", "search", "homework", "tool_call", "other"]

def router_node(input_data):
    """
    Router节点，先关键字识别意图，失败后用LLM识别。
    """
    intent = detect_intent(input_data["message"])
    return {"intent": intent, **input_data}

# 各意图节点预留

def qa_node(input_data):
    # 答疑意图，走RAG
    return rag_search(input_data)

def search_node(input_data):
    # 查资料意图，走RAG
    return rag_search(input_data)

def homework_node(input_data):
    # 作业批改意图，预留
    return {"result": "作业批改功能开发中...", **input_data}

def tool_call_node(input_data):
    # 工具调用意图
    return tool_router(input_data)

def other_node(input_data):
    # 兜底意图
    return {"result": "暂未识别到你的意图，请详细描述。", **input_data}

# workflow定义
def build_agent_workflow():
    sg = StateGraph()
    sg.add_node("router", router_node)
    sg.add_node("qa", qa_node)
    sg.add_node("search", search_node)
    sg.add_node("homework", homework_node)
    sg.add_node("tool_call", tool_call_node)
    sg.add_node("other", other_node)
    # router根据intent路由
    sg.add_edge("router", lambda x: x["intent"])
    sg.add_edge("qa", "end")
    sg.add_edge("search", "end")
    sg.add_edge("homework", "end")
    sg.add_edge("tool_call", "end")
    sg.add_edge("other", "end")
    return sg

def run_agent_workflow(user_id, message):
    # 获取用户memory
    memory = get_user_memory(user_id)
    # 获取llm
    llm = get_llm()
    # 构造输入
    input_data = {"user_id": user_id, "message": message, "memory": memory, "llm": llm}
    workflow = build_agent_workflow()
    result = workflow.run(input_data)
    return result 