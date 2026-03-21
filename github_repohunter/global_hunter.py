import time
from github_repohunter.repo_discovery_engine import RepoHunter
from github_repohunter.guardrail_checker import GuardrailChecker
import json
import os

class GlobalScanner:
    def __init__(self):
        self.hunter = RepoHunter()
        self.checker = GuardrailChecker()
        self.output_path = "github_repohunter/database/validated/global_ocean.jsonl"
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)

        # 🌌 The Universal GitHub Domain Matrix (Covering the Entire Spectrum)
        self.domain_matrix = {
            "Infrastructure_DevOps": [
                "Kubernetes", "Docker", "Terraform", "Ansible", "Helm", "Prometheus", "Grafana", 
                "Jenkins", "GitHub Actions", "GitLab CI", "Nginx", "Envoy", "Istio", "Serverless",
                "Cloud Native", "Vulnerability Scanning", "Vault", "Terraform Provider", "Pulumi"
            ],
            "AI_MachineLearning_DataScience": [
                "LLM", "Transformers", "LangChain", "Llama Index", "PyTorch", "TensorFlow", "Keras",
                "Scikit-learn", "Pandas", "NumPy", "Jupyter", "MLOps", "Model Serving", "Quantization",
                "Computer Vision", "NLP", "Audio Processing", "GNN", "HuggingFace", "Stable Diffusion"
            ],
            "Backend_Distributed": [
                "Microservices", "GRPC", "GraphQL", "REST API", "Kafka", "RabbitMQ", "Redis", 
                "Distributed Locking", "Consensus Algorithm", "Service Mesh", "Load Balancing", 
                "API Gateway", "WebRTC", "Event Sourcing", "CQRS", "ZeroMQ", "P2P"
            ],
            "Databases_Storage": [
                "PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch", "ClickHouse", "Cassandra",
                "RocksDB", "SQLite", "DuckDB", "Vector Database", "ChromaDB", "Pinecone", "Milvus",
                "Storage Engine", "IPFS", "ZFS", "Ceph"
            ],
            "Frontend_UI_UX": [
                "React", "Next.js", "Vue", "Nuxt", "Svelte", "Angular", "TailwindCSS", "Material UI",
                "Framer Motion", "GSAP", "Three.js", "WebAssembly", "Micro Frontends", "Design System",
                "Chrome Extension", "WebExtensions", "WebGL", "WebGPU"
            ],
            "Security_Privacy": [
                "Cryptography", "Zero Knowledge", "Penetration Testing", "Static Analysis", "SAST", "DAST",
                "OAuth2", "OpenID Connect", "JWT", "IAM", "Firewall", "IDS", "IPS", "Malware Analysis",
                "Forensics", "OSINT", "Exploit Development", "Fuzzing", "CTF"
            ],
            "Systems_Programming": [
                "Operating Systems", "Kernel", "Drivers", "Embedded", "IoT", "Compilers", "Runtime",
                "Interpreter", "Virtual Machine", "Wasm", "EBPF", "Memory Management", "Concurrency",
                "Assembly", "BIOS", "Bootloader", "Firmware", "RISC-V"
            ],
            "Game_Development_Graphics": [
                "Unity", "Unreal Engine", "Godot", "Vulkan", "DirectX", "Metal", "Ray Tracing",
                "Shader", "OpenGL", "Bevy", "LibGDX", "SFML", "Physics Engine", "Multiplayer Engine"
            ],
            "Blockchain_Web3": [
                "Ethereum", "Solidity", "Smart Contracts", "DeFi", "NFT", "Solana", "Polkadot",
                "Bitcoin", "Wallet", "Consensus", "DAO", "Layer 2", "EVM", "Chainlink"
            ],
            "Mobile_Universal": [
                "iOS", "Android", "React Native", "Flutter", "Expo", "Ionic", "SwiftUI",
                "Jetpack Compose", "Mobile Security", "BLE", "NFC", "Wearables"
            ],
            "Specialized_Domains": [
                "Bioinformatics", "Robotics", "ROS", "Aerospace", "ArduPilot", "GIS", "PostGIS",
                "Quantum Computing", "Qiskit", "Fintech", "Healthtech", "Computer Algebra"
            ],
            "Productivity_Tools": [
                "CLI", "Automation", "Dotfiles", "Terminal", "Zsh", "Neovim", "VS Code Extension",
                "Obsidian", "Dashboards", "TUI", "Shell Scripting"
            ]
        }
        
        # Expanded languages (The High-Diversity Set)
        self.languages = [
            "Python", "JavaScript", "TypeScript", "Go", "Rust", "C++", "C", "Java", "C#", "Ruby",
            "PHP", "Swift", "Kotlin", "Scala", "Haskell", "Elixir", "Clojure", "Lua", "Zig", 
            "Fortran", "Ada", "Lisp", "Prolog", "Julia", "Dart", "R", "F#", "Nim"
        ]

    def run_deep_ocean_scan(self, target_repos=50000):
        """
        Scans entire domains and languages systematically to reach 50,000+ repos.
        """
        print(f"🌊 HYPER-SCALE SCAN INITIATED... Target: {target_repos} repositories.")
        
        # Load existing progress to avoid duplicates if restarting
        existing_repos = set()
        if os.path.exists(self.output_path):
            with open(self.output_path, 'r') as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        existing_repos.add(data['name'])
                    except:
                        pass
        
        total_discovered = len(existing_repos)
        print(f"📊 Resuming from {total_discovered} existing repositories.")

        with open(self.output_path, 'a') as ocean_file:
            for category, subdomains in self.domain_matrix.items():
                print(f"📂 Category: {category}")
                
                for subdomain in subdomains:
                    for lang in self.languages:
                        query = f"{subdomain} language:{lang}"
                        
                        try:
                            # Search more broadly (up to 20k stars)
                            repos = self.hunter.find_hidden_gems(query, max_stars=20000, count=100)
                            
                            verified_count = 0
                            for repo in repos:
                                if repo['name'] in existing_repos:
                                    continue
                                    
                                is_safe, issues = self.checker.validate_repo(repo)
                                if is_safe:
                                    ocean_file.write(json.dumps(repo) + "\n")
                                    ocean_file.flush() # Ensure it's written immediately
                                    existing_repos.add(repo['name'])
                                    verified_count = (verified_count + 1)
                                    total_discovered = (total_discovered + 1)
                            
                            print(f"✅ {subdomain}/{lang}: {verified_count} unique verified.")
                            print(f"🚢 Total Global Progress: {total_discovered}/{target_repos}")

                            if total_discovered >= target_repos:
                                print("🏁 HYPER-SCALE TARGET REACHED!")
                                return

                            # API delay
                            time.sleep(12) 
                            
                        except Exception as e:
                            print(f"⚠️ Search failed for {query}: {e}")
                            time.sleep(30)

        print(f"🏆 HYPER-SCALE SCAN COMPLETE! Total verified: {total_discovered}")

if __name__ == "__main__":
    scanner = GlobalScanner()
    # 50,000 repositories for a massive dataset
    scanner.run_deep_ocean_scan(target_repos=50000)
