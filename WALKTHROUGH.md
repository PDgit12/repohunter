# RepoHunter - Quick Walkthrough

## What It Does
RepoHunter generates production-ready `architecture.md` blueprints for SaaS products using 7 parallel AI agents and RAG retrieval from 13,000+ GitHub repositories.

## Quick Demo (30 seconds)

```bash
# Install
pip install -e .

# Run demo
repohunter demo --output my-architecture.md
```

**Expected Output:**
```
╔══════════════════════════════════════════════════════════════╗
║   ██████╗ ███████╗██████╗  ██████╗ ██╗  ██╗██╗   ██╗███╗   ██║
║   ██████╔╝█████╗  ██████╔╝██║   ██║███████║██║   ██║██╔██╗ ██║
║        Parallel Agent Architecture Generator               ║
╚══════════════════════════════════════════════════════════════╝

▶ Input Configuration
  Product       : RepoHunter Demo Product
  Top-K Repos   : 6
  Stack Prefs   : FastAPI, PostgreSQL, Redis, React

▶ RAG Knowledge Retrieval
  ✓ Loading vector index
  ✅ RAG index: 13476 repos loaded
  ✓ Retrieved 6 relevant repositories

▶ Parallel Agent Mesh Execution
  Phase 1: Analysis Agents (parallel)
    ⟳ requirements-analyst
    ⟳ system-designer
    ⟳ execution-planner

  Phase 2: Review Agents (parallel)
    ✓ requirements-reviewer
    ✓ design-reviewer
    ✓ execution-reviewer

  Phase 3: Synthesis
    ✓ synthesis-agent

▶ Generation Complete
  ╔════════════════════════════════════════════════════════════╗
  ║  ✅ Architecture Generated Successfully!                    ║
  ╚════════════════════════════════════════════════════════════╝
  Output File   : my-architecture.md
```

## How It Works

### 1. RAG Retrieval
- Loads 13,476 pre-indexed GitHub repositories from ChromaDB
- Uses Sentence Transformers (MiniLM-L6-v2) for semantic search
- Finds similar architectures based on your product description

### 2. Parallel Agent Execution
```
Phase 1 (Parallel):           Phase 2 (Parallel):         Phase 3:
┌─────────────────┐           ┌─────────────────┐         ┌─────────────────┐
│ Requirements    │──write──► │ Requirements    │──read──►│                 │
│ Analyst         │           │ Reviewer        │         │                 │
└─────────────────┘           └─────────────────┘         │   Synthesis     │
┌─────────────────┐           ┌─────────────────┐         │   Agent         │
│ System          │──write──► │ Design          │──read──►│                 │
│ Designer        │           │ Reviewer        │         │                 │
└─────────────────┘           └─────────────────┘         └─────────────────┘
┌─────────────────┐           ┌─────────────────┐                 │
│ Execution       │──write──► │ Execution       │──────────────────┘
│ Planner         │           │ Reviewer        │
└─────────────────┘           └─────────────────┘
        │                              │
        └──────────► BLACKBOARD ◄──────┘
                   (shared state)
```

### 3. Blackboard Pattern
All agents communicate through a shared dictionary:
- Analysts **write** their analysis
- Reviewers **read** + **write** reviews
- Synthesizer **reads all** + generates final output

### 4. Output Generation
The synthesizer merges all outputs into a structured `architecture.md`:
- Executive summary
- Tech stack decisions
- API design
- Data models
- Deployment specs

## Commands

| Command | Description |
|---------|-------------|
| `repohunter demo` | Run showcase with built-in example |
| `repohunter generate -p "My product idea"` | Generate for custom product |
| `repohunter status` | Check RAG index and system status |

## Tech Stack

- **Python 3.10+** - Core language
- **asyncio** - Parallel agent execution
- **ChromaDB** - Vector database for RAG
- **Sentence Transformers** - Embedding model
- **Typer** - CLI framework
- **FastAPI** - API server (optional)

## Project Structure

```
github_repohunter/
├── cli.py               # CLI entry point (visual output)
├── architecture_agents.py  # 7-agent parallel mesh
├── rag_engine.py        # ChromaDB + embeddings
├── server.py            # FastAPI server
└── database/            # ChromaDB index (13K repos)
```

## Key Files

| File | Lines | Purpose |
|------|-------|---------|
| `cli.py` | 180 | Visual CLI with ASCII art, colors, progress |
| `architecture_agents.py` | 200 | Parallel agent orchestration |
| `rag_engine.py` | 150 | Vector index build + retrieval |

---

**Author:** Piyush Dua  
**License:** MIT
