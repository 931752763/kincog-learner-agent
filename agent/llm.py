# -*- coding: utf-8 -*-
from langchain_community.chat_models.tongyi import ChatTongyi

# Initialize the Qwen LLM
llm = ChatTongyi(
    model="qwen-max",
    api_key="sk-2ccd6eee4dc04773add239ab18db4a8f",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)