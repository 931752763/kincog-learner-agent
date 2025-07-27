"""
deductive_agent.py

演绎Agent：导入Word文档，生成大纲，分步讲解，支持RAG问答与动态调整。
"""
from typing import List, Any
from docx import Document
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import DashScopeEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document as LCDocument
from agent.llm import llm  # 你的 LLM 实例

# 1. 读取Word文档，按段落分割为LangChain文档对象
def load_word_to_docs(docx_path: str) -> List[LCDocument]:
    doc = Document(docx_path)
    docs = []
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            docs.append(LCDocument(page_content=text))
    return docs

# 2. 构建知识库（RAG向量库）
def build_knowledge_base(docs: List[LCDocument]):
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    splits = splitter.split_documents(docs)
    embeddings = DashScopeEmbeddings(dashscope_api_key="sk-2ccd6eee4dc04773add239ab18db4a8f")
    vectorstore = FAISS.from_documents(splits, embeddings)
    return vectorstore

# 3. 用LLM自动生成演绎大纲
def generate_narrative_outline(docs: List[LCDocument]) -> List[str]:
    context = "\n".join([d.page_content for d in docs[:10]])  # 取前10段做大纲
    prompt = f"请根据以下内容，列出讲解大纲（每一行一个知识点）：\n{context}\n\n大纲："
    result = llm.invoke(prompt)
    outline = [line.strip() for line in result.content.splitlines() if line.strip()]
    return outline

# 4. 用LLM+RAG生成某个知识点的图文讲解
def generate_narrative_step(topic: str, knowledge_base: Any) -> str:
    retriever = knowledge_base.as_retriever(search_kwargs={"k": 3})
    docs = retriever.invoke(topic)
    context = "\n".join([doc.page_content for doc in docs])
    prompt = f"请用通俗易懂的语言，结合以下知识，图文并茂地讲解：\n主题：{topic}\n相关内容：{context}\n\n讲解："
    result = llm.invoke(prompt)
    return result.content

# 5. RAG问答
def answer_question_with_rag(question: str, knowledge_base: Any) -> str:
    retriever = knowledge_base.as_retriever(search_kwargs={"k": 3})
    docs = retriever.invoke(question)
    context = "\n".join([doc.page_content for doc in docs])
    prompt = f"请结合以下知识，简明回答用户问题：\n{context}\n\n问题：{question}\n\n回答："
    result = llm.invoke(prompt)
    return result.content

def generate_intro(docs: list, outline: list) -> str:
    """用LLM生成课程摘要+欢迎语+引导语"""
    context = "\n".join([d.page_content for d in docs[:10]])
    outline_str = "\n".join(outline)
    prompt = (
        f"请根据以下内容，生成一段课程开场白，包含：\n"
        f"1. 对文档知识的核心内容摘要\n"
        f"2. 对学习者的欢迎和鼓励\n"
        f"3. 简要展示教学大纲\n"
        f"4. 以‘准备好和我一起开始学习了吗？’结尾\n\n"
        f"文档内容：\n{context}\n\n大纲：\n{outline_str}\n\n开场白："
    )
    result = llm.invoke(prompt)
    return result.content