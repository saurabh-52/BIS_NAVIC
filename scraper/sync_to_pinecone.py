"""
BIS NAVIC — Sync Standards to Pinecone Cloud (Resumable & Fast)
Uploads all cataloged standards from local SQLite / Raw Store to Pinecone Cloud.
Stores full metadata and gzipped raw JSON inside vector metadata.
Automatically detects existing vectors in Pinecone and resumes without duplicates.
"""

import os
import sys
import json
import time
import gzip
import base64
import sqlite3
import hashlib
from typing import List, Dict, Any, Set

from dotenv import load_dotenv
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer

# Ensure Windows terminal handles emojis/unicode
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOCAL_DB_PATH = os.path.join(BASE_DIR, "local_search.db")
INDEX_NAME = "bis-standards-test"
NAMESPACE = "standards"
BATCH_SIZE = 32
MAX_RETRIES = 5

load_dotenv(os.path.join(BASE_DIR, ".env"))


def make_vector_id(std_num: str) -> str:
    """Create a URL-safe, deterministic Pinecone vector ID."""
    clean = std_num.replace(" ", "_").replace("/", "_").replace(":", "_").replace("(", "").replace(")", "")
    prefix = hashlib.md5(std_num.encode("utf-8")).hexdigest()[:8]
    return f"std_{prefix}_{clean[:40]}"


def upsert_with_retry(index, vectors, namespace, max_retries=MAX_RETRIES):
    """Upserts a batch of vectors with exponential backoff on network timeout."""
    for attempt in range(1, max_retries + 1):
        try:
            index.upsert(vectors=vectors, namespace=namespace)
            return True
        except Exception as e:
            if attempt == max_retries:
                print(f"   ❌ Final upsert failure on attempt {attempt}: {e}", flush=True)
                raise e
            wait = attempt * 2
            print(f"   ⚠️ Network warning ({e}). Retrying in {wait}s...", flush=True)
            time.sleep(wait)
    return False


def get_existing_vector_ids(index, namespace) -> Set[str]:
    """Fetch all already uploaded vector IDs from Pinecone to enable fast resumption."""
    existing_ids = set()
    try:
        for page in index.list(namespace=namespace):
            for item in page:
                existing_ids.add(item.id)
    except Exception as e:
        print(f"   Notice: Could not list existing vectors ({e}), starting fresh.", flush=True)
    return existing_ids


