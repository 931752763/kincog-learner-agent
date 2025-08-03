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

# === 介绍 Agent 节点 ===
def introduction_agent_node(state: AgentState) -> Dict[str, Any]:
    """
    介绍 Agent 节点：负责课程介绍、解答宏观问题、多轮交互。
    直到用户确认开始学习才切换到演绎Agent。
    """
    from libs.deductive_agent import answer_question_with_rag
    messages = state.get("messages", [])
    knowledge_base = state.get("knowledge_base")
    
    # 获取最新用户输入
    user_input = None
    for msg in reversed(messages):
        role = msg.get("role") if isinstance(msg, dict) else getattr(msg, "role", None)
        content = msg.get("content") if isinstance(msg, dict) else getattr(msg, "content", "")
        if role == "user":
            user_input = content
            break
    
    if not user_input:
        # 首次进入介绍Agent，生成课程介绍
        intro_content = (
            "欢迎来到这门课程！我是您的学习助手。\n\n"
            "这门课程将带您深入了解面向边缘场景动态资源的多出口神经网络设计方法和装置。"
            "我们将从基础概念开始，逐步深入到技术细节和实际应用。\n\n"
            "您可以问我关于课程内容、学习方法、预期收获等问题，"
            "或者直接输入'开始'进入正式学习！"
        )
    else:
        # 用RAG回答用户关于课程的宏观问题
        try:
            intro_content = answer_question_with_rag(user_input, knowledge_base)
        except Exception as e:
            intro_content = f"抱歉，我在回答您的问题时遇到了问题：{str(e)}。请重新提问或输入'开始'进入学习。"
    
    # 追加引导消息
    guide_content = (
        "\n\n如果您想了解更多细节，请继续提问；"
        "如果准备开始学习，请输入'开始'或'继续'！"
    )
    
    message = {
        "role": "assistant",
        "agent_type": "introduction_agent",
        "content": intro_content + guide_content
    }
    new_messages = messages + [message]
    return {
        "messages": new_messages
    }

# === 演绎 Agent 节点 ===
def deductive_agent_node(state: AgentState) -> Dict[str, Any]:
    """
    演绎 Agent 节点：像老师一样分步骤讲课，每次讲一个知识点，给学生思考和提问的机会。
    支持用户中断提问，然后继续讲课。
    """
    outline = state.get("narrative_outline", [])
    step = state.get("current_step", 0)
    knowledge_base = state.get("knowledge_base")
    messages = state.get("messages", [])

    # 检查是否已经讲完所有内容
    if step >= len(outline):
        completion_message = {
            "role": "assistant",
            "agent_type": "deductive_agent",
            "content": "🎉 恭喜！我们已经完成了所有知识点的学习。\n\n"
                      "您已经掌握了课程的核心内容。\n"
                      "如果您还有任何问题，随时可以提问！"
        }
        new_messages = messages + [completion_message]
        return {
            "messages": new_messages,
            "current_step": step
        }

    # 获取当前要讲的知识点
    current_topic = outline[step]
    print(f"[DEBUG] 当前步骤: {step}, 当前主题: {current_topic}")
    
    # 检查最近一次用户疑问（非继续类，且不是空字符串）
    last_user_question = None
    if messages:
        for msg in reversed(messages):
            role = msg.get("role") if isinstance(msg, dict) else getattr(msg, "role", None)
            content = msg.get("content") if isinstance(msg, dict) else getattr(msg, "content", "")
            if role == "user" and content.strip() and content.lower() not in {"c", "continue", "继续", "开始", "好的", "ok", "yes"}:
                last_user_question = content
                break

    # 生成讲课内容
    if last_user_question:
        # 结合用户疑问进行讲解
        print(f"[DEBUG] 结合用户疑问生成内容: {last_user_question}")
        narrative = generate_narrative_step(f"{current_topic}，并要注意用户刚才的问题，可以稍微侧重：{last_user_question}", knowledge_base)
    else:
        # 正常讲解当前知识点
        print(f"[DEBUG] 正常生成内容: {current_topic}")
        narrative = generate_narrative_step(current_topic, knowledge_base)
    
    print(f"[DEBUG] 生成的讲课内容长度: {len(narrative) if narrative else 0}")
    if not narrative or narrative.strip() == "":
        narrative = f"关于{current_topic}的内容正在准备中，请稍等..."

    # 添加讲课内容
    lecture_message = {
        "role": "assistant",
        "agent_type": "deductive_agent",
        "content": f"📚 第{step + 1}讲：{current_topic}\n\n{narrative}"
    }
    
    # 添加引导消息，给学生思考和提问的机会
    guide_message = {
        "role": "assistant",
        "agent_type": "deductive_agent",
        "content": f"---\n"
                  f"💭 请思考一下这部分内容，如果有疑问请随时提问！\n"
                  f"📖 如果理解了，请输入'继续'进入第{step + 2}讲。\n"
                  f"📋 如果想回顾前面的内容，请输入'回顾'。\n"
                  f"📝 如果想测试一下掌握情况，请输入'测验'。"
    }
    
    new_messages = messages + [lecture_message, guide_message]
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
        "content": "---\n"
                  "💭 是否明白？不明白请继续提问！\n"
                  "📖 明白了请输入'继续'进入下一个知识点。\n"
                  "📋 如果想回顾前面的内容，请输入'回顾'。\n"
                  "📝 如果想测试一下掌握情况，请输入'测验'。"
    }
    new_messages = state["messages"] + [message, guide_message]
    return {
        "messages": new_messages
    }

