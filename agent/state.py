"""Agent state schema for the Job Agent."""

from typing import TypedDict, List, Optional, Annotated
from langgraph.graph import add_messages


class JobAgentState(TypedDict):
    """State schema for the Job Agent LangGraph.
    
    This state is passed between nodes in the graph and maintains
    the conversation context and job search data.
    """
    
    # User identification
    telegram_user_id: str
    
    # User's resume
    base_resume: Optional[str]
    
    # Job search parameters
    search_query: Optional[str]
    location: Optional[str]
    
    # Search results
    jobs_found: List[dict]
    selected_job_index: Optional[int]
    selected_job: Optional[dict]
    
    # Generated documents
    customized_resume: Optional[str]
    cover_letter: Optional[str]
    composed_pdf_path: Optional[str]
    
    # Export status
    sheets_exported: bool
    sheets_url: Optional[str]
    
    # Conversation messages (with reducer for appending)
    messages: Annotated[list, add_messages]
    
    # Current action/command being processed
    current_action: str
    
    # Response to send back to user
    response: str
    
    # Error tracking
    error: Optional[str]


def create_initial_state(user_id: str) -> JobAgentState:
    """Create an initial state for a new user session.
    
    Args:
        user_id: Telegram user ID
        
    Returns:
        Initial JobAgentState
    """
    return JobAgentState(
        telegram_user_id=user_id,
        base_resume=None,
        search_query=None,
        location=None,
        jobs_found=[],
        selected_job_index=None,
        selected_job=None,
        customized_resume=None,
        cover_letter=None,
        composed_pdf_path=None,
        sheets_exported=False,
        sheets_url=None,
        messages=[],
        current_action="",
        response="",
        error=None
    )
