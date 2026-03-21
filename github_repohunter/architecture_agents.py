import asyncio
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any


@dataclass
class AgentOutput:
    agent: str
    content: str


def _repo_summary(requirement: str, repos: list[dict[str, Any]]) -> str:
    if not repos:
        return "No indexed repositories were retrieved for this requirement."
    lines = [f"Requirement signal: {requirement}", ""]
    for idx, repo in enumerate(repos[:8], 1):
        lines.append(
            f"{idx}. {repo.get('name', 'unknown')} | {repo.get('language', 'n/a')} | "
            f"{repo.get('stars', 0)} stars | {repo.get('url', '')}"
        )
        lines.append(f"   Fit hint: {repo.get('description', 'No description')}")
    return "\n".join(lines)


def _requirements_agent(requirement: str, stack_preferences: list[str] | None = None) -> AgentOutput:
    prefs = ", ".join(stack_preferences or []) or "No explicit stack preferences"
    return AgentOutput(
        agent="requirements-analyst",
        content=(
            f"Primary objective: {requirement}\n"
            f"Stack preferences: {prefs}\n"
            "Success criteria:\n"
            "- Modular, production-ready architecture.\n"
            "- Clear boundaries between API, workers, storage, and observability.\n"
            "- Copy-paste-ready implementation prompt."
        ),
    )


def _system_design_agent(requirement: str, repos: list[dict[str, Any]]) -> AgentOutput:
    return AgentOutput(
        agent="system-designer",
        content=(
            "Proposed topology:\n"
            "- API Gateway + auth middleware\n"
            "- Orchestrator service for workflow execution\n"
            "- Parallel specialist agents (planner, backend, frontend, data, qa)\n"
            "- Shared event bus + state store for inter-agent communication\n"
            "- RAG knowledge service fed by validated repo corpus\n"
            "- Artifact writer service that emits architecture.md and implementation prompt\n\n"
            f"Repository grounding:\n{_repo_summary(requirement, repos)}"
        ),
    )


def _execution_planner_agent(requirement: str) -> AgentOutput:
    return AgentOutput(
        agent="execution-planner",
        content=(
            "Delivery phases:\n"
            "1) Contracts: API schema, shared message format, event types.\n"
            "2) Agent mesh: concurrent agent runtime with shared blackboard.\n"
            "3) Architecture synthesis: deterministic markdown renderer + optional LLM polish.\n"
            "4) Reliability: retries, timeouts, tracing, metrics.\n"
            "5) CI/CD + tests + docs.\n"
            f"Constraint anchor: {requirement}"
        ),
    )


def _cross_review_agent(
    agent_name: str,
    board: dict[str, Any],
) -> AgentOutput:
    req = board.get("requirements-analyst", "")
    design = board.get("system-designer", "")
    plan = board.get("execution-planner", "")
    critique = (
        f"{agent_name} cross-review:\n"
        f"- Requirement alignment check: {'PASS' if req else 'NEEDS_INPUT'}\n"
        f"- Design completeness check: {'PASS' if design else 'NEEDS_INPUT'}\n"
        f"- Execution feasibility check: {'PASS' if plan else 'NEEDS_INPUT'}\n"
        "- Improvement actions:\n"
        "  1) Add explicit API contracts between gateway/orchestrator.\n"
        "  2) Define failure handling for each agent stage.\n"
        "  3) Ensure artifact generation is deterministic when LLM unavailable."
    )
    return AgentOutput(agent=agent_name, content=critique)


