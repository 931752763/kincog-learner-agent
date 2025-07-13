# -*- coding: utf-8 -*-
from typing import Any, Optional

LLM_MAP = {}

try:
    from langchain_openai import OpenAI
    LLM_MAP["openai"] = lambda: OpenAI(temperature=0.3)
except ImportError:
    pass

# 可扩展：
try:
    from langchain_community.llms import Qwen, ChatGLM
    LLM_MAP["qwen"] = lambda: Qwen()
    LLM_MAP["chatglm"] = lambda: ChatGLM()
except ImportError:
    pass

def get_llm(llm_type: Optional[str] = None) -> Any:
    """
    获取LLM对象，支持通过参数选择llm类型，默认openai。
    """
    llm_type = llm_type or "openai"
    if llm_type in LLM_MAP:
        return LLM_MAP[llm_type]()
    raise ImportError(f"未找到LLM类型: {llm_type}，请确认已安装相关依赖包") 