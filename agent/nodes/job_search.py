"""Job search node using Jooble API - Synchronous version."""

from agent.state import JobAgentState
from tools.jooble_api import JoobleAPI


def job_search_node(state: JobAgentState) -> dict:
    """Search for jobs using Jooble API.
    
    Args:
        state: Current agent state with search_query and location
        
    Returns:
        Updated state with jobs_found and response
    """
    query = state.get("search_query", "")
    location = state.get("location", "remote")
    
    if not query:
        return {
            "response": "❌ Please provide search keywords.\nExample: /search python developer remote",
            "error": "No search query provided"
        }
    
    # Synchronous search
    api = JoobleAPI()
    result = api.search_jobs(query, location)
    
    if "error" in result:
        return {
            "response": f"❌ Search failed: {result['error']}",
            "error": result["error"],
            "jobs_found": []
        }
    
    jobs = result.get("jobs", [])
    total = result.get("totalCount", 0)
    
    if not jobs:
        return {
            "response": f"🔍 No jobs found for '{query}' in '{location}'.\nTry different keywords or location.",
            "jobs_found": [],
            "error": None
        }
    
    # Format jobs for display
    formatted = f"🔍 *Found {total} recent jobs (last 3 days) for '{query}' in '{location}':*\n\n"
    
    for i, job in enumerate(jobs[:10], 1):  # Show top 10
        formatted += api.format_job(job, i) + "\n"
    
    formatted += "\n💡 Reply with /customize <number> to customize your resume for a job."
    
    return {
        "jobs_found": jobs[:10],  # Store top 10
        "response": formatted,
        "error": None
    }
