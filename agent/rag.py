# -*- coding: utf-8 -*-
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import DashScopeEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def setup_rag():
    """Set up the RAG system with sample documents"""
    # Sample documents for demonstration
    documents = [
        Document(page_content="你的名字是kincog-learner-agent")
    ]
    
    # Split documents
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    splits = text_splitter.split_documents(documents)
    
    # Create embeddings and vector store
    embeddings = DashScopeEmbeddings(dashscope_api_key="sk-2ccd6eee4dc04773add239ab18db4a8f")
    vectorstore = FAISS.from_documents(splits, embeddings)
    
    return vectorstore

# Initialize RAG
vectorstore = setup_rag()