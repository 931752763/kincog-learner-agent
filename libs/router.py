"""
router.py

本模块定义多智能体系统的主路由函数。
"""
from libs.state import AgentState
from langgraph.graph import END

# === 主路由函数 ===
def master_router(state: AgentState) -> str:
    messages = state.get("messages", [])
    user_message = None
    for msg in reversed(messages):
        role = msg.get("role") if isinstance(msg, dict) else getattr(msg, "role", None)
        content = msg.get("content") if isinstance(msg, dict) else getattr(msg, "content", "")
        if role == "user":
            user_message = content
            break
    if not user_message:
        return "deductive_agent"  # 默认先讲解
    content = user_message.strip().lower()
    # 终止条件
    if content in {"exit", "quit", "q"}:
        return END
    # 只要输入“继续/开始/c/好的/ok/yes”就走演绎Agent
    if content in {"c", "continue", "继续", "开始", "好的", "ok", "yes"}:
        return "deductive_agent"
    # 其它情况默认走问答Agent
    return "qa_agent" 