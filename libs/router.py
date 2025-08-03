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
        print(f"[DEBUG] Router: 无用户消息，返回 __end__")
        return "__end__"  # 没有用户输入时结束工作流，等待用户输入
    content = user_message.strip().lower()
    print(f"[DEBUG] Router: 用户输入='{user_message}'，处理后='{content}'")
    # 终止条件
    if content in {"exit", "quit", "q"}:
        print(f"[DEBUG] Router: 终止条件，返回 END")
        return END
    # 只有输入"继续/开始/c/好的/ok/yes"才切换到演绎Agent
    if content in {"c", "continue", "继续", "开始", "好的", "ok", "yes"}:
        print(f"[DEBUG] Router: 开始学习，返回 deductive_agent")
        return "deductive_agent"
    # 其他情况默认走介绍Agent（多轮交互）
    print(f"[DEBUG] Router: 其他情况，返回 introduction_agent")
    return "introduction_agent" 