import firebase_admin
from firebase_admin import credentials, firestore
import json
import os

def init_firebase():
    """Initializes Firebase safely targeting ai-task-mvp-7729."""
    try:
        project_id = os.getenv("FIREBASE_PROJECT_ID", "ai-task-mvp-7729")
        if not firebase_admin._apps:
            firebase_admin.initialize_app(options={'projectId': project_id})
        db = firestore.client()
        print(f"✅ Firebase Initialized for {project_id}.")
        return db
    except Exception as e:
        print(f"❌ Firebase Init Failed: {e}")
        raise

def migrate_local_to_cloud(db):
    """Migrates repositories from local JSON to Firestore Ocean."""
    local_path = "github_repohunter/scraped_repos.json"
    if not os.path.exists(local_path):
        print("❌ No local scraped_repos.json found.")
        return

    with open(local_path, "r") as f:
        repos = json.load(f)

    print(f"🚢 Migrating {len(repos)} repositories to Firestore...")
    batch = db.batch()
    collection = db.collection("repositories")

    for i, (repo_name, data) in enumerate(repos.items()):
        doc_id = repo_name.replace("/", "__") # Firestore IDs can't have slashes
        doc_ref = collection.document(doc_id)
        batch.set(doc_ref, {
            "name": repo_name,
            "description": data.get("description", ""),
            "stars": data.get("stars", 0),
            "url": data.get("url", f"https://github.com/{repo_name}"),
            "ingested_at": firestore.SERVER_TIMESTAMP
        })

        # Firestore batches have a 500 document limit
        if (i + 1) % 400 == 0:
            batch.commit()
            batch = db.batch()
            print(f"✅ Migrated {i + 1} repos...")

    batch.commit()
    print("✨ Migration Complete.")

if __name__ == "__main__":
    database = init_firebase()
    migrate_local_to_cloud(database)
