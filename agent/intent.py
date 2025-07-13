# -*- coding: utf-8 -*-
# 预设意图关键字
INTENT_KEYWORDS = {
    "qa": ["什么", "为什么", "如何", "解释", "原理", "原因"],
    "search": ["查找", "资料", "搜索", "文献", "推荐"],
    "homework": ["作业", "批改", "评分", "提交"],
    "tool_call": ["计算", "画图", "工具", "转换"]
}

# 兜底意图
DEFAULT_INTENT = "other"

def detect_intent(message: str) -> str:
    for intent, keywords in INTENT_KEYWORDS.items():
        for kw in keywords:
            if kw in message:
                return intent
    # 兜底：调用LLM识别（此处预留，实际可接入LLM）
    # intent = llm_intent_recognize(message)
    return DEFAULT_INTENT 