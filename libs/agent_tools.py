"""
agent_tools.py

本模块用于封装 Agent 的核心功能，便于多智能体系统复用和协同开发。
"""
from typing import Any, List

# === RAG 问答核心逻辑 ===
def answer_question_with_rag(question: str, knowledge_base: Any) -> str:
    """
    使用 RAG 检索器和大模型进行问答。
    参数：
        question: 用户问题
        knowledge_base: 已初始化的 RAG 检索器（如 FAISS 检索器）
    返回：
        回答字符串
    """
    # 检索相关文档
    retriever = knowledge_base.as_retriever(search_kwargs={"k": 3})
    docs = retriever.invoke(question)
    # 整理上下文
    context = "\n".join([doc.page_content for doc in docs])
    # 构建提示词
    prompt = f"基于以下背景知识回答问题：\n\n{context}\n\n问题：{question}\n\n回答："
    # 这里假设你会在调用处传入 LLM 实例
    # result = llm.invoke(prompt)
    # return result.content
    return f"[RAG占位] {prompt}"

# === 生成演绎文案（占位） ===
def generate_narrative_for_topic(topic_title: str) -> str:
    """
    根据主题生成演绎文案（占位实现）。
    参数：
        topic_title: 主题标题
    返回：
        文案字符串
    """
    return f"[占位] 主题《{topic_title}》的演绎文案。"

# === 生成图片链接（占位） ===
def generate_image_for_concept(keywords: List[str]) -> str:
    """
    根据关键词生成图片链接（占位实现）。
    参数：
        keywords: 概念关键词列表
    返回：
        图片链接字符串
    """
    return f"[占位] 概念 {keywords} 的图片链接。" 