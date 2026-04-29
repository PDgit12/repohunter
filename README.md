# 🏹 RepoHunter: Parallel Agent Architecture Generator

RepoHunter is a hybrid local/cloud AI system that discovers high-quality repositories, builds a RAG knowledge index, and runs **parallel specialist agents** to generate a production-ready `architecture.md` blueprint and implementation prompt.

Core loop: Discovery ➔ Validation ➔ Synthesis/Training ➔ Retrieval ➔ Parallel Agent Planning ➔ `architecture.md`.

---

## 🏗️ Technical Architecture

### 🛡️ Core Infrastructure
- **Local Control Center (M4)**: `hub.py` for orchestration + architecture generation workflows.
- **Cloud Expert Backend (Tesla T4)**: Unsloth/Llama-3 inference and adapter serving.
- **Data + Knowledge Plane**: Firestore + local JSONL + ChromaDB vector index.

### 🧩 Directory Structure
- `hub.py`: CLI launcher for architecture generation, sync, and orchestration.
- `github_repohunter/server.py`: API bridge (`/chat`, `/architecture/generate`, `/status`).
- `github_repohunter/architecture_agents.py`: Parallel agent mesh + markdown renderer.
- `github_repohunter/rag_engine.py`: Chroma index build/retrieval.
- `github_repohunter/scripts/`: Cloud sync, synthesis, training, migration utilities.

---

## 🚀 OSS Quickstart (Clone → Run)

```bash
git clone <your-repo-url>
cd instabot
python3 -m venv venv && source venv/bin/activate
pip install -e .
repohunter demo --output architecture.demo.md
```

If this command succeeds, the project is working end-to-end.

## 🐳 Docker Compose (API + Redis, internet-grade local stack)

```bash
cp .env.docker.example .env
docker compose up --build -d
```

Health check:
```bash
curl http://localhost:8000/status
```

Protected architecture generation:
```bash
curl -X POST http://localhost:8000/architecture/generate \
  -H "Content-Type: application/json" \
  -H "X-Architecture-Key: replace_me_key_v1" \
  -d '{
    "product_name":"Compose Demo Product",
    "requirement":"Need internet-grade multi-agent architecture generation",
    "write_file":true,
    "output_path":"architecture.compose.demo.md"
  }'
```

Stop stack:
```bash
docker compose down
```

## 🧰 CLI Commands

### 1) One-command showcase
```bash
repohunter demo --output architecture.demo.md
```

### 2) Real generation
```bash
repohunter generate \
  --product "Acme AI Copilot" \
  --requirement "Design a scalable multi-agent architecture planner for SaaS engineering teams" \
  --stack FastAPI --stack PostgreSQL --stack Redis \
  --output architecture.md
```

### 3) JSON summary mode
```bash
repohunter generate \
  --product "Acme AI Copilot" \
  --requirement "Need a robust architecture generation system" \
  --json
```

### 4) Local status
```bash
repohunter status
```

## 🔐 Security Defaults

- `ARCHITECTURE_API_KEY` (optional): if set, `/architecture/generate` requires header `X-Architecture-Key`.
- `ARCH_RATE_LIMIT_PER_MIN`: in-memory per-client rate limit for architecture generation endpoint.
- `ALLOW_ORIGINS`: explicit CORS allowlist; no wildcard origin by default.
- `EXPERT_API_KEY`: required on cloud expert server (`/recommend`) for authenticated usage.

Example:
```bash
export ARCHITECTURE_API_KEY="your-strong-key"
export ARCH_RATE_LIMIT_PER_MIN=20
export ALLOW_ORIGINS="http://localhost:5173,http://127.0.0.1:5173"
```

## 📦 What to publish vs keep private

Publish (for users):
- `README.md`
- `docker-compose.yml`
- `.env.example`
- `.env.docker.example`
- `github_repohunter/` source code
- `tests/`
- `.github/workflows/ci.yml`

Keep private/personal:
- Interview prep notes and deep personal study docs
- Local generated architecture artifacts (`architecture*.md`)
- Any internal planning notes (`task.md`)

---

## Getting Started (Detailed)

### 1. Prerequisites
- **Local**: macOS (Apple Silicon recommended), Python 3.12+, Ollama installed.
- **Cloud**: Lightning AI Studio with GPU (Tesla T4/A10G).
- **Service**: Firebase project with Firestore enabled.

### 2. Fast-Track Setup
1.  **Clone & Venv**:
    ```bash
    git clone [your-repo] && cd instabot
    python3 -m venv venv && source venv/bin/activate
    pip install -r requirements.txt
    ```
2.  **Environment Configuration**:
    - Place `service-account.json` in the root (do not commit to public repos).
    - Update `github_repohunter/orchestrator.py` with your Lightning AI Studio URL.
3.  **Launch the API + Hub**:
    ```bash
    python -m github_repohunter.server
    ```
    ```bash
    python3 hub.py
    ```

### 3. Generate `architecture.md`
Use hub option `1` or call API directly:
```bash
curl -X POST http://localhost:8000/architecture/generate \
  -H "Content-Type: application/json" \
  -d '{
    "product_name":"Your Product",
    "requirement":"Need a scalable multi-agent coding architecture",
    "write_file":true,
    "output_path":"architecture.md"
  }'
```

### 4. Activating "Expert Mode" (Cloud GPU)
1.  **Launch Cloud API**:
    On Lightning AI, run the FastAPI server:
    ```bash
    /home/zeus/miniconda3/envs/cloudspace/bin/python github_repohunter/scripts/cloud_inference_api.py
    ```
2.  **Map Port**:
    Forward **Port 8000** in Lightning AI and copy the **Public URL**.
3.  **Connect Hub**:
    Use **Option 5** in `hub.py` to paste your cloud endpoint.

---

## 🤝 Parallel Agent Interaction Model

RepoHunter does not just run independent agents and merge text.

- Round 1 runs in parallel:
  - `requirements-analyst`
  - `system-designer`
  - `execution-planner`
- Round 2 runs in parallel reviewer loop:
  - `requirements-reviewer`
  - `design-reviewer`
  - `execution-reviewer`
- Final synthesis agent reads all outputs from shared blackboard and resolves final architecture decisions.

This gives explicit cross-agent interaction before `architecture.md` is emitted.

---

## 🛠️ Production Roadmap
- [ ] **Secret Management**: remove hardcoded defaults, use secret manager.
- [ ] **Observability**: request tracing + metrics + dashboard.
- [ ] **Reliability**: typed event contracts for agent mesh and retries/timeouts.
- [ ] **Testing**: API and architecture artifact golden tests.

---
