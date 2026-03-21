import chromadb
from chromadb.utils import embedding_functions
import json
import os

CHROMA_PATH = "github_repohunter/database/chroma"
COLLECTION_NAME = "repos"
EMBED_MODEL = "all-MiniLM-L6-v2"

JSONL_SOURCES = [
    "github_repohunter/database/validated/global_ocean.jsonl",
    "github_repohunter/database/validated/global_master_dataset.jsonl",
]

JSON_SOURCES = [
    "github_repohunter/database/validated/master_dataset.json",
    "github_repohunter/database/validated/gems_MLX_AI_safe.json",
]


def get_collection():
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL)
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )
    return collection


def build_index():
    collection = get_collection()

    if collection.count() > 0:
        print(f"✅ RAG index already built: {collection.count()} repos loaded from disk.")
        return collection

    print("🔍 Building RAG index — this runs once and is saved to disk...")

    all_repos = []

    for path in JSONL_SOURCES:
        if not os.path.exists(path):
            continue
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    all_repos.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    for path in JSON_SOURCES:
        if not os.path.exists(path):
            continue
        with open(path, "r") as f:
            try:
                data = json.load(f)
                if isinstance(data, list):
                    all_repos.extend(data)
            except json.JSONDecodeError:
                continue

    seen_urls = set()
    unique_repos = []
    for repo in all_repos:
        url = repo.get("url", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_repos.append(repo)

    print(f"📊 Unique repos to index: {len(unique_repos)}")

    BATCH_SIZE = 500
    for i in range(0, len(unique_repos), BATCH_SIZE):
        batch = unique_repos[i : i + BATCH_SIZE]
        ids, documents, metadatas = [], [], []

        for j, repo in enumerate(batch):
            name = repo.get("name", "") or ""
            description = (repo.get("description", "") or "").strip()
            readme = (repo.get("readme_snippet", "") or "")[:300]
            language = repo.get("language", "") or ""
            url = repo.get("url", "") or ""
            stars = repo.get("stars", 0)
            license_val = repo.get("license", "") or ""

            doc_text = f"{name} {description} {language} {readme}".strip()
            if not doc_text:
                continue

            ids.append(f"repo_{i + j}")
            documents.append(doc_text)
            metadatas.append({
                "name": name,
                "url": url,
                "description": description[:500],
                "stars": int(stars) if isinstance(stars, (int, float)) else 0,
                "language": language,
                "license": license_val,
            })

        if ids:
            collection.add(ids=ids, documents=documents, metadatas=metadatas)
            print(f"  ✓ Indexed {min(i + BATCH_SIZE, len(unique_repos))}/{len(unique_repos)}")

    print(f"✅ RAG index built: {collection.count()} repos ready.")
    return collection


def retrieve(collection, query: str, n_results: int = 8) -> list[dict]:
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        include=["metadatas", "distances"],
    )
    repos = []
    for meta, dist in zip(results["metadatas"][0], results["distances"][0]):
        repos.append({**meta, "relevance_score": round(1 - dist, 3)})
    return repos


def format_context(repos: list[dict]) -> str:
    lines = []
    for i, r in enumerate(repos, 1):
        name = r.get("name", "unknown")
        url = r.get("url", "")
        description = r.get("description", "No description")
        stars = r.get("stars", 0)
        language = r.get("language", "")
        score = r.get("relevance_score", 0)
        lines.append(
            f"{i}. {name} ({stars}⭐, {language}) — {description}\n"
            f"   URL: {url}  [relevance: {score}]"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    col = build_index()
    print(f"\nTotal indexed: {col.count()}")

    test_query = "FastAPI authentication boilerplate JWT"
    results = retrieve(col, test_query)
    print(f"\nTest query: '{test_query}'")
    for r in results[:5]:
        print(f"  [{r['relevance_score']}] {r['name']} ({r['stars']}⭐) — {r['description'][:70]}")
        print(f"    {r['url']}")
