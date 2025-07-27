"""
main.py

多智能体系统主入口，基于 LangGraph 构建。
"""
from langgraph.graph import StateGraph, END
from libs.state import AgentState
from libs.agent_nodes import (
    deductive_agent_node,
    qa_agent_node,
    testing_agent_node,
)
from libs.router import master_router
from libs.deductive_agent import (
    load_word_to_docs,
    build_knowledge_base,
    generate_narrative_outline,
    generate_intro,
)

# ========== 构建多智能体工作流图 ==========
workflow = StateGraph(AgentState)

# 添加所有 Agent 节点
workflow.add_node("deductive_agent", deductive_agent_node)
workflow.add_node("qa_agent", qa_agent_node)
workflow.add_node("testing_agent", testing_agent_node)

# 设置入口点
workflow.set_entry_point("deductive_agent")

# 添加路由逻辑：每个 Agent 完成后回到 master_router 决策
workflow.add_conditional_edges(
    "deductive_agent",
    master_router,
    {
        "deductive_agent": "deductive_agent",
        "qa_agent": "qa_agent",
        "testing_agent": "testing_agent",
    },
)
workflow.add_conditional_edges(
    "qa_agent",
    master_router,
    {
        "deductive_agent": "deductive_agent",
        "qa_agent": "qa_agent",
        "testing_agent": "testing_agent",
    },
)
workflow.add_conditional_edges(
    "testing_agent",
    master_router,
    {
        "deductive_agent": "deductive_agent",
        "qa_agent": "qa_agent",
        "testing_agent": "testing_agent",
    },
)

# 结束节点
workflow.add_edge("deductive_agent", END)
workflow.add_edge("qa_agent", END)
workflow.add_edge("testing_agent", END)

# 编译为可执行 app
app = workflow.compile()

# ========== 交互主循环 ==========

 

if __name__ == "__main__":
    print("欢迎使用多智能体系统！输入 'exit' 退出。\n")
    # ====== 新增：导入Word文档，初始化知识库和大纲 ======
    # docx_path = input("请输入知识Word文档路径（如 knowledge.docx ）: ").strip()
    docx_path = "/Users/amstroy/Downloads/0205-2稿/说明书.docx"
    docs = load_word_to_docs(docx_path)
    knowledge_base = build_knowledge_base(docs)
    narrative_outline = generate_narrative_outline(docs)
    # ====== 生成并输出开场白 ======
    intro = generate_intro(docs, narrative_outline)
    print(f"[assistant] {intro}\n")
    # ====== 等待用户确认 ======
    print("[assistant] 只要你准备好了，输入 '开始' 或 'c' 即可进入正式学习！\n")
    while True:
        user_input = input("你: ").strip()
        if user_input.lower() in {"exit", "quit", "q"}:
            print("再见！")
            exit(0)
        if user_input.lower() in {"c", "continue", "继续", "开始", "好的", "ok", "yes"}:
            break
        
    # 初始化 AgentState
    state: AgentState = {
        "messages": [],
        "knowledge_base": knowledge_base,
        "narrative_outline": narrative_outline,
        "current_step": 0,
    }
    while True:
        user_input = input("你: ").strip()
        if user_input.lower() in {"exit", "quit", "q"}:
            print("再见！")
            break
        # 只追加非空输入
        if user_input:
            state["messages"].append({"role": "user", "content": user_input})
        # 只处理一次 agent 节点，兼容 {node_name: output_dict} 结构
        step_iter = app.stream(state)
        for step in step_iter:
            if isinstance(step, dict) and len(step) == 1:
                node_name, result = next(iter(step.items()))
                new_msgs = result.get("messages", [])
                if new_msgs:
                    last_msg = new_msgs[-1]
                    role = last_msg.get("role", "agent")
                    content = last_msg.get("content", "")
                    print(f"[{role}] {content}")
                state.update(result)
        print("--- 本轮结束 ---\n") 