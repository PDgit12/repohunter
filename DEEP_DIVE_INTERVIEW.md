# RepoHunter — Complete Technical Deep Dive

> Use this document to answer any interview question about the project in depth.

---

## Table of Contents
1. [Project Overview](#1-project-overview)
2. [How It Works (End-to-End Flow)](#2-how-it-works-end-to-end-flow)
3. [Architecture Deep Dive](#3-architecture-deep-dive)
4. [Agent System Explained](#4-agent-system-explained)
5. [RAG Pipeline Explained](#5-rag-pipeline-explained)
6. [Code Walkthrough](#6-code-walkthrough)
7. [Tech Stack Details](#7-tech-stack-details)
8. [CLI Commands](#8-cli-commands)
9. [API Endpoints](#9-api-endpoints)
10. [Security Implementation](#10-security-implementation)
11. [Interview Q&A](#11-interview-qa)

---

## 1. Project Overview

### What is RepoHunter?

RepoHunter is a **CLI tool and API** that generates production-ready `architecture.md` blueprints for software projects. Instead of manually designing system architecture, you describe what you want to build, and RepoHunter:

1. **Retrieves** relevant patterns from 13,476 indexed GitHub repositories
2. **Runs 7 AI agents in parallel** to analyze, design, and review the architecture
3. **Outputs** a structured markdown file with copy-paste prompts for vibe coding

### Why Does It Exist?

**Problem:** Starting a new project means spending hours on architecture decisions — what tech stack, how to structure services, what patterns to use.

**Solution:** RepoHunter automates this by:
- Grounding decisions in **real GitHub projects** (not hallucinated patterns)
- Using **multiple specialist agents** that each focus on one aspect
- Producing **copy-paste-ready prompts** for AI coding assistants

### Demo Command
```bash
repohunter demo --output architecture.md
```

This runs the full pipeline and generates an architecture blueprint in seconds.

---

## 2. How It Works (End-to-End Flow)

```
┌─────────────────────────────────────────────────────────────────────┐
│  USER INPUT                                                         │
│  repohunter generate --product "MyApp" --requirement "Need auth..." │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 1: Input Validation                                           │
│  • Product name: max 200 chars                                      │
│  • Requirement: max 8000 chars                                      │
│  • Output path: validated for security (no path traversal)         │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 2: RAG Retrieval                                              │
│  • Load ChromaDB vector index (13,476 repos)                       │
│  • Embed requirement using Sentence Transformers                    │
│  • Retrieve top-K most similar repositories                        │
│  • Return: repo name, language, stars, URL, description            │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 3: Phase 1 - Analysis Agents (PARALLEL)                      │
│  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐    │
│  │ requirements-    │ │ system-          │ │ execution-       │    │
│  │ analyst          │ │ designer         │ │ planner          │    │
│  │                  │ │                  │ │                  │    │
│  │ Extracts:        │ │ Proposes:        │ │ Defines:         │    │
│  │ • Objectives     │ │ • Topology       │ │ • Delivery phases│    │
│  │ • Constraints    │ │ • Components     │ │ • CI/CD approach │    │
│  │ • Success critr. │ │ • Data flow      │ │ • Test strategy  │    │
│  └────────┬─────────┘ └────────┬─────────┘ └────────┬─────────┘    │
│           └────────────────────┼────────────────────┘              │
│                                ▼                                    │
│                        SHARED BLACKBOARD                            │
│                    (Python dict in memory)                          │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 4: Phase 2 - Review Agents (PARALLEL)                        │
│  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐    │
│  │ requirements-    │ │ design-          │ │ execution-       │    │
│  │ reviewer         │ │ reviewer         │ │ reviewer         │    │
│  │                  │ │                  │ │                  │    │
│  │ Cross-checks:    │ │ Cross-checks:    │ │ Cross-checks:    │    │
│  │ • Alignment      │ │ • Completeness   │ │ • Feasibility    │    │
│  │ • Gaps           │ │ • Patterns       │ │ • Risks          │    │
│  └────────┬─────────┘ └────────┬─────────┘ └────────┬─────────┘    │
│           └────────────────────┼────────────────────┘              │
│                                ▼                                    │
│                     BLACKBOARD (updated)                           │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 5: Phase 3 - Synthesis Agent                                  │
│  • Reads all agent outputs from blackboard                         │
│  • Resolves conflicts between agents                               │
│  • Produces final architecture decisions                           │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 6: Markdown Rendering                                         │
│  • Combines all agent outputs into structured markdown             │
│  • Generates copy-paste prompt for vibe coding                     │
│  • Writes to output file                                           │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│  OUTPUT: architecture.md                                            │
│  • Product requirement                                              │
│  • Agent analysis outputs                                          │
│  • Recommended architecture                                        │
│  • Copy-paste implementation prompt                                │
│  • Evidence from indexed repositories                              │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. Architecture Deep Dive

### System Components

```
github_repohunter/
├── cli.py                 # CLI entry point (repohunter command)
├── server.py              # FastAPI REST API
├── architecture_agents.py # 7-agent parallel mesh
├── rag_engine.py          # ChromaDB vector index + retrieval
├── security_utils.py      # Input validation, rate limiting
├── orchestrator.py        # Hub coordination (optional cloud)
└── database/
    └── chroma/            # Persistent vector index (13K repos)
```

### Component Responsibilities

| Component | Responsibility | Key Functions |
|-----------|---------------|---------------|
| `cli.py` | User interface | `cmd_generate()`, `cmd_demo()`, `cmd_status()` |
| `architecture_agents.py` | Agent orchestration | `run_parallel_agents()`, `render_architecture_markdown()` |
| `rag_engine.py` | Knowledge retrieval | `build_index()`, `retrieve()` |
| `server.py` | REST API | `/architecture/generate`, `/status`, `/health/*` |
| `security_utils.py` | Security controls | `validate_markdown_output_path()`, rate limiters |

### Data Flow

```
User Input → CLI/API → RAG Retrieval → Agent Mesh → Markdown Renderer → Output File
                           ↓
                    ChromaDB Index
                    (13,476 repos)
```

---

## 4. Agent System Explained

### Why Multiple Agents?

**Single LLM approach:** One prompt → One perspective → Blind spots

**Multi-agent approach:** 
- Each agent has a **focused role**
- Agents **review each other's work**
- Final output has **multiple expert perspectives**

### The 7 Agents

| Agent | Phase | Role | Input | Output |
|-------|-------|------|-------|--------|
| `requirements-analyst` | 1 | Extract constraints | Requirement, stack prefs | Objectives, success criteria |
| `system-designer` | 1 | Design topology | Requirement, repos | Components, data flow |
| `execution-planner` | 1 | Plan delivery | Requirement | Phases, CI/CD approach |
| `requirements-reviewer` | 2 | Validate requirements | Blackboard | Alignment check, gaps |
| `design-reviewer` | 2 | Validate design | Blackboard | Completeness check |
| `execution-reviewer` | 2 | Validate plan | Blackboard | Feasibility check |
| `synthesis-agent` | 3 | Final synthesis | Blackboard | Unified decisions |

### Parallel Execution Code

```python
# Phase 1: Run 3 agents in parallel
tasks = [
    loop.run_in_executor(None, _requirements_agent, requirement, stack_preferences),
    loop.run_in_executor(None, _system_design_agent, requirement, repos),
    loop.run_in_executor(None, _execution_planner_agent, requirement),
]
phase_one = await asyncio.gather(*tasks)  # All 3 run simultaneously

# Write outputs to shared blackboard
for out in phase_one:
    blackboard[out.agent] = out.content

# Phase 2: Run 3 reviewers in parallel (they read the blackboard)
review_tasks = [
    loop.run_in_executor(None, _cross_review_agent, "requirements-reviewer", blackboard),
    loop.run_in_executor(None, _cross_review_agent, "design-reviewer", blackboard),
    loop.run_in_executor(None, _cross_review_agent, "execution-reviewer", blackboard),
]
reviews = await asyncio.gather(*review_tasks)
```

### Blackboard Pattern

The **blackboard** is a shared dictionary that all agents read from and write to:

```python
blackboard = {
    "requirement": "Build a scalable API...",
    "stack_preferences": ["FastAPI", "PostgreSQL"],
    "repo_candidates": [...],  # From RAG retrieval
    
    # Phase 1 agents write here:
    "requirements-analyst": "Primary objective: ...",
    "system-designer": "Proposed topology: ...",
    "execution-planner": "Delivery phases: ...",
    
    # Phase 2 reviewers write here:
    "requirements-reviewer": "Cross-review: PASS...",
    "design-reviewer": "Cross-review: PASS...",
    "execution-reviewer": "Cross-review: PASS...",
    
    # Phase 3 synthesis writes here:
    "synthesis-agent": "Final decisions: ..."
}
```

---

## 5. RAG Pipeline Explained

### What is RAG?

**RAG = Retrieval-Augmented Generation**

Instead of relying only on the LLM's training data, we:
1. **Retrieve** relevant documents from a knowledge base
2. **Augment** the prompt with this retrieved context
3. **Generate** output grounded in real data

### How RepoHunter Uses RAG

```
┌─────────────────────────────────────────────────────────────────┐
│  KNOWLEDGE BASE: 13,476 GitHub Repositories                     │
│                                                                 │
│  Each repo has:                                                 │
│  • name, description, language, stars, URL                     │
│  • Vector embedding (384 dimensions via MiniLM)                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  RETRIEVAL PROCESS                                              │
│                                                                 │
│  1. User requirement: "Build a scalable auth system"           │
│  2. Embed requirement → 384-dim vector                         │
│  3. Query ChromaDB for nearest neighbors                       │
│  4. Return top-K repos (default: 8)                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  AUGMENTATION                                                   │
│                                                                 │
│  Agents receive retrieved repos as context:                    │
│  "Repository grounding:                                        │
│   1. supabase/supabase | TypeScript | 52000⭐                  │
│   2. authelia/authelia | Go | 18000⭐                          │
│   ..."                                                         │
└─────────────────────────────────────────────────────────────────┘
```

### RAG Code Walkthrough

```python
# rag_engine.py

def build_index() -> Collection:
    """Build or load the ChromaDB vector index."""
    client = chromadb.PersistentClient(path="github_repohunter/database/chroma")
    collection = client.get_or_create_collection(
        name="repos",
        embedding_function=SentenceTransformerEmbeddingFunction(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
    )
    
    if collection.count() == 0:
        # Load repos from JSONL and add to index
        repos = load_repos_from_jsonl()
        collection.add(
            documents=[r["description"] for r in repos],
            metadatas=repos,
            ids=[r["name"] for r in repos]
        )
    
    return collection


def retrieve(collection: Collection, query: str, n_results: int = 8) -> list[dict]:
    """Retrieve top-K similar repositories."""
    results = collection.query(query_texts=[query], n_results=n_results)
    return results["metadatas"][0]  # List of repo dicts
```

### Why 13,476 Repos?

The knowledge base was built by:
1. **Discovery**: Scanning GitHub for repos matching quality criteria
2. **Validation**: Filtering for stars, recent activity, proper documentation
3. **Indexing**: Embedding descriptions with Sentence Transformers
4. **Storage**: Persisting in ChromaDB for fast retrieval

---

## 6. Code Walkthrough

### Entry Point: CLI

```python
# cli.py - main()
def main():
    parser = build_parser()
    args = parser.parse_args()
    code = args.func(args)  # Calls cmd_generate, cmd_demo, or cmd_status
    raise SystemExit(code)
```

### Generate Command Flow

```python
# cli.py - cmd_generate()
def cmd_generate(args):
    # 1. Validate inputs
    product = args.product.strip()
    requirement = args.requirement.strip()
    
    # 2. RAG retrieval
    repos = _load_repos(requirement, args.top_k)
    
    # 3. Run parallel agents
    mesh_output = asyncio.run(
        run_parallel_agents(
            requirement=requirement,
            repos=repos,
            stack_preferences=args.stack,
        )
    )
    
    # 4. Render markdown
    markdown = render_architecture_markdown(
        product_name=product,
        requirement=requirement,
        mesh_output=mesh_output,
        repos=repos,
    )
    
    # 5. Write output
    output_path.write_text(markdown)
    return 0
```

### Agent Execution

```python
# architecture_agents.py - run_parallel_agents()
async def run_parallel_agents(requirement, repos, stack_preferences):
    loop = asyncio.get_running_loop()
    blackboard = {"requirement": requirement, ...}
    
    # Phase 1: Analysis (parallel)
    tasks = [
        loop.run_in_executor(None, _requirements_agent, ...),
        loop.run_in_executor(None, _system_design_agent, ...),
        loop.run_in_executor(None, _execution_planner_agent, ...),
    ]
    phase_one = await asyncio.gather(*tasks)
    
    # Write to blackboard
    for out in phase_one:
        blackboard[out.agent] = out.content
    
    # Phase 2: Review (parallel)
    review_tasks = [...]
    reviews = await asyncio.gather(*review_tasks)
    
    # Phase 3: Synthesis
    synthesis = await loop.run_in_executor(None, _synthesis_agent, blackboard)
    
    return blackboard
```

---

## 7. Tech Stack Details

| Technology | Purpose | Why This Choice |
|------------|---------|-----------------|
| **Python 3.12+** | Core language | Async support, type hints, ecosystem |
| **FastAPI** | REST API | Async, auto-docs, Pydantic validation |
| **asyncio** | Parallel execution | Native async/await for concurrent agents |
| **ChromaDB** | Vector database | Embedded, persistent, Python-native |
| **Sentence Transformers** | Embeddings | MiniLM-L6-v2 is fast and effective |
| **Redis** | Rate limiting (optional) | Distributed rate limit state |
| **Docker** | Deployment | Reproducible, portable |

### Dependencies (pyproject.toml)

```toml
dependencies = [
  "fastapi",
  "uvicorn[standard]",
  "pydantic",
  "python-dotenv",
  "httpx",
  "requests",
  "chromadb",
  "sentence-transformers",
  "redis",
]
```

---

## 8. CLI Commands

### `repohunter generate`

Generate a custom architecture:

```bash
repohunter generate \
  --product "MyApp" \
  --requirement "Build a scalable microservices architecture with auth" \
  --stack FastAPI --stack PostgreSQL --stack Redis \
  --top-k 10 \
  --output architecture.md
```

**Flags:**
| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--product` | Yes | - | Product name |
| `--requirement` | Yes | - | What you want to build |
| `--stack` | No | Auto | Preferred tech (repeatable) |
| `--top-k` | No | 8 | Number of repos to retrieve |
| `--output` | No | `architecture.md` | Output file path |
| `--json` | No | False | Output JSON summary |

### `repohunter demo`

Quick showcase:

```bash
repohunter demo --output architecture.demo.md
```

### `repohunter status`

Check system health:

```bash
repohunter status
```

---

## 9. API Endpoints

### POST `/architecture/generate`

```bash
curl -X POST http://localhost:8000/architecture/generate \
  -H "Content-Type: application/json" \
  -H "X-Architecture-Key: your-api-key" \
  -d '{
    "product_name": "MyApp",
    "requirement": "Build a scalable auth system",
    "write_file": true,
    "output_path": "architecture.md"
  }'
```

### GET `/status`

```bash
curl http://localhost:8000/status
```

### GET `/health/live` and `/health/ready`

Kubernetes-style health probes.

---

## 10. Security Implementation

### Input Validation

```python
# cli.py
if len(product) > 200:
    raise SystemExit("error: --product too long (max 200 chars)")
if len(requirement) > 8000:
    raise SystemExit("error: --requirement too long (max 8000 chars)")
```

### Path Traversal Prevention

```python
# security_utils.py
def validate_markdown_output_path(path: str) -> Path:
    """Prevent path traversal attacks."""
    if ".." in path or path.startswith("/"):
        raise ValueError("Invalid path: no absolute paths or parent traversal")
    if not path.endswith(".md"):
        raise ValueError("Output must be a .md file")
    return Path(path)
```

### API Key Authentication

```python
# server.py
ARCHITECTURE_API_KEY = os.getenv("ARCHITECTURE_API_KEY")

@app.post("/architecture/generate")
async def generate(request: Request, body: GenerateRequest):
    if ARCHITECTURE_API_KEY:
        key = request.headers.get("X-Architecture-Key")
        if not hmac.compare_digest(key or "", ARCHITECTURE_API_KEY):
            raise HTTPException(401, "Invalid API key")
    ...
```

### Rate Limiting

```python
# security_utils.py
class SlidingWindowRateLimiter:
    """In-memory rate limiter."""
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)
    
    def is_allowed(self, client_id: str) -> bool:
        now = time.time()
        # Remove old requests outside window
        self.requests[client_id] = [
            t for t in self.requests[client_id] 
            if now - t < self.window_seconds
        ]
        if len(self.requests[client_id]) >= self.max_requests:
            return False
        self.requests[client_id].append(now)
        return True
```

---

## 11. Interview Q&A

### "Tell me about this project in 30 seconds"

> "RepoHunter is a CLI tool that generates architecture blueprints for software projects. You describe what you want to build, and it retrieves relevant patterns from 13,000 indexed GitHub repos, runs 7 AI agents in parallel to analyze and review the architecture, and outputs a markdown file with copy-paste prompts for AI coding assistants. The key innovation is the multi-agent parallel mesh — instead of one LLM perspective, you get 7 specialist agents that cross-validate each other's work."

### "Why parallel agents instead of one prompt?"

> "Three reasons:
> 1. **Specialization** — each agent focuses on one thing. The requirements agent only extracts constraints, the system designer only proposes topology.
> 2. **Speed** — 7 agents running concurrently vs. sequentially.
> 3. **Quality** — the reviewer agents explicitly cross-check the analysts' work, catching blind spots a single LLM would miss."

### "How does RAG improve output quality?"

> "Without RAG, the LLM would hallucinate architecture patterns based on training data that might be outdated. With RAG, we ground decisions in real GitHub projects — if the user asks for an auth system, we retrieve repos like Supabase and Authelia that actually implement auth well. The agents see 'this is what successful projects do' not 'this is what I imagine a project might do.'"

### "Explain the blackboard pattern"

> "The blackboard is a shared data structure — in our case, a Python dictionary. All agents read from it and write to it. Phase 1 agents write their analysis, then Phase 2 reviewers read that analysis and write their critiques, then the synthesis agent reads everything and produces final decisions. It's like a shared whiteboard where each expert adds their contribution and can see what others wrote."

### "What was the hardest technical challenge?"

> "Getting the async coordination right. Each agent is a synchronous function, but we want them to run in parallel. I used `asyncio.gather()` with `run_in_executor()` to run blocking functions concurrently. The tricky part was ensuring the blackboard updates were visible to later phases without race conditions — solved by running phases sequentially (Phase 1 completes before Phase 2 starts) while parallelizing within each phase."

### "Why ChromaDB for the vector store?"

> "ChromaDB is embedded — it runs in-process without needing a separate server. For a CLI tool that needs to work offline, this is perfect. It persists to disk, so the 13K repo index loads instantly on subsequent runs. And it's Python-native, so no JNI bridges or network calls. For production scale, I'd consider Pinecone or Weaviate, but for local-first developer tooling, ChromaDB is ideal."

### "How would you scale this to production?"

> "Several changes:
> 1. **Replace deterministic agents with LLM calls** — current agents are template-based for demo; production would call Claude/GPT.
> 2. **Add caching** — cache RAG retrieval and agent outputs keyed by requirement hash.
> 3. **Kubernetes deployment** — scale API horizontally, Redis for rate limiting state.
> 4. **Observability** — add tracing (OpenTelemetry), metrics (Prometheus), logging (structured JSON).
> 5. **Queue for long jobs** — architecture generation could be async with job status polling."

### "What would you improve with more time?"

> "1. **Real LLM integration** — replace template agents with actual Claude/GPT calls.
> 2. **Streaming output** — show agent progress in real-time instead of waiting for all to complete.
> 3. **Custom repo index** — let users add their own company's repos to the knowledge base.
> 4. **Learning from feedback** — track which generated architectures users actually use and improve retrieval accordingly."

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────────┐
│  REPOHUNTER QUICK REFERENCE                                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  INSTALL:    pip install -e .                                   │
│  DEMO:       repohunter demo                                    │
│  GENERATE:   repohunter generate --product X --requirement Y    │
│  STATUS:     repohunter status                                  │
│                                                                 │
│  AGENTS:     7 total (3 analysts + 3 reviewers + 1 synthesis)  │
│  RAG INDEX:  13,476 GitHub repositories                        │
│  OUTPUT:     architecture.md with copy-paste prompts           │
│                                                                 │
│  TECH:       Python, FastAPI, ChromaDB, asyncio                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

*Last Updated: March 2026*
