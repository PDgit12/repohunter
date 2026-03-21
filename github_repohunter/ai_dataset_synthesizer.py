import json
import os
import requests
import time

class RepoHunterSynthesizer:
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"
        self.input_path = "github_repohunter/database/validated/global_ocean.jsonl"
        self.output_path = "github_repohunter/database/training/matchmaker_pairs.jsonl"
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)

    def generate_pair(self, repo_data):
        """
        Uses local Ollama to synthesize a training pair from repo metadata.
        """
        prompt = f"""
        You are an expert technical data generator. 
        Create a training pair for a GitHub Project Assistant.
        
        Repository Name: {repo_data['name']}
        Description: {repo_data['description']}
        Main Language: {repo_data['language']}
        README Snippet: {repo_data['readme_snippet']}
        
        Format the output as a JSON object with:
        "instruction": A realistic user question or project requirement that this repo would solve.
        "response": A detailed recommendation explaining WHY this repo is the perfect match.
        
        ONLY return the JSON object.
        """
        
        payload = {
            "model": "llama3",
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }

        try:
            response = requests.post(self.ollama_url, json=payload, timeout=60)
            if response.status_code == 200:
                result = response.json().get('response', '')
                return json.loads(result)
        except Exception as e:
            print(f"⚠️ Synthesis failed for {repo_data['name']}: {e}")
        return None

    def start_synthesis(self):
        print(f"🧠 Initiating AI Synthesis...")
        processed_count = 0
        
        # 1. Process Legacy Master Dataset (JSON) if exists
        legacy_path = "github_repohunter/database/validated/master_dataset.json"
        if os.path.exists(legacy_path):
            print(f"📦 Processing legacy dataset: {legacy_path}")
            with open(legacy_path, 'r') as f_in, open(self.output_path, 'a') as f_out:
                data = json.load(f_in)
                for repo_data in data:
                    # Synthetic dataset needs README content; providing a fallback if missing
                    if 'readme_snippet' not in repo_data:
                        repo_data['readme_snippet'] = repo_data.get('description', 'No details available.')
                    
                    self.process_and_write(repo_data, f_out)
                    processed_count += 1
                    time.sleep(1)

        # 2. Process Global Ocean (JSONL) if exists
        if os.path.exists(self.input_path):
            print(f"🌊 Processing global ocean: {self.input_path}")
            with open(self.input_path, 'r') as f_in, open(self.output_path, 'a') as f_out:
                for line in f_in:
                    repo_data = json.loads(line)
                    self.process_and_write(repo_data, f_out)
                    processed_count = (processed_count + 1)
                    time.sleep(1)

        print(f"📊 Synthesis batch complete. Total pairs generated: {processed_count}")

    def process_and_write(self, repo_data, f_out):
        print(f"✨ Synthesizing context for: {repo_data['name']}...")
        training_pair = self.generate_pair(repo_data)
        if training_pair:
            formatted_pair = {
                "text": f"### Instruction: {training_pair['instruction']} ### Response: {training_pair['response']}"
            }
            f_out.write(json.dumps(formatted_pair) + "\n")
            print(f"✅ Success: {repo_data['name']}")

if __name__ == "__main__":
    synthesizer = RepoHunterSynthesizer()
    synthesizer.start_synthesis()
