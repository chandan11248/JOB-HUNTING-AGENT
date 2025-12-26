"""Composer node for generating the final job application PDF."""

from agent.state import JobAgentState
from tools.pdf_composer import compose_docs
import os


def composer_node(state: JobAgentState) -> dict:
    """Compose the customized resume and cover letter into a professional PDF.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with composed_pdf_path and response
    """
    custom_resume = state.get("customized_resume")
    cover_letter = state.get("cover_letter")
    
    if not custom_resume or not cover_letter:
        return {
            "response": "❌ No customized resume or cover letter found. Please use /customize first.",
            "error": "Missing documents for composition"
        }
    
    try:
        # Generate the PDF
        pdf_path = compose_docs(state)
        
        if os.path.exists(pdf_path):
            return {
                "composed_pdf_path": pdf_path,
                "response": "✨ **Professional Job Application Composed!**\n\nI've combined your customized resume and cover letter into a well-managed PDF. Sending the file to you now...",
                "error": None
            }
        else:
            return {
                "response": "❌ Failed to generate PDF document.",
                "error": "File not created"
            }
            
    except Exception as e:
        return {
            "response": f"❌ Error composing document: {str(e)}",
            "error": str(e)
        }