# === 测试 Agent 节点 ===
def testing_agent_node(state: AgentState) -> Dict[str, Any]:
    """
    测试 Agent 节点：生成选择题、评分、提供解释。
    支持多轮测试和问答。
    """
    from libs.deductive_agent import generate_test_questions, evaluate_test_answers
    
    messages = state.get("messages", [])
    knowledge_base = state.get("knowledge_base")
    current_step = state.get("current_step", 0)
    outline = state.get("narrative_outline", [])
    
    # 获取最新用户输入
    user_input = None
    for msg in reversed(messages):
        role = msg.get("role") if isinstance(msg, dict) else getattr(msg, "role", None)
        content = msg.get("content") if isinstance(msg, dict) else getattr(msg, "content", "")
        if role == "user":
            user_input = content.strip()
            break
    
    # 检查是否已有测试题目在进行中
    test_questions = state.get("test_questions", [])
    test_answers = state.get("test_answers", [])
    test_mode = state.get("test_mode", False)
    
    if not test_mode or not test_questions:
        # 首次进入测试模式，生成测试题目
        if current_step > 0:
            # 基于已学内容生成测试题
            learned_topics = outline[:current_step]
            test_questions = generate_test_questions(learned_topics, knowledge_base)
        else:
            test_questions = [
                {
                    "question": "这是一道示例题目，请选择正确答案：",
                    "options": ["A. 选项A", "B. 选项B", "C. 选项C", "D. 选项D"],
                    "correct": "A",
                    "explanation": "这是示例解释。"
                }
            ]
        
        # 显示第一道题
        first_question = test_questions[0]
        question_content = f"📝 测验开始！共{len(test_questions)}道题\n\n"
        question_content += f"第1题：{first_question['question']}\n\n"
        for option in first_question['options']:
            question_content += f"{option}\n"
        question_content += f"\n请输入您的答案（A/B/C/D）："
        
        message = {
            "role": "assistant",
            "agent_type": "testing_agent",
            "content": question_content
        }
        new_messages = messages + [message]
        
        return {
            "messages": new_messages,
            "test_questions": test_questions,
            "test_answers": [],
            "test_mode": True,
            "test_score": 0
        }
    
    elif len(test_answers) < len(test_questions):
        # 正在答题过程中
        if user_input and user_input.upper() in ['A', 'B', 'C', 'D']:
            # 记录用户答案
            new_test_answers = test_answers + [user_input.upper()]
            current_question_index = len(new_test_answers)
            
            if current_question_index < len(test_questions):
                # 还有题目，显示下一题
                next_question = test_questions[current_question_index]
                question_content = f"第{current_question_index + 1}题：{next_question['question']}\n\n"
                for option in next_question['options']:
                    question_content += f"{option}\n"
                question_content += f"\n请输入您的答案（A/B/C/D）："
                
                message = {
                    "role": "assistant",
                    "agent_type": "testing_agent",
                    "content": question_content
                }
                new_messages = messages + [message]
                
                return {
                    "messages": new_messages,
                    "test_answers": new_test_answers
                }
            else:
                # 所有题目答完，进行评分
                score, detailed_results = evaluate_test_answers(test_questions, new_test_answers)
                
                result_content = f"🎯 测验完成！您的得分：{score}/{len(test_questions)}\n\n"
                result_content += "📊 详细结果：\n"
                for i, (question, user_ans, is_correct, explanation) in enumerate(detailed_results):
                    status = "✅ 正确" if is_correct else "❌ 错误"
                    result_content += f"第{i+1}题：{status}\n"
                    result_content += f"您的答案：{user_ans} | 正确答案：{question['correct']}\n"
                    result_content += f"解释：{explanation}\n\n"
                
                # 添加后续选项
                result_content += "---\n"
                result_content += "💭 如果有疑问请随时提问！\n"
                result_content += "🔄 输入'重新测验'可以重新开始测试。\n"
                result_content += "📖 输入'继续'回到课程学习。"
                
                message = {
                    "role": "assistant",
                    "agent_type": "testing_agent",
                    "content": result_content
                }
                new_messages = messages + [message]
                
                return {
                    "messages": new_messages,
                    "test_answers": new_test_answers,
                    "test_score": score,
                    "test_mode": False  # 测试完成，退出测试模式
                }
        else:
            # 无效输入，重新提示
            current_question_index = len(test_answers)
            current_question = test_questions[current_question_index]
            
            error_content = f"❌ 请输入有效的选项（A/B/C/D）\n\n"
            error_content += f"第{current_question_index + 1}题：{current_question['question']}\n\n"
            for option in current_question['options']:
                error_content += f"{option}\n"
            error_content += f"\n请输入您的答案（A/B/C/D）："
            
            message = {
                "role": "assistant",
                "agent_type": "testing_agent",
                "content": error_content
            }
            new_messages = messages + [message]
            
            return {
                "messages": new_messages
            }
    
    else:
        # 测试已完成，处理后续交互
        if user_input and "重新测验" in user_input:
            # 重新开始测试
            return testing_agent_node({
                **state,
                "test_questions": [],
                "test_answers": [],
                "test_mode": False,
                "test_score": 0
            })
        elif user_input and user_input.lower() in {"c", "continue", "继续", "好的", "ok"}:
            # 返回学习模式的引导消息
            guide_content = "📚 好的，让我们继续学习吧！请输入'继续'回到课程讲解。"
            message = {
                "role": "assistant",
                "agent_type": "testing_agent",
                "content": guide_content
            }
            new_messages = messages + [message]
            
            return {
                "messages": new_messages,
                "test_mode": False
            }
        else:
            # 用户提问，使用RAG回答
            from libs.deductive_agent import answer_question_with_rag
            try:
                answer = answer_question_with_rag(user_input, knowledge_base)
                answer_content = f"💡 {answer}\n\n"
                answer_content += "还有其他疑问吗？或者输入'继续'回到课程学习，输入'重新测验'重新测试。"
            except Exception as e:
                answer_content = f"抱歉，回答问题时出现错误：{str(e)}\n\n请重新提问，或输入'继续'回到课程学习。"
            
            message = {
                "role": "assistant",
                "agent_type": "testing_agent",
                "content": answer_content
            }
            new_messages = messages + [message]
            
            return {
                "messages": new_messages
            }