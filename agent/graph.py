"""LangGraph workflow definition for the Job Agent."""

from langgraph.graph import StateGraph, END
from agent.state import JobAgentState
from agent.nodes.router import router_node
from agent.nodes.job_search import job_search_node
from agent.nodes.customizer import customizer_node
from agent.nodes.exporter import exporter_node
from agent.nodes.chat import chat_node
from agent.nodes.more_jobs import more_jobs_node
from agent.nodes.composer import composer_node


def route_action(state: JobAgentState) -> str:
    """Route to the appropriate node based on current action.
    
    Args:
        state: Current agent state
        
    Returns:
        Name of the next node to execute
    """
    action = state.get("current_action", "")
    
    if action == "search":
        return "job_search"
    elif action == "customize":
        return "customizer"
    elif action == "export":
        return "exporter"
    elif action == "chat":
        return "chat"
    elif action == "more":
        return "more"
    elif action == "compose":
        return "composer"
    elif action == "help":
        return END
    elif action == "start":
        return END
    else:
        return END


def create_job_agent_graph() -> StateGraph:
    """Create the LangGraph workflow for the job agent.
    
    Returns:
        Compiled StateGraph
    """
    # Create the graph
    workflow = StateGraph(JobAgentState)
    
    # Add nodes
    workflow.add_node("router", router_node)
    workflow.add_node("job_search", job_search_node)
    workflow.add_node("customizer", customizer_node)
    workflow.add_node("exporter", exporter_node)
    workflow.add_node("chat", chat_node)
    workflow.add_node("more", more_jobs_node)
    workflow.add_node("composer", composer_node)
    
    # Set entry point
    workflow.set_entry_point("router")
    
    # Add conditional edges from router
    workflow.add_conditional_edges(
        "router",
        route_action,
        {
            "job_search": "job_search",
            "customizer": "customizer",
            "exporter": "exporter",
            "chat": "chat",
            "more": "more",
            "composer": "composer",
            END: END
        }
    )
    
    # All action nodes end the workflow after completion
    workflow.add_edge("job_search", END)
    workflow.add_edge("customizer", END)
    workflow.add_edge("exporter", END)
    workflow.add_edge("chat", END)
    workflow.add_edge("more", END)
    workflow.add_edge("composer", END)
    
    return workflow.compile()


# Create the compiled graph
job_agent = create_job_agent_graph()
