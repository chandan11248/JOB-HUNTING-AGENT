"""Smart Query Expander using OpenRouter (Free Tier)."""

import requests
import json
from typing import List
from config import Config

class LLMQueryExpander:
    """Uses OpenRouter to expand a search query into related job titles."""
    
    def __init__(self):
        self.api_key = Config.OPENROUTER_API_KEY
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        # Using a reliable free model
        self.model = "google/gemma-2-9b-it:free"

    def expand_query(self, query: str) -> List[str]:
        """Expands a query into 5 related job titles."""
        if not self.api_key or self.api_key == "your_openrouter_key":
            print("OpenRouter API key missing. Falling back to original query.")
            return [query]

        prompt = f"""
        You are a recruitment expert. Your goal is to expand the job search query '{query}' into 5 highly related but distinct job titles or search terms.
        These will be used to find a variety of relevant jobs.
        
        Examples:
        - "ML/AI" -> Python Developer, Data Scientist, LLM Engineer, Research Scientist, Computer Vision Engineer
        - "Frontend" -> React Developer, Tailwind CSS Expert, UI/UX Engineer, Javascript Developer, Frontend Architect
        
        Return ONLY a comma-separated list of the 5 titles. Do not include any other text.
        Query: {query}
        """

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/chandan11248/job-agent-bot", # OpenRouter requirement
            "X-Title": "LangGraph Job Agent"
        }

        data = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        try:
            response = requests.post(self.base_url, headers=headers, data=json.dumps(data), timeout=20)
            if response.status_code == 200:
                content = response.json()["choices"][0]["message"]["content"].strip()
                # Parse comma-separated list
                variations = [v.strip() for v in content.split(",")]
                # Filter out empty strings and limit to 5
                variations = [v for v in variations if v][:5]
                
                # Ensure original query is included if not in result
                if query not in variations:
                   variations.insert(0, query)
                
                return variations
            else:
                print(f"OpenRouter Error {response.status_code}: {response.text}")
                return [query]
        except Exception as e:
            print(f"Query Expansion Error: {e}")
            return [query]
