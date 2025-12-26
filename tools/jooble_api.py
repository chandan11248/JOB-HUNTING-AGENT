"""Jooble Job Search API wrapper - Synchronous version."""

import requests
from datetime import datetime
from typing import Optional
from config import Config


class JoobleAPI:
    """Synchronous wrapper for Jooble Job Search API."""
    
    def __init__(self):
        self.api_key = Config.JOOBLE_API_KEY
        self.base_url = f"{Config.JOOBLE_API_URL}{self.api_key}"
    
    def search_jobs(
        self,
        keywords: str,
        location: Optional[str] = None,
        radius: Optional[int] = None,
        salary: Optional[int] = None,
        page: int = 1
    ) -> dict:
        """Search for jobs on Jooble.
        
        Args:
            keywords: Job search keywords (e.g., "python developer")
            location: Location to search in (e.g., "New York" or "remote")
            radius: Search radius in km (0, 4, 8, 16, 26, 40, 80)
            salary: Minimum salary filter
            page: Page number for pagination
            
        Returns:
            Dict containing jobs list and total count
        """
        payload = {
            "keywords": keywords,
            "location": location or Config.DEFAULT_LOCATION,
            "page": page
        }
        
        if radius is not None:
            payload["radius"] = radius
        if salary is not None:
            payload["salary"] = salary
        
        try:
            response = requests.post(
                self.base_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                raw_jobs = data.get("jobs", [])
                
                # Filter for recent jobs (e.g., last 3 days)
                recent_jobs = []
                now = datetime.now()
                for job in raw_jobs:
                    updated_str = job.get("updated")
                    if updated_str:
                        try:
                            # Try to parse Jooble date format (often "2023-11-25T12:00:00")
                            # If it's just "2023-11-25", we handle that too
                            if "T" in updated_str:
                                updated_dt = datetime.fromisoformat(updated_str.split(".")[0])
                            else:
                                updated_dt = datetime.strptime(updated_str, "%Y-%m-%d")
                            
                            delta = now - updated_dt
                            if delta.days <= 3:
                                recent_jobs.append(job)
                        except Exception:
                            # If parsing fails, include the job to be safe
                            recent_jobs.append(job)
                    else:
                        # No date info, include it
                        recent_jobs.append(job)
                
                return {
                    "jobs": recent_jobs,
                    "totalCount": len(recent_jobs)
                }
            else:
                return {
                    "jobs": [],
                    "totalCount": 0,
                    "error": f"API error {response.status_code}: {response.text}"
                }
        except Exception as e:
            return {
                "jobs": [],
                "totalCount": 0,
                "error": f"Request failed: {str(e)}"
            }
    
    def format_job(self, job: dict, index: int) -> str:
        """Format a job for display in Telegram.
        
        Args:
            job: Job dict from Jooble API
            index: Job number for selection
            
        Returns:
            Formatted string for Telegram message
        """
        title = job.get("title", "Unknown Title")
        company = job.get("company", "Unknown Company")
        location = job.get("location", "Unknown Location")
        salary = job.get("salary", "Not specified")
        snippet = job.get("snippet", "")[:150]  # Truncate long descriptions
        link = job.get("link", "")
        
        return (
            f"{index}. {title}\n"
            f"🏢 {company}\n"
            f"📍 {location}\n"
            f"💰 {salary}\n"
            f"📝 {snippet}...\n"
            f"🔗 {link}\n"
        )
    
    def format_jobs_list(self, jobs: list) -> str:
        """Format a list of jobs for Telegram display.
        
        Args:
            jobs: List of job dicts from Jooble API
            
        Returns:
            Formatted string with all jobs
        """
        if not jobs:
            return "No jobs found. Try different keywords or location."
        
        formatted = "🔍 Found Jobs:\n\n"
        for i, job in enumerate(jobs[:10], 1):  # Limit to 10 jobs
            formatted += self.format_job(job, i) + "\n"
        
        formatted += "\n💡 Reply with job number to customize your resume."
        return formatted
