"""Exporter node for Google Sheets export."""

from agent.state import JobAgentState
from tools.sheets_writer import SheetsWriter


def exporter_node(state: JobAgentState) -> dict:
    """Export jobs to Google Sheets.
    
    Args:
        state: Current state with jobs_found
        
    Returns:
        Updated state with export status
    """
    jobs = state.get("jobs_found", [])
    
    if not jobs:
        return {
            "response": "❌ No jobs to export. Use /search first to find jobs.",
            "error": "No jobs to export"
        }
    
    try:
        writer = SheetsWriter()
        
        if writer.error:
            return {
                "response": f"❌ Google Sheets error: {writer.error}\n\n💡 Ensure your sheet is shared as 'Editor' with the service account email or 'Anyone with the link: Editor'.",
                "error": writer.error
            }
        
        if not writer.client:
            return {
                "response": "❌ Google Sheets client not initialized. Check your credentials.",
                "error": "Sheets not initialized"
            }
        
        # Export jobs
        count = writer.add_jobs_batch(jobs)
        sheet_url = writer.get_sheet_url()
        
        if count > 0:
            return {
                "sheets_exported": True,
                "sheets_url": sheet_url,
                "response": f"""✅ **Exported {count} jobs to Google Sheets!**

📊 [Open your spreadsheet]({sheet_url})

💡 Data was inserted at the top of the sheet (Row 2). 
If it's not appearing, please check for a tab named **'Jobs'** at the bottom.
""",
                "error": None
            }
        else:
            return {
                "response": f"❌ Failed to export jobs. Found {len(jobs)} jobs in session, but could not write to sheet. Check your Google Sheets permissions and tab name ('Jobs').",
                "error": "Export failed"
            }
            
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Export Error:\n{error_details}")
        return {
            "response": f"❌ Export error: {str(e)}\n\nPlease ensure your Google Sheet is shared as 'Editor' with the service account email.",
            "error": str(e)
        }
