import argparse
import asyncio
import json
import os
import sys
import time
from pathlib import Path

from github_repohunter.architecture_agents import run_parallel_agents, render_architecture_markdown
from github_repohunter.rag_engine import build_index, retrieve
from github_repohunter.security_utils import validate_markdown_output_path


# ANSI colors
class Colors:
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    MAGENTA = "\033[95m"
    BLUE = "\033[94m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"


def _banner() -> str:
    return f"""{Colors.CYAN}{Colors.BOLD}
  ╔══════════════════════════════════════════════════════════════╗
  ║                                                              ║
  ║   ██████╗ ███████╗██████╗  ██████╗ ██╗  ██╗██╗   ██╗███╗   ██║
  ║   ██╔══██╗██╔════╝██╔══██╗██╔═══██╗██║  ██║██║   ██║████╗  ██║
  ║   ██████╔╝█████╗  ██████╔╝██║   ██║███████║██║   ██║██╔██╗ ██║
  ║   ██╔══██╗██╔══╝  ██╔═══╝ ██║   ██║██╔══██║██║   ██║██║╚██╗██║
  ║   ██║  ██║███████╗██║     ╚██████╔╝██║  ██║╚██████╔╝██║ ╚████║
  ║   ╚═╝  ╚═╝╚══════╝╚═╝      ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══║
  ║                                                              ║
  ║        {Colors.YELLOW}Parallel Agent Architecture Generator{Colors.CYAN}               ║
  ║                                                              ║
  ╚══════════════════════════════════════════════════════════════╝{Colors.RESET}
"""


def _print_section(title: str) -> None:
    print(f"\n{Colors.BOLD}{Colors.GREEN}▶ {title}{Colors.RESET}")


def _print_agent(name: str, status: str = "running") -> None:
    icons = {
        "running": f"{Colors.YELLOW}⟳{Colors.RESET}",
        "done": f"{Colors.GREEN}✓{Colors.RESET}",
        "waiting": f"{Colors.DIM}○{Colors.RESET}",
    }
    print(f"  {icons.get(status, '○')} {Colors.CYAN}{name}{Colors.RESET}")


def _spinner(text: str, duration: float = 0.5) -> None:
    """Simple inline spinner for visual feedback."""
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    end_time = time.time() + duration
    i = 0
    while time.time() < end_time:
        sys.stdout.write(f"\r  {Colors.YELLOW}{frames[i % len(frames)]}{Colors.RESET} {text}")
        sys.stdout.flush()
        time.sleep(0.08)
        i += 1
    sys.stdout.write(f"\r  {Colors.GREEN}✓{Colors.RESET} {text}\n")
    sys.stdout.flush()


def _load_repos(requirement: str, top_k: int) -> list[dict]:
    try:
        collection = build_index()
        return retrieve(collection, requirement, n_results=top_k)
    except Exception:
        return []


