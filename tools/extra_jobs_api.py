"""Additional Job APIs wrapper for multi-platform search."""

import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import os
from tools.google_search_api import GoogleSearchAPI


class ExtraJobsAPI:
    """Wrapper for additional free job boards (Remotive, etc.)."""
    
    def __init__(self):
        self.remotive_url = "https://remotive.com/api/remote-jobs"

    def search_remotive(self, keywords: str, limit: int = 10) -> List[Dict]:
        """Search jobs on Remotive.com.
        
        Args:
            keywords: Search keywords
            limit: Number of results to return
            
        Returns:
            List of job dictionaries
        """
        try:
            params = {"search": keywords, "limit": limit}
            response = requests.get(self.remotive_url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                jobs = data.get("jobs", [])
                
                # Filter for recent jobs (last 3 days)
                recent_jobs = []
                now = datetime.now()
                three_days_ago = now - timedelta(days=3)
                
                for job in jobs:
                    # Remotive date format: "2023-11-25T12:00:00"
                    pub_date_str = job.get("publication_date")
                    if pub_date_str:
                        try:
                            # Handle different date formats or truncate the time
                            pub_date = datetime.fromisoformat(pub_date_str.replace("Z", ""))
                            if pub_date >= three_days_ago:
                                recent_jobs.append({
                                    "title": job.get("title"),
                                    "company": job.get("company_name"),
                                    "location": "Remote",
                                    "salary": job.get("salary", "Not specified"),
                                    "link": job.get("url"),
                                    "source": "Remotive",
                                    "updated": pub_date_str
                                })
                        except Exception:
                            # If date parsing fails, include it
                            recent_jobs.append({
                                "title": job.get("title"),
                                "company": job.get("company_name"),
                                "location": "Remote",
                                "salary": job.get("salary", "Not specified"),
                                "link": job.get("url"),
                                "source": "Remotive",
                                "updated": pub_date_str
                            })
                    if len(recent_jobs) >= limit:
                        break
                        
                return recent_jobs
            return []
        except Exception as e:
            print(f"Remotive API Error: {e}")
            return []

    def search_google(self, keywords: str, location: str = "Remote") -> List[Dict]:
        """Search jobs using Google Custom Search."""
        google_api = GoogleSearchAPI()
        return google_api.search_jobs(keywords, location)

    def format_jobs_list(self, jobs: List[Dict]) -> str:
        """Format a list of jobs for Telegram display."""
        if not jobs:
            return "No additional recent jobs found on other platforms."
        
        formatted = "🌐 **More Jobs from Other Platforms:**\n\n"
        for i, job in enumerate(jobs, 1):
            formatted += (
                f"{i}. {job['title']}\n"
                f"🏢 {job['company']} ({job['source']})\n"
                f"💰 {job['salary']}\n"
                f"🔗 {job['link']}\n\n"
            )
        
        return formatted
