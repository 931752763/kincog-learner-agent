from typing import TypedDict, List, Any, Annotated
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages: Annotated[List[Any], add_messages]
    knowledge_base: Any
    narrative_outline: List[Any]
    current_step: int
    # 测试相关状态
    test_questions: List[Any]  # 当前测试题目
    test_answers: List[str]    # 用户答案
    test_score: int           # 测试得分
    test_mode: bool          # 是否在测试模式