async def run_parallel_agents(
    requirement: str,
    repos: list[dict[str, Any]],
    stack_preferences: list[str] | None = None,
) -> dict[str, Any]:
    loop = asyncio.get_running_loop()
    blackboard: dict[str, Any] = {
        "requirement": requirement,
        "stack_preferences": stack_preferences or [],
        "repo_candidates": repos,
    }

    tasks = [
        loop.run_in_executor(None, _requirements_agent, requirement, stack_preferences),
        loop.run_in_executor(None, _system_design_agent, requirement, repos),
        loop.run_in_executor(None, _execution_planner_agent, requirement),
    ]
    phase_one = await asyncio.gather(*tasks)
    for out in phase_one:
        blackboard[out.agent] = out.content

    review_tasks = [
        loop.run_in_executor(None, _cross_review_agent, "requirements-reviewer", blackboard),
        loop.run_in_executor(None, _cross_review_agent, "design-reviewer", blackboard),
        loop.run_in_executor(None, _cross_review_agent, "execution-reviewer", blackboard),
    ]
    reviews = await asyncio.gather(*review_tasks)
    for out in reviews:
        blackboard[out.agent] = out.content

    def _synthesis_agent(board: dict[str, Any]) -> AgentOutput:
        return AgentOutput(
            agent="synthesis-agent",
            content=(
                "Cross-agent synthesis:\n"
                f"- Requirement signal captured: {board.get('requirement')}\n"
                f"- Requirements constraints: {board.get('requirements-analyst', '')[:300]}\n"
                f"- System topology draft: {board.get('system-designer', '')[:300]}\n"
                f"- Execution phases draft: {board.get('execution-planner', '')[:300]}\n"
                f"- Reviewer loop notes: {board.get('design-reviewer', '')[:240]}\n"
                "Decision: keep parallel mesh + shared blackboard + artifact renderer as core architecture pattern."
            ),
        )

    synthesis = await loop.run_in_executor(None, _synthesis_agent, blackboard)
    blackboard[synthesis.agent] = synthesis.content
    return blackboard


def render_architecture_markdown(
    product_name: str,
    requirement: str,
    mesh_output: dict[str, Any],
    repos: list[dict[str, Any]],
) -> str:
    timestamp = datetime.now(UTC).isoformat()
    repo_lines = "\n".join(
        [
            f"- **{r.get('name', 'unknown')}** ({r.get('language', 'n/a')}, {r.get('stars', 0)}⭐): {r.get('url', '')}"
            for r in repos[:8]
        ]
    ) or "- No repository evidence found in local index."

    return f"""# {product_name} — Architecture Blueprint

Generated at: `{timestamp}`

## 1. Product Requirement
{requirement}

## 2. Parallel Agent Mesh Design
The system uses parallel specialist agents that communicate through a shared context store (blackboard) and event bus.

### Agent Outputs
#### Requirements Analyst
{mesh_output.get("requirements-analyst", "")}

#### System Designer
{mesh_output.get("system-designer", "")}

#### Execution Planner
{mesh_output.get("execution-planner", "")}

#### Reviewer Loop
{mesh_output.get("requirements-reviewer", "")}

{mesh_output.get("design-reviewer", "")}

{mesh_output.get("execution-reviewer", "")}

#### Synthesis Agent
{mesh_output.get("synthesis-agent", "")}

## 3. Recommended System Architecture
- **API Layer**: FastAPI service exposing `/chat`, `/architecture/generate`, `/status`.
- **Orchestration Layer**: Concurrent agent runtime (`asyncio`) with explicit contracts.
- **Knowledge Layer**: Chroma vector store + retriever grounded on validated repo corpus.
- **Generation Layer**: Markdown artifact renderer + optional expert model refinement.
- **Data Layer**: Firestore/JSONL datasets for discovery, synthesis, and training.
- **Ops Layer**: Logging, metrics, health checks, deployment to local/cloud.

## 4. Communication Model (Agent-to-Agent)
- Every agent reads a shared input contract.
- Every agent writes a structured output block to the blackboard.
- Aggregator combines blocks into:
  - architecture decisions
  - implementation phases
  - risks and mitigations
- Finalizer produces `architecture.md` and an implementation prompt.

## 5. Copy-Paste Prompt For Vibe Coding Platforms
```md
Build a production-ready implementation from this architecture:

Product: {product_name}
Requirement: {requirement}

Constraints:
- Use modular services (API, orchestration, knowledge, artifact generation).
- Implement parallel specialist agents that communicate via shared context + event messages.
- Include observability, retry strategy, and typed request/response contracts.
- Generate a final architecture.md artifact from agent outputs.

Deliverables:
1. Backend service with endpoints for chat + architecture generation
2. Agent mesh runtime (parallel execution + aggregation)
3. RAG integration for evidence-grounded decisions
4. Test suite and CI checks
5. Deployment-ready configuration
```

## 6. Evidence From Indexed Repositories
{repo_lines}

## 7. Production Readiness Checklist
- Contract-first API design
- End-to-end tests for generation pipeline
- Deterministic fallback when LLM unavailable
- Secret management + auth hardening
- Monitoring dashboards + alerting
- Release automation and rollback plan
"""
