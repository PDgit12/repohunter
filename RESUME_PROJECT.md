# Resume Project: RepoHunter — Parallel Agent Architecture Generator

## 🎯 Resume One-Liner (Copy-Paste Ready)

```
• Built RepoHunter, a CLI tool using Python/FastAPI that runs 7 parallel AI agents with RAG retrieval 
  (13K+ GitHub repos) to generate production-ready architecture blueprints in seconds
```

**Short version:**
```
• RepoHunter — Multi-agent architecture generator | Python, FastAPI, ChromaDB, asyncio | 7 parallel agents, 13K repo RAG index
```

---

## 📋 Resume Bullet Points (Multiple Versions)

### Version 1: Technical Focus
```
• Built RepoHunter, a parallel multi-agent architecture generator using FastAPI, ChromaDB, 
  and RAG pipelines that synthesizes production-ready blueprints from GitHub repository patterns
• Implemented 6-agent parallel mesh (requirements-analyst, system-designer, execution-planner + 
  3 reviewers) with shared blackboard pattern for cross-agent communication and consensus
• Designed hybrid local/cloud infrastructure: M4 orchestration hub + Tesla T4 GPU inference 
  server with Unsloth/Llama-3 fine-tuned adapters for domain-specific generation
```

### Version 2: Impact Focus
```
• Created AI-powered architecture generator that analyzes GitHub repositories and outputs 
  structured, copy-paste-ready implementation prompts for vibe coding platforms
• Engineered parallel agent system reducing architecture planning time by running 6 specialist 
  agents concurrently with automated cross-review validation
• Built enterprise-grade API with rate limiting, API key auth, CORS controls, and Docker 
  Compose deployment for internet-scale usage
```

### Version 3: Short (1 bullet)
```
• Built RepoHunter: parallel multi-agent architecture generator using FastAPI, ChromaDB RAG, 
  and 6 specialist agents that synthesize production-ready blueprints from GitHub patterns
```

---

## 🛠️ Tech Stack

| Category | Technologies |
|----------|--------------|
| **Backend** | Python 3.12+, FastAPI, Uvicorn |
| **AI/ML** | Llama-3, Unsloth (fine-tuning), Sentence Transformers |
| **Vector DB** | ChromaDB (RAG knowledge index) |
| **Database** | Firebase Firestore, Local JSONL |
| **Infrastructure** | Docker, Docker Compose, Redis |
| **Cloud** | Lightning AI Studio (Tesla T4/A10G GPU) |
| **Local** | Apple Silicon M4, Ollama |
| **Architecture** | Multi-agent mesh, Blackboard pattern, RAG pipeline |

---

## 📐 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER INPUT                                    │
│  Product: "AI Copilot"  Requirement: "Scalable multi-agent..."  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                 RAG KNOWLEDGE RETRIEVAL                          │
│  ChromaDB vector index → Top 8 relevant GitHub repos            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              ROUND 1: PARALLEL AGENTS (async)                    │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐    │
│  │  requirements-  │ │  system-        │ │  execution-     │    │
│  │  analyst        │ │  designer       │ │  planner        │    │
│  └────────┬────────┘ └────────┬────────┘ └────────┬────────┘    │
│           └──────────────────┬┴───────────────────┘             │
│                              ▼                                   │
│                    SHARED BLACKBOARD                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              ROUND 2: PARALLEL REVIEWERS (async)                 │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐    │
│  │  requirements-  │ │  design-        │ │  execution-     │    │
│  │  reviewer       │ │  reviewer       │ │  reviewer       │    │
│  └────────┬────────┘ └────────┬────────┘ └────────┬────────┘    │
│           └──────────────────┬┴───────────────────┘             │
│                              ▼                                   │
│            Cross-review validation + improvements               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│               SYNTHESIS + OUTPUT                                 │
│  • architecture.md blueprint                                     │
│  • Copy-paste implementation prompt                             │
│  • Domain reports from each agent                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Core Features Built

### 1. Parallel Agent Mesh
- **6 specialist agents** running concurrently via `asyncio.gather`
- Round 1: Analysts (requirements, system design, execution planning)
- Round 2: Reviewers (cross-validate and improve Round 1 outputs)
- **Blackboard pattern** for shared state between agents

### 2. RAG Knowledge Pipeline
- ChromaDB vector index built from validated GitHub repositories
- Sentence Transformers for semantic embedding
- Top-K retrieval grounding agent outputs in real-world patterns

### 3. Hybrid Local/Cloud Architecture
- **Local (M4)**: `hub.py` orchestration, CLI, architecture generation
- **Cloud (Tesla T4)**: Unsloth/Llama-3 inference with fine-tuned adapters
- Seamless handoff between local and cloud expert mode

