import json
import os
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def load_env_manual(path=".env"):
    if os.path.exists(path):
        with open(path, "r") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    os.environ[key] = value

class RepoHunterSynthesizerParallel:
    def __init__(self, use_remote=True):
        # 🔗 Fallback manual env load
        load_env_manual()
        
        # 🔗 Remote Inference vs Local Ollama
        # To avoid slowing down the Mac, use a high-speed remote API (Groq/OpenAI) 
        # or a remote GPU instance (RunPod/AWS).
        self.ollama_url = "http://localhost:11434/api/generate" # Default local fallback
        self.remote_url = os.getenv("REMOTE_LLM_URL", self.ollama_url)
        self.api_key = os.getenv("LLM_API_KEY", "")
        self.model_name = os.getenv("SYNTHESIS_MODEL", "llama-3.3-70b-versatile")
        
        self.input_path = "github_repohunter/database/validated/global_ocean.jsonl"
        self.output_path = "github_repohunter/database/training/matchmaker_pairs.jsonl"
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        
        # 🧵 Concurrency control (Set to 10-20 for cloud, 2-3 for local)
        self.max_workers = 10 if use_remote else 2

    def generate_pair(self, repo_data):
        """
        Synthesizes a training pair from repo metadata.
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
        
        is_groq = "groq" in self.remote_url
        
        # 🔗 Payload adjustment for Groq/OpenAI format
        if is_groq or "openai" in self.remote_url:
            payload = {
                "model": self.model_name,
                "messages": [{"role": "user", "content": prompt}],
                "response_format": {"type": "json_object"}
            }
        else:
            payload = {
                "model": "llama3",
                "prompt": prompt,
                "stream": False,
                "format": "json"
            }
        
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"} if self.api_key else {}

        try:
            response = requests.post(self.remote_url, json=payload, headers=headers, timeout=60)
            if response.status_code == 200:
                resp_json = response.json()
                
                # Check for standard OpenAI/Groq response path
                if "choices" in resp_json:
                    result = resp_json['choices'][0]['message']['content']
                else:
                    result = resp_json.get('response', '')
                
                return json.loads(result)
            else:
                # print(f"❌ API Error {response.status_code}: {response.text}")
                pass
        except Exception as e:
            # print(f"⚠️ Synthesis failed for {repo_data['name']}: {e}")
            pass
        return None

    def process_repo(self, repo_data):
        pair = self.generate_pair(repo_data)
        if pair:
            print(f"✅ Synthesized: {repo_data['name']}")
            return {
                "text": f"### Instruction: {pair['instruction']} ### Response: {pair['response']}"
            }
        return None

    def start_factory(self):
        """
        Runs the synthesis factory infinitely.
        """
        print(f"🚀 REPOHUNTER FACTORY ACTIVE (Workers: 20 | Model: {self.model_name})")
        while True:
            try:
                self.run_once()
            except Exception as e:
                print(f"⚠️ Factory Loop Error: {e}")
            
            print("💤 Factory resting for 5 minutes...")
            time.sleep(300)

    def run_once(self):
        if not os.path.exists(self.input_path):
            return

        # Load all repos
        repos_to_process = []
        with open(self.input_path, 'r') as f:
            for line in f:
                try:
                    repos_to_process.append(json.loads(line))
                except: continue

        # Duplicate check: check if repo name is in existing output
        existing_content = ""
        if os.path.exists(self.output_path):
            with open(self.output_path, 'r') as f:
                existing_content = f.read()
        
        final_repos = []
        for repo in repos_to_process:
            if f"for {repo['name']}" not in existing_content:
                final_repos.append(repo)

        if not final_repos:
            return

        print(f"🏭 Factory starting batch: {len(final_repos)} new repositories...")
        
        with ThreadPoolExecutor(max_workers=20) as executor:
            future_to_repo = {executor.submit(self.process_repo, repo): repo for repo in final_repos}
            for future in as_completed(future_to_repo):
                repo = future_to_repo[future]
                try:
                    result = future.result()
                    if result:
                        with open(self.output_path, 'a') as f_out:
                            f_out.write(json.dumps(result) + "\n")
                except Exception as exc:
                    print(f"❌ {repo['name']} error: {exc}")

if __name__ == "__main__":
    # If running on Mac, suggest use_remote=True with Groq/OpenAI to stay fast.
    factory = RepoHunterSynthesizerParallel(use_remote=True)
    factory.start_factory()
