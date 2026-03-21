import time
from github_repohunter.repo_discovery_engine import RepoHunter
from github_repohunter.guardrail_checker import GuardrailChecker
import json
import os

def bulk_hunt():
    hunter = RepoHunter()
    checker = GuardrailChecker()
    
    # Defining 10 initial "High Interest" niches for the dataset
    niches = [
        "LLM Orchestration",
        "Local AI Agent",
        "React Native Performance",
        "Rust CLI Tools",
        "FastAPI Boilerplate",
        "Open Source Security",
        "WebRTC Video",
        "Flutter Widgets",
        "Postgres Vector",
        "Go Microservices"
    ]
    
    all_validated_data = []
    
    print(f"🚀 Starting Bulk Hunt across {len(niches)} niches...")
    
    for niche in niches:
        # 1. Hunt
        gems = hunter.find_hidden_gems(niche, max_stars=3000, count=10)
        
        # 2. Filter & Validate
        safe_gems = []
        for gem in gems:
            is_safe, issues = checker.validate_repo(gem)
            if is_safe:
                safe_gems.append(gem)
        
        all_validated_data.extend(safe_gems)
        print(f"📦 niche '{niche}': {len(safe_gems)}/10 passed guardrails.")
        
        # 3. Rate limit prevention
        time.sleep(5)

    # Save the master training set
    master_path = "github_repohunter/database/validated/master_dataset.json"
    os.makedirs(os.path.dirname(master_path), exist_ok=True)
    with open(master_path, 'w') as f:
        json.dump(all_validated_data, f, indent=4)
        
    print(f"🏆 Bulk Hunt Complete! Total verified repos: {len(all_validated_data)}")
    print(f"📁 Master dataset saved to: {master_path}")

if __name__ == "__main__":
    bulk_hunt()
