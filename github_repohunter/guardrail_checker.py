import json
import os

class GuardrailChecker:
    def __init__(self):
        # We only want permissive, open-source friendly repos
        self.allowed_licenses = ["MIT License", "Apache License 2.0", "GNU General Public License v3.0", "BSD 3-Clause 'New' or 'Revised' License"]

    def validate_repo(self, repo_data):
        """
        Runs multiple security and quality checks on a repository.
        """
        issues = []
        
        # 1. License Check
        license_val = repo_data.get('license', 'No License')
        if license_val == "No License":
            issues.append("MISSING_LICENSE")
        elif license_val not in self.allowed_licenses:
            issues.append(f"UNAPPROVED_LICENSE: {license_val}")

        # 2. Maintenance Check (Is it a ghost ship?)
        # For simplicity, we assume the input data is already filtered for recent push

        # 3. Description Depth
        description_val = repo_data.get('description', '')
        if not description_val or len(description_val) < 15:
            issues.append("LOW_DESCRIPTION_DEPTH")

        is_safe = len(issues) == 0
        return is_safe, issues

    def process_data_file(self, filename):
        if not os.path.exists(filename):
            print(f"❌ Error: {filename} not found.")
            return

        with open(filename, 'r') as f:
            data = json.load(f)

        print(f"🛡️ Running guardrails on {len(data)} repos from {filename}...")
        safe_repos = []
        for repo in data:
            is_safe, issues = self.validate_repo(repo)
            if is_safe:
                safe_repos.append(repo)
                print(f"✅ Safe: {repo['name']}")
            else:
                print(f"🚨 Flagged: {repo['name']} - Issues: {', '.join(issues)}")

        return safe_repos

if __name__ == "__main__":
    checker = GuardrailChecker()
    # Replace with an actual file path after running discovery
    # checker.process_data_file("data/gems_MLX_AI.json")
