"""
BIS NAVIC — Restore & Sync from Pinecone Cloud to Local SQLite
Pulls all cataloged standards and their metadata directly from Pinecone Cloud,
restores the raw JSON documents, and automatically builds/populates:
  1. scraper/raw_store/standards_portal/ (raw JSON documents)
  2. scraper/local_search.db (SQLite FTS5 full-text search table for ultra-fast local retrieval)
  3. scraper/raw_documents.db (document catalog & SHA256 integrity store)

Run this on any new laptop/machine to get the entire database in seconds without scraping!
"""

import os
import sys
import json
import time
import gzip
import base64
from typing import List, Dict, Any

from dotenv import load_dotenv
from pinecone import Pinecone

# Ensure Windows terminal handles emojis/unicode
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_STORE_DIR = os.path.join(BASE_DIR, "raw_store", "standards_portal")
INDEX_NAME = "bis-standards-test"
NAMESPACE = "standards"
FETCH_BATCH_SIZE = 100

load_dotenv(os.path.join(BASE_DIR, ".env"))

# Import local search & raw store builders
from local_search import LocalStandardsSearch
from storage.raw_document_store import RawDocumentStore


def fetch_all_from_pinecone():
    print("=" * 65, flush=True)
    print("  📥 BIS NAVIC: Syncing from Pinecone Cloud to Local SQLite", flush=True)
    print("=" * 65, flush=True)

    pinecone_key = os.environ.get("PINECONE_API_KEY")
    if not pinecone_key:
        print("❌ Error: PINECONE_API_KEY not found in scraper/.env", flush=True)
        print("   Please create scraper/.env with your PINECONE_API_KEY first.", flush=True)
        sys.exit(1)

    os.makedirs(RAW_STORE_DIR, exist_ok=True)
    raw_store = RawDocumentStore()

    # 1. Connect to Pinecone
    print(f"\n1. Connecting to Pinecone index: '{INDEX_NAME}' (namespace: '{NAMESPACE}')...", flush=True)
    pc = Pinecone(api_key=pinecone_key)
    index = pc.Index(INDEX_NAME)

    # 2. Discover all vector IDs in the namespace
    print("2. Listing all standards stored in Pinecone...", flush=True)
    t0 = time.time()
    vector_ids = []
    
    for page in index.list(namespace=NAMESPACE):
        for item in page:
            vector_ids.append(item.id)

    total_vectors = len(vector_ids)
    print(f"   Discovered {total_vectors} standards in cloud index ({round(time.time() - t0, 2)}s).", flush=True)

    if total_vectors == 0:
        print("⚠️ Warning: No standards found in namespace 'standards'.", flush=True)
        print("   Did you run 'python scraper/sync_to_pinecone.py' on the source laptop first?", flush=True)
        sys.exit(1)

    # 3. Fetch metadata in batches and restore local documents
    print("\n3. Fetching standards and writing local files...", flush=True)
    t0_fetch = time.time()
    saved_count = 0

    for i in range(0, total_vectors, FETCH_BATCH_SIZE):
        batch_ids = vector_ids[i : i + FETCH_BATCH_SIZE]
        fetch_res = index.fetch(ids=batch_ids, namespace=NAMESPACE)
        vectors_dict = fetch_res.vectors

        for vid, vdata in vectors_dict.items():
            meta = vdata.metadata or {}
            std_num = meta.get("standard_number")
            raw_json_str = None

            # 1. Check for compressed raw_json_gz
            if meta.get("raw_json_gz"):
                try:
                    compressed_bytes = base64.b64decode(meta["raw_json_gz"].encode("ascii"))
                    raw_json_str = gzip.decompress(compressed_bytes).decode("utf-8")
                except Exception:
                    pass

            # 2. Fallback to uncompressed raw_json
            if not raw_json_str and meta.get("raw_json"):
                raw_json_str = meta["raw_json"]

            # 3. Fallback to reconstructing from metadata
            if not raw_json_str:
                raw_json_str = json.dumps({
                    "standardNumber": std_num,
                    "standardName": meta.get("standard_name"),
                    "departmentName": meta.get("department_name"),
                    "committeeName": meta.get("committee_name"),
                    "groupName": meta.get("group_name"),
                    "subGroupName": meta.get("sub_group_name"),
                    "subSubGroupName": meta.get("sub_sub_group_name"),
                    "ministryName": meta.get("ministry_name"),
                    "publishedOn": meta.get("published_on"),
                    "typeOfStandard": meta.get("type_of_standard"),
                    "language": meta.get("language"),
                }, indent=2)

            source_file = meta.get("source_file")
            if not source_file:
                clean_std = std_num.replace(" ", "_").replace("/", "_").replace(":", "_")
                source_file = f"standard_{clean_std}.json"

            file_path = os.path.join(RAW_STORE_DIR, source_file)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(raw_json_str)

            # Register in raw_documents.db
            try:
                raw_bytes = raw_json_str.encode("utf-8")
                raw_store.store_document(
                    source_domain="standards.bis.gov.in",
                    category="standards_portal",
                    source_url=f"https://standardsadmin.bis.gov.in/standards/{std_num}",
                    doc_name=source_file,
                    doc_type="json",
                    content=raw_bytes,
                    metadata={
                        "standard_number": std_num,
                        "title": meta.get("standard_name"),
                        "department": meta.get("department_name"),
                        "committee": meta.get("committee_name"),
                        "group": meta.get("group_name"),
                    }
                )
            except Exception:
                pass

            saved_count += 1

        pct = round(saved_count / total_vectors * 100, 1)
        print(f"   [Restored {saved_count}/{total_vectors}] ({pct}%)", flush=True)

    fetch_time = round(time.time() - t0_fetch, 1)
    print(f"   Finished restoring files in {fetch_time}s.", flush=True)

    # 4. Rebuild Local FTS5 SQLite Search Index
    print("\n4. Rebuilding SQLite FTS5 Search Index (local_search.db)...", flush=True)
    search_engine = LocalStandardsSearch()
    build_stats = search_engine.build_index()

    indexed_count = build_stats.get("indexed", 0)
    depts = build_stats.get("departments", [])

    print("\n" + "=" * 65, flush=True)
    print(f"  🎉 SYNC COMPLETE!", flush=True)
    print(f"  Total Standards Restored : {saved_count}", flush=True)
    print(f"  Indexed in SQLite FTS5   : {indexed_count}", flush=True)
    print(f"  Departments Indexed      : {len(depts)}", flush=True)
    print(f"  Local SQLite Database    : {search_engine.db_path}", flush=True)
    print("=" * 65, flush=True)
    print("\nYour local search backend (python scraper/local_backend.py) is ready to run with maximum speed!", flush=True)


if __name__ == "__main__":
    fetch_all_from_pinecone()
