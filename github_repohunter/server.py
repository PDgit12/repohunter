from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
import httpx
import time
import hmac
import logging
from uuid import uuid4
from dotenv import load_dotenv
from github_repohunter.rag_engine import build_index, retrieve, format_context
from github_repohunter.architecture_agents import run_parallel_agents, render_architecture_markdown
from github_repohunter.security_utils import (
    validate_markdown_output_path,
    SlidingWindowRateLimiter,
    RedisSlidingWindowRateLimiter,
    parse_api_keys,
)

load_dotenv() # Load variables from .env
logger = logging.getLogger("repohunter.api")
logging.basicConfig(level=logging.INFO)

USE_CLOUD = os.getenv("USE_CLOUD", "false").lower() == "true"
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").strip().lower()
CLOUD_ENDPOINT = os.getenv("CLOUD_EXPERT_ENDPOINT")
EXPERT_API_KEY = os.getenv("EXPERT_API_KEY")
ARCHITECTURE_API_KEYS = parse_api_keys(
    os.getenv("ARCHITECTURE_API_KEYS"),
    os.getenv("ARCHITECTURE_API_KEY"),
)
ALLOW_ORIGINS = [
    origin.strip()
    for origin in os.getenv("ALLOW_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
    if origin.strip()
]
ARCH_RATE_LIMIT_PER_MIN = int(os.getenv("ARCH_RATE_LIMIT_PER_MIN", "20"))
REDIS_URL = os.getenv("REDIS_URL", "").strip()
ALLOW_IN_MEMORY_RATE_LIMIT_FALLBACK = os.getenv("ALLOW_IN_MEMORY_RATE_LIMIT_FALLBACK", "true").lower() == "true"
_rate_limiter: SlidingWindowRateLimiter | RedisSlidingWindowRateLimiter = SlidingWindowRateLimiter(
    limit_per_minute=ARCH_RATE_LIMIT_PER_MIN
)
if REDIS_URL:
    try:
        import redis
        _rate_limiter = RedisSlidingWindowRateLimiter(
            redis_client=redis.Redis.from_url(REDIS_URL, decode_responses=True),
            limit_per_minute=ARCH_RATE_LIMIT_PER_MIN,
        )
        print("✅ Redis-backed rate limiter enabled.")
    except Exception as exc:
        if ENVIRONMENT == "production" and not ALLOW_IN_MEMORY_RATE_LIMIT_FALLBACK:
            raise RuntimeError(f"Redis limiter required in production but unavailable: {exc}") from exc
        print(f"⚠️ Redis limiter unavailable, falling back to memory limiter: {exc}")

if not USE_CLOUD:
    try:
        import mlx_lm
    except ImportError:
        print("⚠️ MLX not found. Defaulting to Cloud Mode (please set USE_CLOUD=true in .env)")
        USE_CLOUD = True

if ENVIRONMENT == "production":
    if not ARCHITECTURE_API_KEYS:
        raise RuntimeError("Production requires ARCHITECTURE_API_KEY(S) to be configured.")
    if not ALLOW_ORIGINS:
        raise RuntimeError("Production requires explicit ALLOW_ORIGINS.")
    if ARCH_RATE_LIMIT_PER_MIN <= 0:
        raise RuntimeError("ARCH_RATE_LIMIT_PER_MIN must be > 0 in production.")

app = FastAPI(title="RepoHunter API Bridge")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid4()))
    request.state.request_id = request_id
    start = time.time()
    logger.info("request.start id=%s method=%s path=%s", request_id, request.method, request.url.path)
    try:
        response = await call_next(request)
    except Exception as exc:
        logger.exception("request.error id=%s error=%s", request_id, exc)
        return JSONResponse(status_code=500, content={"detail": "internal server error", "request_id": request_id})
    duration_ms = int((time.time() - start) * 1000)
    response.headers["X-Request-ID"] = request_id
    logger.info(
        "request.end id=%s method=%s path=%s status=%s duration_ms=%s",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response

# --- Model Loading ---
MODEL_PATH = os.getenv("MODEL_NAME", "mlx-community/Meta-Llama-3-8B-Instruct-4bit")
ADAPTER_PATH = "github_repohunter/training/adapters"

model, tokenizer = None, None

if not USE_CLOUD:
    print("⏳ Loading RepoHunter Model into local memory (MLX)...")
    try:
        model, tokenizer = mlx_lm.load(MODEL_PATH, adapter_path=ADAPTER_PATH)
        print("✅ Model loaded successfully.")
    except Exception as e:
        print(f"❌ Failed to load local model: {e}")
else:
    print(f"☁️ Cloud Mode Enabled. Targeting: {CLOUD_ENDPOINT}")

# --- RAG Index Loading ---
print("📚 Loading RAG index...")
try:
    rag_collection = build_index()
    print(f"✅ RAG ready: {rag_collection.count()} repos indexed.")
except Exception as e:
    print(f"❌ Failed to load RAG index: {e}")
    rag_collection = None


class ChatRequest(BaseModel):
    query: str


class ArchitectureRequest(BaseModel):
    product_name: str
    requirement: str
    stack_preferences: list[str] | None = None
    write_file: bool = True
    output_path: str = "architecture.md"


def _enforce_rate_limit(client_id: str, now_ts: float) -> None:
    try:
        _rate_limiter.check(client_id, now_ts)
    except ValueError as exc:
        raise HTTPException(status_code=429, detail=str(exc)) from exc


@app.post("/chat")
async def chat(request: ChatRequest):
    user_query = request.query.strip()
    if not user_query:
        raise HTTPException(status_code=400, detail="query cannot be empty")
    if len(user_query) > 4000:
        raise HTTPException(status_code=400, detail="query too long (max 4000 chars)")

    if not USE_CLOUD and (not model or not tokenizer):
        raise HTTPException(status_code=500, detail="Local model not loaded and Cloud Mode is disabled.")

    print(f"📩 Received Query: {user_query}")

    # --- RAG: retrieve real repos matching the query ---
    context_block = ""
    retrieved_repos = []
    if rag_collection:
        retrieved_repos = retrieve(rag_collection, user_query, n_results=8)
        context_block = format_context(retrieved_repos)
        print(f"🔍 Retrieved {len(retrieved_repos)} repos from RAG index.")

    # --- Build grounded prompt ---
    if context_block:
        prompt = (
            f"### Instruction: {user_query}\n\n"
            f"Real GitHub repositories from database:\n{context_block}\n\n"
            f"Using only the repositories listed above, recommend the best match(es). "
            f"Include the GitHub URL, stars, and explain why it solves the requirement. "
            f"### Response:"
        )
    else:
        prompt = f"### Instruction: {user_query} ### Response:"

    try:
        if USE_CLOUD:
            print(f"🚀 Forwarding to Cloud Expert: {CLOUD_ENDPOINT}")
            headers = {"X-API-Key": EXPERT_API_KEY} if EXPERT_API_KEY else {}
            async with httpx.AsyncClient(timeout=60.0) as client:
                res = await client.post(CLOUD_ENDPOINT, json={"query": prompt}, headers=headers)
                if res.status_code != 200:
                    raise HTTPException(status_code=res.status_code, detail=f"Cloud API Error: {res.text}")
                
                cloud_data = res.json()
                # Cloud returns {"recommendation": "..."}
                clean_response = cloud_data.get("recommendation", cloud_data.get("response", "No response from cloud."))
        else:
            print("🤖 Generating response locally...")
            response = mlx_lm.generate(
                model=model,
                tokenizer=tokenizer,
                prompt=prompt,
                max_tokens=600,
                verbose=True,
            )
            clean_response = response.split("<|eot_id|>")[0].split("<|start_header_id|>")[0].strip()

        print("✅ Response generated successfully.")
        return {
            "response": clean_response,
            "repos": retrieved_repos,
        }
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"❌ INFERENCE ERROR:\n{error_detail}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/architecture/generate")
async def architecture_generate(request: ArchitectureRequest, client_request: Request):
    requirement = request.requirement.strip()
    product_name = request.product_name.strip()
    if not requirement:
        raise HTTPException(status_code=400, detail="requirement cannot be empty")
    if not product_name:
        raise HTTPException(status_code=400, detail="product_name cannot be empty")
    if len(requirement) > 8000:
        raise HTTPException(status_code=400, detail="requirement too long (max 8000 chars)")
    if len(product_name) > 200:
        raise HTTPException(status_code=400, detail="product_name too long (max 200 chars)")

    # Optional API key guard for public deployments
    if ARCHITECTURE_API_KEYS:
        incoming_key = client_request.headers.get("X-Architecture-Key", "")
        authorized = any(hmac.compare_digest(incoming_key, configured) for configured in ARCHITECTURE_API_KEYS)
        if not authorized:
            raise HTTPException(status_code=401, detail="Unauthorized: invalid architecture key")

    # Lightweight in-memory rate limiter
    client_host = "local"
    if client_request is not None and client_request.client:
        client_host = client_request.client.host or "unknown"
    _enforce_rate_limit(client_host, time.time())

    repos: list[dict] = []
    if rag_collection:
        repos = retrieve(rag_collection, requirement, n_results=8)

    mesh_output = await run_parallel_agents(
        requirement=requirement,
        repos=repos,
        stack_preferences=request.stack_preferences,
    )
    markdown = render_architecture_markdown(
        product_name=product_name,
        requirement=requirement,
        mesh_output=mesh_output,
        repos=repos,
    )

    file_written = False
    if request.write_file:
        try:
            output_path = validate_markdown_output_path(request.output_path)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(markdown)
            file_written = True
        except OSError as exc:
            raise HTTPException(status_code=500, detail=f"failed to write file: {exc}") from exc

    return {
        "architecture_markdown": markdown,
        "output_path": str(output_path) if request.write_file else None,
        "file_written": file_written,
        "repos_used": repos,
        "agent_outputs": mesh_output,
    }


@app.get("/status")
async def status():
    return {
        "status": "online" if (USE_CLOUD or model) else "offline",
        "model": MODEL_PATH,
        "rag_indexed": rag_collection.count() if rag_collection else 0,
        "ready": bool(model and rag_collection),
    }


@app.get("/health/live")
async def health_live():
    return {"status": "live", "environment": ENVIRONMENT}


@app.get("/health/ready")
async def health_ready():
    ready = bool(rag_collection) and (USE_CLOUD or bool(model and tokenizer))
    status_code = 200 if ready else 503
    payload = {
        "status": "ready" if ready else "not_ready",
        "environment": ENVIRONMENT,
        "rag_ready": bool(rag_collection),
        "inference_ready": bool(USE_CLOUD or bool(model and tokenizer)),
    }
    return JSONResponse(status_code=status_code, content=payload)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
