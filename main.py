"""
main.py

多智能体系统主入口，基于 LangGraph 构建。

"""
from langgraph.graph import StateGraph, END
from libs.state import AgentState
from libs.agent_nodes import (
    introduction_agent_node,
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
workflow.add_node("introduction_agent", introduction_agent_node)
workflow.add_node("deductive_agent", deductive_agent_node)
workflow.add_node("qa_agent", qa_agent_node)
workflow.add_node("testing_agent", testing_agent_node)

# 设置入口点
workflow.set_entry_point("introduction_agent")

# 添加路由逻辑：每个 Agent 完成后回到 master_router 决策
workflow.add_conditional_edges(
    "introduction_agent",
    master_router,
    {
        "introduction_agent": "introduction_agent",
        "deductive_agent": "deductive_agent",
        "qa_agent": "qa_agent",
        "testing_agent": "testing_agent",
        "__end__": END,
    },
)
workflow.add_conditional_edges(
    "deductive_agent",
    master_router,
    {
        "introduction_agent": "introduction_agent",
        "deductive_agent": "deductive_agent",
        "qa_agent": "qa_agent",
        "testing_agent": "testing_agent",
        "__end__": END,
    },
)
workflow.add_conditional_edges(
    "qa_agent",
    master_router,
    {
        "introduction_agent": "introduction_agent",
        "deductive_agent": "deductive_agent",
        "qa_agent": "qa_agent",
        "testing_agent": "testing_agent",
        "__end__": END,
    },
)
workflow.add_conditional_edges(
    "testing_agent",
    master_router,
    {
        "introduction_agent": "introduction_agent",
        "deductive_agent": "deductive_agent",
        "qa_agent": "qa_agent",
        "testing_agent": "testing_agent",
        "__end__": END,
    },
)

# 编译为可执行 app
app = workflow.compile()

# ========== 交互主循环 ==========

 

if __name__ == "__main__":
    print("欢迎使用多智能体系统！输入 'exit' 退出。\n")
    docx_path = "/Users/amstroy/Downloads/0205-2稿/说明书_副本.docx"
    docs = load_word_to_docs(docx_path)
    knowledge_base = build_knowledge_base(docs)
    narrative_outline = generate_narrative_outline(docs)
    # 初始化 AgentState
    state: AgentState = {
        "messages": [],
        "knowledge_base": knowledge_base,
        "narrative_outline": narrative_outline,
        "current_step": 0,
        # 测试相关状态初始化
        "test_questions": [],
        "test_answers": [],
        "test_score": 0,
        "test_mode": False,
    }
    
    # 主循环：交互式对话
    current_agent = "introduction"  # 跟踪当前活跃的Agent
    
    while True:
        # 检查是否需要显示介绍
        if not state.get("messages"):
            print("[DEBUG] 首次进入，显示介绍")
            # 手动调用介绍Agent
            intro_result = introduction_agent_node(state)
            state.update(intro_result)
            new_msgs = intro_result.get("messages", [])
            if new_msgs:
                last_msg = new_msgs[-1]
                content = last_msg.get("content", "")
                print(f"[助手] {content}")
            current_agent = "introduction"
        
        # 等待用户输入
        user_input = input("你: ").strip()
        if user_input.lower() in {"exit", "quit", "q"}:
            print("再见！")
            break
        
        # 只追加非空输入
        if user_input:
            state["messages"].append({"role": "user", "content": user_input})
        
        # 智能Agent选择逻辑
        if current_agent == "introduction":
            # 在介绍阶段
            if user_input.lower() in {"c", "continue", "继续", "开始", "好的", "ok", "yes"}:
                # 用户想开始学习，切换到演绎Agent
                print("[DEBUG] 用户选择开始学习，切换到演绎Agent")
                deductive_result = deductive_agent_node(state)
                state.update(deductive_result)
                new_msgs = deductive_result.get("messages", [])
                # 显示所有新生成的消息（讲课内容 + 引导消息）
                for msg in new_msgs:
                    if msg.get("role") == "assistant" and msg.get("agent_type") == "deductive_agent":
                        content = msg.get("content", "")
                        print(f"[老师] {content}")
                current_agent = "deductive"
            else:
                # 用户提问，继续使用介绍Agent回答
                print("[DEBUG] 用户提问，介绍Agent回答")
                intro_result = introduction_agent_node(state)
                state.update(intro_result)
                new_msgs = intro_result.get("messages", [])
                if new_msgs:
                    last_msg = new_msgs[-1]
                    content = last_msg.get("content", "")
                    print(f"[助手] {content}")
        
        elif current_agent == "deductive":
            # 在演绎阶段（老师模式）
            if user_input.lower() in {"c", "continue", "继续", "好的", "ok", "yes"}:
                # 用户想继续学习，继续使用演绎Agent
                print("[DEBUG] 用户想继续学习，演绎Agent继续讲课")
                deductive_result = deductive_agent_node(state)
                state.update(deductive_result)
                new_msgs = deductive_result.get("messages", [])
                # 显示所有新生成的消息（讲课内容 + 引导消息）
                for msg in new_msgs:
                    if msg.get("role") == "assistant" and msg.get("agent_type") == "deductive_agent":
                        content = msg.get("content", "")
                        print(f"[老师] {content}")
            elif user_input.lower() in {"回顾", "review", "back"}:
                # 用户想回顾前面的内容
                print("[DEBUG] 用户想回顾内容")
                # 这里可以添加回顾逻辑，暂时简单处理
                review_message = {
                    "role": "assistant",
                    "agent_type": "deductive_agent",
                    "content": "📋 回顾功能正在开发中，您可以输入'继续'继续学习，或者直接提问。"
                }
                state["messages"].append(review_message)
                print(f"[老师] {review_message['content']}")
            elif user_input.lower() in {"测验", "test", "测试"}:
                # 用户想进行测验，切换到测试Agent
                print("[DEBUG] 用户选择测验，切换到测试Agent")
                testing_result = testing_agent_node(state)
                state.update(testing_result)
                new_msgs = testing_result.get("messages", [])
                for msg in new_msgs:
                    if msg.get("role") == "assistant" and msg.get("agent_type") == "testing_agent":
                        content = msg.get("content", "")
                        print(f"[测验] {content}")
                current_agent = "testing"
            else:
                # 用户提问，切换到问答Agent
                print("[DEBUG] 用户提问，切换到问答Agent")
                qa_result = qa_agent_node(state)
                state.update(qa_result)
                new_msgs = qa_result.get("messages", [])
                # 显示所有新生成的消息（问答内容 + 引导消息）
                for msg in new_msgs:
                    if msg.get("role") == "assistant" and msg.get("agent_type") == "qa_agent":
                        content = msg.get("content", "")
                        print(f"[老师] {content}")
                # 问答后，切换到问答模式，等待用户选择下一步
                current_agent = "qa"
        
        elif current_agent == "qa":
            # 在问答阶段，用户可以继续提问、选择测验、回顾或继续学习
            if user_input.lower() in {"c", "continue", "继续", "好的", "ok", "yes"}:
                # 用户想继续学习，切换回演绎Agent并讲解下一个知识点
                print("[DEBUG] 用户选择继续学习，切换回演绎Agent")
                deductive_result = deductive_agent_node(state)
                state.update(deductive_result)
                new_msgs = deductive_result.get("messages", [])
                # 显示所有新生成的消息（讲课内容 + 引导消息）
                for msg in new_msgs:
                    if msg.get("role") == "assistant" and msg.get("agent_type") == "deductive_agent":
                        content = msg.get("content", "")
                        print(f"[老师] {content}")
                current_agent = "deductive"
            elif user_input.lower() in {"测验", "test", "测试"}:
                # 用户想进行测验，切换到测试Agent
                print("[DEBUG] 用户选择测验，切换到测试Agent")
                testing_result = testing_agent_node(state)
                state.update(testing_result)
                new_msgs = testing_result.get("messages", [])
                for msg in new_msgs:
                    if msg.get("role") == "assistant" and msg.get("agent_type") == "testing_agent":
                        content = msg.get("content", "")
                        print(f"[测验] {content}")
                current_agent = "testing"
            elif user_input.lower() in {"回顾", "review", "back"}:
                # 用户想回顾前面的内容
                print("[DEBUG] 用户想回顾内容")
                review_message = {
                    "role": "assistant",
                    "agent_type": "qa_agent",
                    "content": "📋 回顾功能正在开发中，您可以输入'继续'继续学习，或者直接提问。"
                }
                state["messages"].append(review_message)
                print(f"[老师] {review_message['content']}")
            else:
                # 用户继续提问，继续使用问答Agent
                print("[DEBUG] 用户继续提问，问答Agent回答")
                qa_result = qa_agent_node(state)
                state.update(qa_result)
                new_msgs = qa_result.get("messages", [])
                for msg in new_msgs:
                    if msg.get("role") == "assistant" and msg.get("agent_type") == "qa_agent":
                        content = msg.get("content", "")
                        print(f"[老师] {content}")
        
        elif current_agent == "testing":
            # 在测试阶段
            # 先检查用户是否想直接退出测试模式
            if user_input.lower() in {"c", "continue", "继续", "好的", "ok"} and not state.get("test_mode", False):
                # 用户想继续学习，使用智能分析后切换回演绎Agent
                print("[DEBUG] 用户选择继续学习，从测试模式切换回演绎Agent")
                
                # 导入智能分析函数
                from libs.deductive_agent import analyze_test_results_and_questions
                
                # 进行智能分析
                analysis_keywords = analyze_test_results_and_questions(state)
                print(f"[DEBUG] 智能分析结果: {analysis_keywords}")
                
                # 将分析结果作为"用户疑问"传递给演绎Agent
                # 临时添加一个分析消息到状态中
                analysis_message = {
                    "role": "user",
                    "content": f"请结合我的测验情况和学习疑问，重点关注：{analysis_keywords}"
                }
                state["messages"].append(analysis_message)
                
                deductive_result = deductive_agent_node(state)
                state.update(deductive_result)
                new_msgs = deductive_result.get("messages", [])
                # 显示所有新生成的消息（讲课内容 + 引导消息）
                for msg in new_msgs:
                    if msg.get("role") == "assistant" and msg.get("agent_type") == "deductive_agent":
                        content = msg.get("content", "")
                        print(f"[老师] {content}")
                current_agent = "deductive"
            else:
                # 正常的测试流程处理
                print("[DEBUG] 用户在测试模式下输入")
                testing_result = testing_agent_node(state)
                state.update(testing_result)
                new_msgs = testing_result.get("messages", [])
                for msg in new_msgs:
                    if msg.get("role") == "assistant" and msg.get("agent_type") == "testing_agent":
                        content = msg.get("content", "")
                        print(f"[测验] {content}")
                
                # 检查是否退出测试模式
                if not state.get("test_mode", False):
                    # 测试完成，等待用户选择下一步
                    pass
        
        print("--- 本轮结束 ---\n")