import asyncio
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from github_repohunter.llm_client import get_llm_client, LLMClient, TemplateClient


@dataclass
class AgentOutput:
    agent: str
    content: str


# Global LLM client (lazy initialized)
_llm_client: LLMClient | None = None


def _get_llm() -> LLMClient:
    """Get or initialize the LLM client"""
    global _llm_client
    if _llm_client is None:
        _llm_client = get_llm_client()
    return _llm_client


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
    """Analyze requirements and produce structured output"""
    prefs = ", ".join(stack_preferences or []) or "No explicit stack preferences"
    llm = _get_llm()
    
    if isinstance(llm, TemplateClient):
        # Fallback template mode
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
    
    prompt = f"""You are a senior requirements analyst. Analyze this product requirement and produce a structured analysis.

REQUIREMENT: {requirement}
STACK PREFERENCES: {prefs}

Produce a concise analysis with:
1. Primary objective (1-2 sentences)
2. Key functional requirements (bullet points)
3. Non-functional requirements (performance, security, scalability)
4. Success criteria (measurable outcomes)
5. Constraints and assumptions

Be specific and actionable. No fluff."""

    try:
        response = llm.generate(prompt, system="You are a senior software architect specializing in requirements analysis.")
        return AgentOutput(agent="requirements-analyst", content=response)
    except Exception as e:
        return AgentOutput(agent="requirements-analyst", content=f"[Error: {e}] Fallback: {requirement}")


def _system_design_agent(requirement: str, repos: list[dict[str, Any]]) -> AgentOutput:
    """Design system architecture based on requirement and similar repos"""
    llm = _get_llm()
    repo_context = _repo_summary(requirement, repos)
    
    if isinstance(llm, TemplateClient):
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
                f"Repository grounding:\n{repo_context}"
            ),
        )
    
    prompt = f"""You are a senior system architect. Design the system architecture for this product.

REQUIREMENT: {requirement}

SIMILAR REPOSITORIES FOR REFERENCE:
{repo_context}

Produce a detailed system design including:
1. High-level architecture diagram (describe in text)
2. Core services/components and their responsibilities
3. Data flow between components
4. API design (key endpoints)
5. Database schema design (key entities)
6. Technology stack recommendations with justification
7. Scalability considerations

Be specific about technology choices. Reference patterns from the similar repositories where applicable."""

    try:
        response = llm.generate(prompt, system="You are a senior software architect with 15+ years experience designing scalable systems.")
        return AgentOutput(agent="system-designer", content=response)
    except Exception as e:
        return AgentOutput(agent="system-designer", content=f"[Error: {e}] Fallback design needed")


def _execution_planner_agent(requirement: str) -> AgentOutput:
    """Plan execution phases and milestones"""
    llm = _get_llm()
    
    if isinstance(llm, TemplateClient):
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
    
    prompt = f"""You are a senior engineering manager. Create an execution plan for building this product.

REQUIREMENT: {requirement}

Produce a detailed execution plan including:
1. Development phases (with clear milestones)
2. Task breakdown for each phase
3. Dependencies between tasks
4. Risk assessment and mitigation strategies
5. Testing strategy (unit, integration, e2e)
6. Deployment strategy (staging, production)
7. Estimated timeline (in sprints/weeks)

Be realistic about timelines. Identify critical path items."""

    try:
        response = llm.generate(prompt, system="You are a senior engineering manager with expertise in agile delivery.")
        return AgentOutput(agent="execution-planner", content=response)
    except Exception as e:
        return AgentOutput(agent="execution-planner", content=f"[Error: {e}] Fallback plan needed")


def _cross_review_agent(agent_name: str, board: dict[str, Any]) -> AgentOutput:
    """Review and critique other agents' outputs"""
    llm = _get_llm()
    req = board.get("requirements-analyst", "")
    design = board.get("system-designer", "")
    plan = board.get("execution-planner", "")
    
    if isinstance(llm, TemplateClient):
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
    
    review_focus = {
        "requirements-reviewer": "requirements completeness, clarity, and testability",
        "design-reviewer": "architecture soundness, scalability, and maintainability", 
        "execution-reviewer": "plan feasibility, risk coverage, and timeline realism"
    }
    
    prompt = f"""You are a senior technical reviewer. Review the following outputs from other architects.

REQUIREMENTS ANALYSIS:
{req[:1500]}

SYSTEM DESIGN:
{design[:1500]}

EXECUTION PLAN:
{plan[:1500]}

Your focus: {review_focus.get(agent_name, 'overall quality')}

Provide a structured review:
1. Strengths (what's good)
2. Gaps (what's missing)
3. Risks (potential issues)
4. Recommendations (specific improvements)

Be constructive and specific."""

    try:
        response = llm.generate(prompt, system=f"You are a {agent_name} conducting a technical review.")
        return AgentOutput(agent=agent_name, content=response)
    except Exception as e:
        return AgentOutput(agent=agent_name, content=f"[Error: {e}] Review incomplete")


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
        """Synthesize all agent outputs into final decisions"""
        llm = _get_llm()
        
        if isinstance(llm, TemplateClient):
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
        
        prompt = f"""You are the chief architect synthesizing inputs from multiple specialist agents.

ORIGINAL REQUIREMENT:
{board.get('requirement')}

REQUIREMENTS ANALYSIS:
{board.get('requirements-analyst', '')[:2000]}

SYSTEM DESIGN:
{board.get('system-designer', '')[:2000]}

EXECUTION PLAN:
{board.get('execution-planner', '')[:2000]}

REVIEW FEEDBACK:
Requirements Review: {board.get('requirements-reviewer', '')[:800]}
Design Review: {board.get('design-reviewer', '')[:800]}
Execution Review: {board.get('execution-reviewer', '')[:800]}

Synthesize all inputs into FINAL DECISIONS:
1. Final architecture decision (what to build)
2. Technology stack (final choices with brief justification)
3. Key components and their interfaces
4. Critical implementation priorities (ordered)
5. Risk mitigations to implement
6. Success metrics

Be decisive. This is the final architecture document."""

        try:
            response = llm.generate(prompt, system="You are a chief software architect making final architecture decisions.")
            return AgentOutput(agent="synthesis-agent", content=response)
        except Exception as e:
            return AgentOutput(agent="synthesis-agent", content=f"[Error: {e}] Synthesis incomplete")

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