def upload_all_standards():
    print("=" * 65, flush=True)
    print("  🚀 BIS NAVIC: Syncing All Standards to Pinecone Cloud", flush=True)
    print("=" * 65, flush=True)

    pinecone_key = os.environ.get("PINECONE_API_KEY")
    if not pinecone_key:
        print("❌ Error: PINECONE_API_KEY not found in scraper/.env", flush=True)
        sys.exit(1)

    if not os.path.exists(LOCAL_DB_PATH):
        print(f"❌ Error: {LOCAL_DB_PATH} not found. Run local_search.py first.", flush=True)
        sys.exit(1)

    # 1. Read all standards from local SQLite
    print("\n1. Reading standards from local SQLite database...", flush=True)
    conn = sqlite3.connect(LOCAL_DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("""
        SELECT 
            standard_number, standard_name, department_name, committee_name,
            group_name, sub_group_name, sub_sub_group_name, ministry_name,
            published_on, type_of_standard, language, pdf_path, source_file, raw_json
        FROM standards_data
        ORDER BY id ASC
    """).fetchall()
    conn.close()

    total_records = len(rows)
    print(f"   Found {total_records} standards cataloged locally.", flush=True)

    if total_records == 0:
        print("❌ No standards found in standards_data table.", flush=True)
        return

    # 2. Connect to Pinecone and check existing vectors
    print(f"\n2. Connecting to Pinecone index: '{INDEX_NAME}' (namespace: '{NAMESPACE}')...", flush=True)
    pc = Pinecone(api_key=pinecone_key)
    index = pc.Index(INDEX_NAME)

    existing_ids = get_existing_vector_ids(index, NAMESPACE)
    print(f"   Already in Pinecone: {len(existing_ids)} standards.", flush=True)

    # Filter out rows already in Pinecone
    pending_rows = [r for r in rows if make_vector_id(r["standard_number"]) not in existing_ids]
    print(f"   Remaining to upload: {len(pending_rows)} standards.", flush=True)

    if not pending_rows:
        print(f"\n✅ All {total_records} standards are already fully synced to Pinecone!", flush=True)
        return

    # 3. Load Embedding Model
    print("\n3. Loading embedding model 'intfloat/e5-large-v2'...", flush=True)
    t0_model = time.time()
    model = SentenceTransformer("intfloat/e5-large-v2")
    print(f"   Model ready in {round(time.time() - t0_model, 2)}s.", flush=True)

    # 4. Prepare passages and metadata
    print("\n4. Encoding and Upserting to Pinecone...", flush=True)
    t0_sync = time.time()
    uploaded_now = 0
    total_in_cloud = len(existing_ids)

    for i in range(0, len(pending_rows), BATCH_SIZE):
        chunk_rows = pending_rows[i : i + BATCH_SIZE]
        
        # Prepare text representation for e5 embedding
        passages = []
        for r in chunk_rows:
            std_num = r["standard_number"] or ""
            std_name = r["standard_name"] or ""
            dept = r["department_name"] or ""
            comm = r["committee_name"] or ""
            grp = r["group_name"] or ""
            minis = r["ministry_name"] or ""
            text = f"passage: {std_num} - {std_name}. Department: {dept}. Committee: {comm}. Group: {grp}. Ministry: {minis}."
            passages.append(text)

        # Generate dense embeddings (fast 1-second batch)
        embeddings = model.encode(passages, batch_size=BATCH_SIZE, show_progress_bar=False).tolist()

        # Format Pinecone vector objects
        batch_records = []
        for r, emb in zip(chunk_rows, embeddings):
            std_num = r["standard_number"]
            vid = make_vector_id(std_num)

            raw_j = r["raw_json"] or "{}"
            compressed_json = base64.b64encode(gzip.compress(raw_j.encode("utf-8"))).decode("ascii")

            meta = {
                "standard_number": std_num,
                "standard_name": (r["standard_name"] or "")[:500],
                "department_name": (r["department_name"] or "")[:200],
                "committee_name": (r["committee_name"] or "")[:200],
                "group_name": (r["group_name"] or "")[:200],
                "sub_group_name": (r["sub_group_name"] or "")[:200],
                "sub_sub_group_name": (r["sub_sub_group_name"] or "")[:200],
                "ministry_name": (r["ministry_name"] or "")[:200],
                "published_on": (r["published_on"] or "")[:50],
                "type_of_standard": (r["type_of_standard"] or "")[:100],
                "language": (r["language"] or "")[:50],
                "pdf_path": (r["pdf_path"] or "")[:300],
                "source_file": (r["source_file"] or "")[:200],
                "raw_json_gz": compressed_json
            }

            batch_records.append({
                "id": vid,
                "values": emb,
                "metadata": meta
            })

        # Upsert the batch
        upsert_with_retry(index, batch_records, namespace=NAMESPACE)
        uploaded_now += len(batch_records)
        total_in_cloud += len(batch_records)
        pct = round(total_in_cloud / total_records * 100, 1)
        print(f"   [Progress: {total_in_cloud}/{total_records}] ({pct}%)", flush=True)

    elapsed = round(time.time() - t0_sync, 1)
    print("\n" + "=" * 65, flush=True)
    print(f"  ✅ SUCCESS: {total_in_cloud} standards are now synced to Pinecone!", flush=True)
    print(f"  Namespace: '{NAMESPACE}' in index '{INDEX_NAME}'", flush=True)
    print(f"  Uploaded in this run: {uploaded_now} standards ({elapsed}s)", flush=True)
    print("=" * 65, flush=True)


if __name__ == "__main__":
    upload_all_standards()
