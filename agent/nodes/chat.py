"""Chat node for general conversation and career advice."""

from agent.state import JobAgentState
from tools.groq_llm import GroqLLM


def chat_node(state: JobAgentState) -> dict:
    """Handle general conversation and provide career/job advice.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with response
    """
    messages = state.get("messages", [])
    resume = state.get("base_resume", "No resume uploaded.")
    jobs = state.get("jobs_found", [])
    
    # Format context for the LLM
    context = f"Candidate's Resume:\n{resume}\n\n"
    
    if jobs:
        context += "Found Jobs:\n"
        for i, job in enumerate(jobs, 1):
            context += f"{i}. {job.get('title')} at {job.get('company')} ({job.get('location')})\n"
    else:
        context += "No jobs currently found in the session."
        
    try:
        llm = GroqLLM()
        response = llm.chat(messages, context)
        
        return {
            "response": response,
            "error": None
        }
        
    except Exception as e:
        return {
            "response": f"❌ Error in chat: {str(e)}",
            "error": str(e)
        }
