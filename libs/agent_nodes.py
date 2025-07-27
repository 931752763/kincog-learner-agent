"""
agent_nodes.py

本模块定义多智能体系统中的所有 Agent 节点。
"""
from typing import Dict, Any
from libs.state import AgentState
from libs.deductive_agent import (
    generate_narrative_step,
    answer_question_with_rag,
)

# === 演绎 Agent 节点 ===
def deductive_agent_node(state: AgentState) -> Dict[str, Any]:
    """
    演绎 Agent 节点：根据大纲和当前步骤生成图文内容，并追加到消息。
    支持用户中断提问，Agent 用RAG回答并动态调整大纲。
    讲解时结合最近一次用户疑问。
    """
    outline = state.get("narrative_outline", [])
    step = state.get("current_step", 0)
    knowledge_base = state.get("knowledge_base")
    messages = state.get("messages", [])

    # 检查最近一次用户疑问（非继续类，且不是空字符串）
    last_user_question = None
    if messages:
        for msg in reversed(messages):
            role = msg.get("role") if isinstance(msg, dict) else getattr(msg, "role", None)
            content = msg.get("content") if isinstance(msg, dict) else getattr(msg, "content", "")
            if role == "user" and content.strip() and content.lower() not in {"c", "continue", "继续", "开始", "好的", "ok", "yes"}:
                last_user_question = content
                break
    # 正常演绎流程，结合最近一次用户疑问
    if step < len(outline):
        topic = outline[step]
    else:
        topic = "[无主题]"
    # 让LLM结合最近一次用户疑问讲解（仅当有疑问且不是继续类内容时）
    if last_user_question:
        narrative = generate_narrative_step(f"{topic}，并要注意用户刚才的问题，可以稍微侧重：{last_user_question}", knowledge_base)
    else:
        narrative = generate_narrative_step(topic, knowledge_base)
    message = {
        "role": "assistant",
        "agent_type": "deductive_agent",
        "content": narrative,
        "step": step
    }
    new_messages = messages + [message]
    new_step = step + 1
    return {
        "messages": new_messages,
        "current_step": new_step
    }

# === 问答 Agent 节点 ===
def qa_agent_node(state: AgentState) -> Dict[str, Any]:
    """
    问答 Agent 节点：对最新用户问题进行 RAG 问答，并追加到消息。
    回答后自动追加引导消息。
    """
    from libs.deductive_agent import answer_question_with_rag
    # 获取最新用户问题
    user_question = None
    for msg in reversed(state["messages"]):
        role = msg.get("role") if isinstance(msg, dict) else getattr(msg, "role", None)
        content = msg.get("content") if isinstance(msg, dict) else getattr(msg, "content", "")
        if role == "user":
            user_question = content
            break
    if not user_question:
        answer = "[未检测到用户问题]"
    else:
        answer = answer_question_with_rag(user_question, state["knowledge_base"])
    message = {
        "role": "assistant",
        "agent_type": "qa_agent",
        "content": answer
    }
    # 自动追加引导消息
    guide_message = {
        "role": "assistant",
        "agent_type": "qa_agent",
        "content": "是否明白？不明白请继续提问，明白了请输入‘继续’进入下一个知识点。"
    }
    new_messages = state["messages"] + [message, guide_message]
    return {
        "messages": new_messages
    }

# === 测试 Agent 节点 ===
def testing_agent_node(state: AgentState) -> Dict[str, Any]:
    """
    测试 Agent 节点：返回占位消息。
    """
    message = {
        "role": "assistant",
        "agent_type": "testing_agent",
        "content": "[功能开发中]"
    }
    new_messages = state["messages"] + [message]
    return {
        "messages": new_messages
    } 