import os
import time
import json

import importlib
import subprocess
import sys
from typing import Optional

# 1. Dependency Setup
def setup_dependencies():
    required = {"requests": "requests", "python-dotenv": "dotenv"}
    for pkg, import_name in required.items():
        try:
            importlib.import_module(import_name)
        except ImportError:
            print(f"📦 Installing missing dependency: {pkg}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

setup_dependencies()


class RepoHunterOrchestrator:
    def __init__(self):
        # Load env vars if available
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except Exception:
            pass

        self.venv_python = "/Users/piyushdua/Desktop/instabot/venv/bin/python3"
        self.base_dir = "/Users/piyushdua/Desktop/instabot"
        # Cloud endpoint used by query_expert; update via .env or hub menu option 5
        self.cloud_endpoint = (
            os.environ.get("CLOUD_EXPERT_ENDPOINT")
            or os.environ.get("REPOHUNTER_CLOUD_ENDPOINT")
            or "https://your-studio-id.lightning.ai/recommend"
        )
        self.expert_api_key: Optional[str] = os.environ.get("EXPERT_API_KEY")
        
        # Paths
        self.raw_data = "github_repohunter/database/training/matchmaker_pairs.jsonl"
        self.clean_dataset = "github_repohunter/database/training/platinum_matchmaker.jsonl"
        self.training_script = "github_repohunter/training/train_repohunter.sh"
        self.adapters_dir = "github_repohunter/training/adapters"
        
        # Performance Thresholds
        # Scale: Retrain every time we gain 500 new validated pairs
        self.threshold = 500 
        # Track last trained line count to avoid NameError
        self.last_trained_count = self.get_current_data_count()

    def get_current_data_count(self):
        if not os.path.exists(self.raw_data):
            return 0
        try:
            return int(subprocess.check_output(['wc', '-l', self.raw_data]).split()[0])
        except:
            return 0

    def query_expert(self, query):
        import requests
        try:
            if not self.cloud_endpoint or "your-studio-id" in self.cloud_endpoint:
                return "Cloud endpoint not configured. Set REPOHUNTER_CLOUD_ENDPOINT or update orchestrator.py."
            print(f"📡 Querying RepoHunter Expert at {self.cloud_endpoint}...")
            headers = {}
            if self.expert_api_key:
                headers["X-API-Key"] = self.expert_api_key
            response = requests.post(
                self.cloud_endpoint,
                json={"query": query, "max_tokens": 512, "temperature": 0.7},
                headers=headers,
                timeout=30
            )
            if response.status_code == 200:
                result = response.json().get("recommendation", "No recommendation found.")
                print(f"✨ Expert Response: {result[:100]}...")
                return result
            else:
                print(f"❌ Cloud Error: {response.status_code} - {response.text}")
                return f"Cloud Error: {response.status_code}"
        except Exception as e:
            print(f"❌ Connection Error: {e}")
            return str(e)

    def trigger_pipeline(self):

        print(f"\n🚀 [ORCHESTRATOR] Triggering Infinite Learning Loop at {time.strftime('%H:%M:%S')}")
        
        # 1. Clean Data
        print("🧼 Step 1: Automated Cleaning...")
        subprocess.run([self.venv_python, "github_repohunter/training/auto_cleaner.py"], cwd=self.base_dir)
        
        # 2. Prepare/Split Data
        print("🎯 Step 2: Preparing MLX Splits...")
        subprocess.run([self.venv_python, "github_repohunter/training/prepare_mlx_data.py"], cwd=self.base_dir)
        
        # 3. Fine-Tune
        print("🧬 Step 3: Launching MLX Fine-Tuning (LoRA)...")
        # We run the shell script which handles the mlx_lm.lora command
        subprocess.run(["bash", self.training_script], cwd=self.base_dir)
        
        # 4. Update state
        self.last_trained_count = self.get_current_data_count()
        print(f"✅ [ORCHESTRATOR] Training Cycle Complete. Model evolved using {self.last_trained_count} pairs.")

    def start_autonomous_mode(self):
        print("🤖 REPOHUNTER ORCHESTRATOR: ONLINE")
        print(f"🎯 Target Scale: 50,000 Repositories")
        
        # Initial run if data exists
        current_count = self.get_current_data_count()
        if current_count > 0:
            self.trigger_pipeline()

        while True:
            current_count = self.get_current_data_count()
            diff = current_count - self.last_trained_count
            
            if diff >= self.threshold:
                print(f"🔥 Threshold Reached! ({diff} new pairs found). Starting evolution...")
                self.trigger_pipeline()
            else:
                if current_count % 50 == 0:
                    print(f"🕒 Orchestrator monitoring: {current_count} raw pairs synthesized. ({self.threshold - diff} more needed for next training).")
            
            # Check every 10 minutes
            time.sleep(600)

if __name__ == "__main__":
    orchestrator = RepoHunterOrchestrator()
    orchestrator.start_autonomous_mode()
