"""Customizer node for resume and cover letter generation - Synchronous version."""

from agent.state import JobAgentState
from tools.groq_llm import GroqLLM


def customizer_node(state: JobAgentState) -> dict:
    """Customize resume and generate cover letter for selected job.
    
    Args:
        state: Current state with selected_job_index and base_resume
        
    Returns:
        Updated state with customized_resume and cover_letter
    """
    job_index = state.get("selected_job_index")
    jobs = state.get("jobs_found", [])
    resume = state.get("base_resume")
    
    # Validate inputs
    if job_index is None:
        return {
            "response": "❌ No job selected. Use /customize <number> after searching.",
            "error": "No job selected"
        }
    
    if not jobs:
        return {
            "response": "❌ No jobs in search results. Use /search first.",
            "error": "No jobs found"
        }
    
    if job_index < 0 or job_index >= len(jobs):
        return {
            "response": f"❌ Invalid job number. Please choose 1-{len(jobs)}.",
            "error": "Invalid job index"
        }
    
    if not resume:
        return {
            "response": "❌ No resume uploaded. Please send your resume file first with /resume.",
            "error": "No resume"
        }
    
    selected_job = jobs[job_index]
    
    # Format job description
    job_desc = f"""
Title: {selected_job.get('title', '')}
Company: {selected_job.get('company', '')}
Location: {selected_job.get('location', '')}
Description: {selected_job.get('snippet', '')}
"""
    
    # Generate customized documents
    try:
        llm = GroqLLM()
        
        # Generate resume and cover letter (synchronous)
        customized_resume = llm.customize_resume(resume, job_desc)
        cover_letter = llm.generate_cover_letter(
            resume, job_desc, selected_job.get('company', 'the company')
        )
        
        # Format response
        job_title = selected_job.get('title', 'Unknown')
        company = selected_job.get('company', 'Unknown')
        
        response = f"""✅ *Documents Generated for {job_title} at {company}*

📄 *Customized Resume:*
{customized_resume[:2000]}...

📝 *Cover Letter:*
{cover_letter[:1500]}...

💡 Use /export to save all jobs to Google Sheets.
🔗 Apply here: {selected_job.get('link', 'N/A')}
"""
        
        return {
            "selected_job": selected_job,
            "customized_resume": customized_resume,
            "cover_letter": cover_letter,
            "response": response,
            "error": None
        }
        
    except Exception as e:
        return {
            "response": f"❌ Error generating documents: {str(e)}",
            "error": str(e)
        }