def cmd_generate(args: argparse.Namespace) -> int:
    product = args.product.strip()
    requirement = args.requirement.strip()
    if not product:
        raise SystemExit("error: --product cannot be empty")
    if not requirement:
        raise SystemExit("error: --requirement cannot be empty")
    if len(product) > 200:
        raise SystemExit("error: --product too long (max 200 chars)")
    if len(requirement) > 8000:
        raise SystemExit("error: --requirement too long (max 8000 chars)")
    if args.top_k < 1 or args.top_k > 25:
        raise SystemExit("error: --top-k must be in range [1, 25]")

    if not args.json:
        print(_banner())
        _print_section("Input Configuration")
        print(f"  {Colors.DIM}Product{Colors.RESET}       : {Colors.BOLD}{product}{Colors.RESET}")
        print(f"  {Colors.DIM}Requirement{Colors.RESET}   : {requirement[:100]}{'...' if len(requirement) > 100 else ''}")
        print(f"  {Colors.DIM}Top-K Repos{Colors.RESET}   : {args.top_k}")
        print(f"  {Colors.DIM}Stack Prefs{Colors.RESET}   : {', '.join(args.stack) if args.stack else 'Auto-detect'}")

    if not args.json:
        _print_section("RAG Knowledge Retrieval")
        _spinner("Loading vector index", 0.3)
    repos = _load_repos(args.requirement, args.top_k)
    if not args.json:
        _spinner(f"Retrieved {len(repos)} relevant repositories", 0.2)
        for idx, repo in enumerate(repos[:3], 1):
            print(f"    {Colors.DIM}{idx}.{Colors.RESET} {Colors.CYAN}{repo.get('name','unknown')}{Colors.RESET} ({repo.get('stars',0)}⭐)")

    if not args.json:
        _print_section("Parallel Agent Mesh Execution")
        print(f"\n  {Colors.BOLD}Phase 1: Analysis Agents (parallel){Colors.RESET}")
        _print_agent("requirements-analyst", "running")
        _print_agent("system-designer", "running")
        _print_agent("execution-planner", "running")

    mesh_output = asyncio.run(
        run_parallel_agents(
            requirement=requirement,
            repos=repos,
            stack_preferences=args.stack,
        )
    )

    if not args.json:
        print(f"\n  {Colors.BOLD}Phase 2: Review Agents (parallel){Colors.RESET}")
        _print_agent("requirements-reviewer", "done")
        _print_agent("design-reviewer", "done")
        _print_agent("execution-reviewer", "done")
        print(f"\n  {Colors.BOLD}Phase 3: Synthesis{Colors.RESET}")
        _print_agent("synthesis-agent", "done")

    markdown = render_architecture_markdown(
        product_name=product,
        requirement=requirement,
        mesh_output=mesh_output,
        repos=repos,
    )

    try:
        output_path = validate_markdown_output_path(args.output)
    except ValueError as exc:
        raise SystemExit(f"error: {exc}") from exc
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8")

    if args.json:
        print(
            json.dumps(
                {
                    "output_path": str(output_path),
                    "repos_used": len(repos),
                    "agents": sorted(k for k in mesh_output.keys() if "-" in k),
                },
                indent=2,
            )
        )
    else:
        _print_section("Generation Complete")
        print(f"""
  {Colors.GREEN}╔════════════════════════════════════════════════════════════╗
  ║  {Colors.BOLD}✅ Architecture Generated Successfully!{Colors.RESET}{Colors.GREEN}                    ║
  ╚════════════════════════════════════════════════════════════╝{Colors.RESET}

  {Colors.DIM}Output File{Colors.RESET}   : {Colors.CYAN}{output_path}{Colors.RESET}
  {Colors.DIM}Repos Analyzed{Colors.RESET}: {Colors.YELLOW}{len(repos)}{Colors.RESET} from knowledge base
  {Colors.DIM}Agents Used{Colors.RESET}   : {Colors.YELLOW}{len([k for k in mesh_output.keys() if '-' in k])}{Colors.RESET} parallel specialists
  
  {Colors.BOLD}📋 Next Step:{Colors.RESET}
  Copy the prompt section from {Colors.CYAN}{output_path}{Colors.RESET}
  and paste it into your vibe coding platform (Cursor, Copilot, etc.)
""")
    return 0


def cmd_demo(args: argparse.Namespace) -> int:
    demo_requirement = (
        "Design a production-ready AI architecture copilot that generates architecture.md "
        "for SaaS teams with scalable API, worker orchestration, and observability."
    )
    ns = argparse.Namespace(
        product="RepoHunter Demo Product",
        requirement=demo_requirement,
        output=args.output,
        top_k=6,
        stack=["FastAPI", "PostgreSQL", "Redis", "React"],
        json=args.json,
    )
    return cmd_generate(ns)


def cmd_status(args: argparse.Namespace) -> int:
    out = {
        "cwd": os.getcwd(),
        "index_exists": Path("github_repohunter/database/chroma").exists(),
        "server_module": "github_repohunter.server",
    }
    if getattr(args, "json", False):
        print(json.dumps(out, indent=2))
        return 0
    print(_banner())
    _print_section("Status")
    print(f"Working directory : {out['cwd']}")
    print(f"RAG index exists  : {out['index_exists']}")
    print(f"Server module     : {out['server_module']}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="repohunter", description="RepoHunter CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    gen = sub.add_parser("generate", help="Generate architecture markdown")
    gen.add_argument("--product", required=True, help="Product name")
    gen.add_argument("--requirement", required=True, help="Requirement statement")
    gen.add_argument("--output", default="architecture.md", help="Output markdown path")
    gen.add_argument("--top-k", type=int, default=8, help="Number of repos to retrieve")
    gen.add_argument("--stack", action="append", default=[], help="Preferred stack (repeatable)")
    gen.add_argument("--json", action="store_true", help="JSON output summary")
    gen.set_defaults(func=cmd_generate)

    demo = sub.add_parser("demo", help="Run one-command showcase")
    demo.add_argument("--output", default="architecture.demo.md", help="Demo output path")
    demo.add_argument("--json", action="store_true", help="JSON output summary")
    demo.set_defaults(func=cmd_demo)

    status = sub.add_parser("status", help="Show local status")
    status.add_argument("--json", action="store_true", help="JSON output")
    status.set_defaults(func=cmd_status)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    code = args.func(args)
    raise SystemExit(code)


if __name__ == "__main__":
    main()
