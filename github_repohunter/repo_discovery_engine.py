import requests
import json
from datetime import datetime, timedelta
import os
import time
import base64

class RepoHunter:
    def __init__(self):
        self.base_url = "https://api.github.com/search/repositories"
        self.repo_url = "https://api.github.com/repos"
        # Optional: Use GITHUB_TOKEN environment variable for higher rate limits
        self.token = os.environ.get("GITHUB_TOKEN")
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "RepoHunter-Agent"
        }
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"
            
        self.data_dir = "github_repohunter/database/raw"
        os.makedirs(self.data_dir, exist_ok=True)

    def get_readme(self, repo_full_name):
        """
        Fetches the README content for a repository to provide deep context.
        """
        url = f"{self.repo_url}/{repo_full_name}/readme"
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                content_b64: str = response.json().get('content', '')
                # Decode base64 README and truncate to first 1000 chars
                decoded_bytes: bytes = base64.b64decode(content_b64)
                readme_text: str = decoded_bytes.decode('utf-8', errors='ignore')
                return readme_text[0:1000] if readme_text else "No README content found."
        except Exception as e:
            print(f"⚠️ Could not fetch README for {repo_full_name}: {e}")
        return "No README content found."

    def find_hidden_gems(self, query, max_stars=5000, min_activity_days=60, count=15):
        """
        Finds underrated repos and enriches them with README context.
        """
        print(f"🕵️‍♂️ Deep Hunting for: '{query}'...")
        
        date_limit = (datetime.now() - timedelta(days=min_activity_days)).strftime('%Y-%m-%d')
        full_query = f"{query} stars:<{max_stars} pushed:>{date_limit}"
        params = {
            "q": full_query,
            "sort": "updated",
            "order": "desc",
            "per_page": 100
        }

        response = requests.get(self.base_url, headers=self.headers, params=params)
        
        if response.status_code != 200:
            print(f"❌ Error fetching data: {response.text}")
            return []

        items = response.json().get('items', [])
        gems = []

        for item in items:
            repo_name = item['full_name']
            print(f"🔍 Enrichment: {repo_name}...")
            
            # Fetch deeper context
            readme_context = self.get_readme(repo_name)
            
            gem = {
                "name": repo_name,
                "url": item['html_url'],
                "description": item['description'] or "No description provided.",
                "stars": item['stargazers_count'],
                "forks": item['forks_count'],
                "last_update": item['pushed_at'],
                "language": item['language'] or "Unknown",
                "license": item['license']['name'] if item['license'] else "No License",
                "readme_snippet": readme_context
            }
            gems.append(gem)
            time.sleep(1) # Small delay to be polite to the API

        self.save_gems(gems, query)
        return gems

    def save_gems(self, gems, query):
        safe_query = query.replace(' ', '_').replace('/', '_')
        filename = os.path.join(self.data_dir, f"gems_{safe_query}.json")
        with open(filename, 'w') as f:
            json.dump(gems, f, indent=4)
        print(f"💾 Saved {len(gems)} enriched gems to {filename}")

if __name__ == "__main__":
    hunter = RepoHunter()
    hunter.find_hidden_gems("FastAPI", max_stars=1000)
