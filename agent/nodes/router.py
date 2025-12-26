"""Router node for parsing user commands."""

from agent.state import JobAgentState


HELP_MESSAGE = """🤖 **Job Agent Bot Commands**

**/search `<keywords>` `<location>`**
Search for jobs. Example: `/search python developer remote`

**/customize `<job_number>`**
Customize your resume for a specific job from search results.
Example: `/customize 1`

**/compose**
Compose your customized resume and cover letter into a professional PDF for download.

**/export**
Export all found jobs to your Google Sheet.

**/more**
Find more jobs from other platforms (Remotive, etc.) based on your last search.

**/resume**
Upload a new resume (send as file after this command).

**/chat `<any message>`**
Chat with me! Ask for job suggestions, career advice, or why you should apply to certain jobs.

**/help**
Show this help message.

---
💡 **Quick Start:**
1. Upload your resume with /resume
2. Search jobs with /search
3. Pick a job number to customize your resume
4. Compose your professional PDF with /compose
5. Export all jobs to Google Sheets with /export
"""

START_MESSAGE = """👋 **Welcome to Job Agent Bot!**

I help you find jobs, customize your resume, and track applications.

**Before we start:**
1. Make sure your `.env` file has all API keys configured
2. Upload your base resume using /resume

Use /help to see all available commands.

🚀 Ready when you are!
"""


def router_node(state: JobAgentState) -> dict:
    """Route user commands to appropriate actions.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with routing decision
    """
    messages = state.get("messages", [])
    
    if not messages:
        return {
            "current_action": "help",
            "response": HELP_MESSAGE
        }
    
    # Get the last user message
    last_message = messages[-1]
    if hasattr(last_message, 'content'):
        text = last_message.content
    else:
        text = str(last_message)
    
    text = text.strip().lower()
    
    # Parse commands
    if text.startswith("/start"):
        return {
            "current_action": "start",
            "response": START_MESSAGE
        }
    
    elif text.startswith("/help"):
        return {
            "current_action": "help",
            "response": HELP_MESSAGE
        }
    
    elif text.startswith("/search"):
        # Parse search query: /search <keywords> <location>
        parts = text.replace("/search", "").strip().split()
        
        if len(parts) < 1:
            return {
                "current_action": "help",
                "response": "❌ Usage: /search `<keywords>` `<location>`\nExample: /search python developer remote"
            }
        
        # Try to find location (last word if it looks like a location)
        location = "remote"
        keywords = " ".join(parts)
        
        # Common location keywords
        location_keywords = ["remote", "hybrid", "onsite"]
        if parts[-1].lower() in location_keywords or len(parts) > 2:
            location = parts[-1]
            keywords = " ".join(parts[:-1])
        
        return {
            "current_action": "search",
            "search_query": keywords,
            "location": location
        }
    
    elif text.startswith("/customize"):
        # Parse job selection: /customize <number>
        parts = text.replace("/customize", "").strip().split()
        
        if len(parts) < 1:
            return {
                "current_action": "help",
                "response": "❌ Usage: /customize `<job_number>`\nExample: /customize 1"
            }
        
        try:
            job_index = int(parts[0]) - 1  # Convert to 0-indexed
            return {
                "current_action": "customize",
                "selected_job_index": job_index
            }
        except ValueError:
            return {
                "current_action": "help",
                "response": "❌ Please provide a valid job number.\nExample: /customize 1"
            }
    
    elif text.startswith("/export"):
        return {
            "current_action": "export"
        }
    
    elif text.startswith("/resume"):
        return {
            "current_action": "help",
            "response": "📄 Please send your resume file (PDF, DOCX, or TXT) as a reply to this message."
        }
    
    elif text.startswith("/chat"):
        return {
            "current_action": "chat"
        }
    
    elif text.startswith("/more"):
        return {
            "current_action": "more"
        }
    
    elif text.startswith("/compose"):
        return {
            "current_action": "compose"
        }
    
    else:
        # Check if it's a number (job selection shortcut)
        try:
            job_index = int(text) - 1
            return {
                "current_action": "customize",
                "selected_job_index": job_index
            }
        except ValueError:
            pass
        
        # Default to chat for any other input
        return {
            "current_action": "chat"
        }