### 4. Enterprise-Grade API
- FastAPI server with `/chat`, `/architecture/generate`, `/status` endpoints
- API key authentication (`X-Architecture-Key` header)
- Rate limiting (in-memory + Redis-backed)
- CORS controls with explicit allowlist

### 5. CLI Tool (`repohunter`)
```bash
repohunter demo --output architecture.md          # Quick demo
repohunter generate --product "X" --requirement "Y"  # Real generation
repohunter status                                 # Health check
```

### 6. Docker Deployment
- `docker-compose.yml` with API + Redis services
- Environment-based configuration
- Production-ready with health checks

---

## 📊 Agent Interaction Model

| Phase | Agents | Output |
|-------|--------|--------|
| **Round 1** | `requirements-analyst`, `system-designer`, `execution-planner` | Initial architecture proposal |
| **Round 2** | `requirements-reviewer`, `design-reviewer`, `execution-reviewer` | Cross-validation + improvements |
| **Synthesis** | Markdown renderer | Final `architecture.md` |

**Key insight**: Not just independent agents merged — explicit cross-agent review before final output.

---

## 💡 Problems Solved

| Problem | Solution |
|---------|----------|
| Architecture planning is slow | 6 agents run in parallel |
| Generic AI outputs lack grounding | RAG retrieval from real GitHub repos |
| Single-perspective blind spots | Multi-agent cross-review catches issues |
| Vibe coding needs structured prompts | Copy-paste-ready implementation output |
| Local GPU limitations | Hybrid local/cloud with expert mode handoff |

---

## 📊 Skills Demonstrated

| Skill Category | Specific Skills |
|----------------|-----------------|
| **AI/ML Engineering** | LLM fine-tuning (Unsloth), RAG pipelines, multi-agent systems |
| **Backend Development** | FastAPI, async Python, API design |
| **System Design** | Distributed systems, blackboard pattern, parallel execution |
| **DevOps** | Docker, Docker Compose, CI/CD, environment management |
| **Data Engineering** | ChromaDB, vector embeddings, Firestore |
| **Security** | API auth, rate limiting, CORS, input validation |

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `github_repohunter/architecture_agents.py` | 6-agent parallel mesh + blackboard |
| `github_repohunter/server.py` | FastAPI API with auth + rate limiting |
| `github_repohunter/rag_engine.py` | ChromaDB index + retrieval |
| `github_repohunter/cli.py` | `repohunter` CLI commands |
| `hub.py` | Local orchestration launcher |
| `docker-compose.yml` | Production deployment stack |

---

## 📝 Interview Talking Points

### "Tell me about this project"
> "RepoHunter is a multi-agent architecture generator. You give it a product description and requirements, and it outputs a production-ready architecture.md blueprint. The key innovation is running 6 specialist agents in parallel — 3 analysts and 3 reviewers — that share context via a blackboard pattern and cross-validate each other's work before synthesis."

### "Why parallel agents instead of one LLM?"
> "Three reasons: 1) Specialized expertise — the requirements agent focuses only on requirements, the system designer only on topology. 2) Speed — 6 agents running concurrently vs sequentially. 3) Quality through cross-review — the reviewer agents explicitly validate and improve the analysts' outputs, catching blind spots."

### "How does RAG improve the output?"
> "Instead of hallucinating architecture patterns, the agents are grounded in real GitHub repositories. ChromaDB retrieves the top 8 relevant repos based on semantic similarity to the requirement. The system-designer agent sees actual project structures, tech stacks, and star counts — so recommendations are based on proven patterns."

### "What was hardest to build?"
> "The cross-agent communication. Each agent runs async and independently, but they need to share context. I implemented a shared blackboard dictionary that agents read from and write to. Round 2 reviewers read all Round 1 outputs before generating their critiques. Getting the timing and data flow right took iteration."

### "How does the hybrid local/cloud work?"
> "Local M4 handles orchestration, RAG retrieval, and the CLI. For heavier inference, the hub connects to a Lightning AI cloud server running Llama-3 with Unsloth fine-tuned adapters on a Tesla T4 GPU. The API key authenticates the connection. You can run fully local with Ollama or switch to cloud expert mode for better quality."

---

## 📈 Production Roadmap (Future Work)

- [ ] Secret management (replace hardcoded defaults)
- [ ] Request tracing + metrics dashboard
- [ ] Typed event contracts for agent mesh
- [ ] Golden tests for architecture artifacts
- [ ] Real-time agent streaming output

---

*Built by Piyush Dua | March 2026*
