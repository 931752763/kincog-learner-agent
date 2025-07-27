from typing import TypedDict, List, Any, Annotated
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages: Annotated[List[Any], add_messages]
    knowledge_base: Any
    narrative_outline: List[Any]
    current_step: int 