from agent.state import JobAgentState
from tools.extra_jobs_api import ExtraJobsAPI
from tools.llm_query_expander import LLMQueryExpander


def more_jobs_node(state: JobAgentState) -> dict:
    """Fetch additional jobs from other platforms with Smart Variety Search.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with additional jobs and response
    """
    query = state.get("search_query")
    
    if not query:
        # Fallback: look through messages for the last search command
        messages = state.get("messages", [])
        for msg in reversed(messages):
            content = getattr(msg, "content", str(msg))
            if content.startswith("/search"):
                parts = content.replace("/search", "").strip().split()
                if parts:
                    query = " ".join(parts[:-1]) if len(parts) > 1 else parts[0]
                    break
    
    if not query:
        return {
            "response": "❌ No previous search found. Please use /search first.",
            "error": "No query found for more jobs"
        }
    
    extra_api = ExtraJobsAPI()
    expander = LLMQueryExpander()
    location = state.get("location", "Remote")
    
    # 1. Expand query into variations for variety
    print(f"Expanding query '{query}' for variety search...")
    variations = expander.expand_query(query)
    print(f"Variations: {variations}")

    all_extra_jobs = []
    seen_links = set()
    
    # Add existing job links to avoid duplicates
    for j in state.get("jobs_found", []):
        seen_links.add(j.get("link"))

    # 2. Search Remotive first for the direct query
    remotive_jobs = extra_api.search_remotive(query)
    for j in remotive_jobs:
        if j.get("link") not in seen_links:
            all_extra_jobs.append(j)
            seen_links.add(j.get("link"))

    # 3. Search Google/LinkedIn for each variation until we hit at least 15 jobs
    for var in variations:
        if len(all_extra_jobs) >= 15:
            break
            
        print(f"Searching for variety: '{var}' in {location}...")
        google_jobs = extra_api.search_google(var, location)
        
        for j in google_jobs:
            if j.get("link") not in seen_links:
                all_extra_jobs.append(j)
                seen_links.add(j.get("link"))
                if len(all_extra_jobs) >= 20: # Cap at 20 to avoid overwhelming
                    break
    
    if not all_extra_jobs:
        return {
            "response": f"🔍 No additional recent jobs found for '{query}' or related fields.",
            "error": None
        }
    
    current_jobs = state.get("jobs_found", [])
    start_index = len(current_jobs) + 1
    
    # Store these extra jobs in the state
    updated_jobs = current_jobs + all_extra_jobs
    
    # Re-format with combined indexing for the response
    variations_str = ", ".join(variations[1:4]) # Show some of the smart terms used
    full_response = f"🚀 **Smart Variety Search for '{query}':**\n"
    full_response += f"💡 Also searched for: _{variations_str}_\n\n"
    
    for i, job in enumerate(all_extra_jobs, start_index):
        full_response += (
            f"{i}. {job['title']}\n"
            f"🏢 {job['company']} (via {job.get('source', 'Other')})\n"
            f"💰 {job.get('salary', 'Not specified')}\n"
            f"🔗 {job['link']}\n\n"
        )
    
    full_response += f"✅ Found {len(all_extra_jobs)} extra jobs! Use /customize <number> to pick one."
    
    return {
        "jobs_found": updated_jobs,
        "response": full_response,
        "error": None
    }
