# -*- coding: utf-8 -*-
from pydantic import BaseModel
from pydantic import Field
from typing_extensions import Literal
from langchain_core.messages import HumanMessage, SystemMessage
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

from agent.llm import llm
from agent.rag import vectorstore

# Schema for structured output to use as routing logic
 
class Route(BaseModel):
    step: Literal["poem", "story", "joke", "tool"] = Field(
        None, description="The next step in the routing process"
    )

# Augment the LLM with schema for structured output
router = llm.with_structured_output(Route)

# State
class State(TypedDict):
    input: str
    decision: str
    output: str

# Nodes
def llm_call_1(state: State):
    """Write a story with RAG capability"""
    # Retrieve relevant documents
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    docs = retriever.invoke(state["input"])
    
    # Format retrieved context
    context = "\n".join([doc.page_content for doc in docs])
    
    # Create prompt with context
    prompt = f"基于以下背景知识回答问题：\n\n{context}\n\n问题：{state['input']}\n\n回答："
    
    # Generate response
    result = llm.invoke(prompt)
    return {"output": result.content}

def llm_call_2(state: State):
    """Write a joke"""
    result = llm.invoke(state["input"])
    return {"output": result.content}

def llm_call_3(state: State):
    """Write a poem"""
    result = llm.invoke(state["input"])
    return {"output": result.content}

def llm_call_4(state: State):
    """Tool call node"""
    from agent.tools import tool_router
    result = tool_router({"input": state["input"]})
    return {"output": result.get("result", "[工具调用无结果]")}

def llm_call_router(state: State):
    """Route the input to the appropriate node"""
    # Run the augmented LLM with structured output to serve as routing logic
    decision = router.invoke(
        [
            SystemMessage(
                content="Route the input to story, joke, poem, or tool based on the user's request. If the input is a question about machine learning, deep learning, NLP, or Python, route to story. If the input is a tool call, route to tool."
            ),
            HumanMessage(content=state["input"]),
        ]
    )

    # Handle case where decision is None
    if decision is None or decision.step is None:
        return {"decision": "story"}  # Default to story if routing fails

    return {"decision": decision.step}

# Conditional edge function to route to the appropriate node
def route_decision(state: State):
    # Return the node name you want to visit next
    if state["decision"] == "story":
        return "llm_call_1"
    elif state["decision"] == "joke":
        return "llm_call_2"
    elif state["decision"] == "poem":
        return "llm_call_3"
    elif state["decision"] == "tool":
        return "llm_call_4"

# Build workflow
router_builder = StateGraph(State)

# Add nodes
router_builder.add_node("llm_call_1", llm_call_1)
router_builder.add_node("llm_call_2", llm_call_2)
router_builder.add_node("llm_call_3", llm_call_3)
router_builder.add_node("llm_call_router", llm_call_router)
router_builder.add_node("llm_call_4", llm_call_4)

# Add edges to connect nodes
router_builder.add_edge(START, "llm_call_router")
router_builder.add_conditional_edges(
    "llm_call_router",
    route_decision,
    {  # Name returned by route_decision : Name of next node to visit
        "llm_call_1": "llm_call_1",
        "llm_call_2": "llm_call_2",
        "llm_call_3": "llm_call_3",
        "llm_call_4": "llm_call_4",
    },
)

router_builder.add_edge("llm_call_1", END)
router_builder.add_edge("llm_call_2", END)
router_builder.add_edge("llm_call_3", END)
router_builder.add_edge("llm_call_4", END)

# Compile workflow
router_workflow = router_builder.compile()