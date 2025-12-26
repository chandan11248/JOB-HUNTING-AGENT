"""Google Custom Search API wrapper for job scraping."""

import requests
from typing import List, Dict
from config import Config


class GoogleSearchAPI:
    """Wrapper for Google Custom Search API to find job listings."""
    
    def __init__(self):
        self.api_key = Config.GOOGLE_SEARCH_KEY
        self.cx = Config.GOOGLE_SEARCH_CX
        self.base_url = "https://www.googleapis.com/customsearch/v1"

    def search_jobs(self, keywords: str, location: str = "Remote", limit: int = 5) -> List[Dict]:
        """Search for job listings using Google Custom Search.
        
        Args:
            keywords: Job search keywords
            location: Location (default 'Remote')
            limit: Number of results to return
            
        Returns:
            List of job dictionaries
        """
        if not self.api_key or not self.cx:
            print("Google Search API key or CX missing.")
            return []

        # Construct query: site:linkedin.com/jobs/view "keywords" "location" "1 day ago"
        query = f'site:linkedin.com/jobs/view "{keywords}" "{location}" "1 day ago"'
        
        params = {
            "q": query,
            "cx": self.cx,
            "key": self.api_key,
            "num": limit
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])
                
                jobs = []
                for item in items:
                    # Parse title and company (usually "Job Title | Company | LinkedIn")
                    title_raw = item.get("title", "Unknown Job")
                    title_parts = [p.strip() for p in title_raw.split("|")]
                    
                    title = title_parts[0] if len(title_parts) > 0 else "Unknown Job"
                    company = title_parts[1] if len(title_parts) > 1 else "Unknown Company"
                    
                    jobs.append({
                        "title": title,
                        "company": company,
                        "location": location,
                        "salary": "Check listing",
                        "link": item.get("link"),
                        "source": "LinkedIn (Google)",
                        "snippet": item.get("snippet", "")
                    })
                return jobs
            else:
                print(f"Google Search API Error {response.status_code}: {response.text}")
                return []
        except Exception as e:
            print(f"Google Search Request Error: {e}")
            return []
