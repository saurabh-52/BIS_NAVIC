"""
BIS NAVIC — Ingest Environment & Ecology Department (EED)
Fetches all standards for the Environment & Ecology Department (~114 standards)
and saves them to the Raw Document Store, then rebuilds the local search index.
"""

import sys
import os
import json
import time

# Ensure proper encoding
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from connectors.standards_portal_connector import StandardsPortalConnector
from storage.raw_document_store import RawDocumentStore
from local_search import LocalStandardsSearch

def main():
    print("="*60)
    print("  BIS NAVIC: Ingesting Environment & Ecology Department (EED)")
    print("="*60)

    store = RawDocumentStore()
    connector = StandardsPortalConnector(store=store, request_delay=0.3)

    print("\n1. Fetching technical departments...")
    depts = connector.get_departments()
    eed_dept = None
    for d in depts:
        if "ENVIRONMENT" in d.get("deptName", "").upper():
            eed_dept = d
            break

    if not eed_dept:
        print("❌ Environment & Ecology Department not found!")
        return

    print(f"   Found: {eed_dept.get('deptName')} (Alias: {eed_dept.get('deptAliasName')})")
    enc_dept_id = eed_dept.get("encryptedDepartmentId")

    print("\n2. Ingesting standards catalog...")
    t0 = time.time()
    result = connector.fetch_and_store(department_filter="ENVIRONMENT", limit_per_dept=300)
    elapsed = round(time.time() - t0, 1)

    print(f"\n   Ingestion complete in {elapsed}s:")
    print(f"   - Departments processed: {result.get('departments_processed')}")
    print(f"   - Standards in catalog: {result.get('department_lists_stored')}")
    print(f"   - Detail files stored: {result.get('standard_details_stored')}")

    print("\n3. Rebuilding local search index (SQLite FTS5)...")
    search_engine = LocalStandardsSearch()
    build_stats = search_engine.build_index()
    print(f"   Indexed: {build_stats.get('indexed')} standards")
    print(f"   Departments: {build_stats.get('departments')}")

    print("\n4. Current Database Statistics:")
    stats = search_engine.get_stats()
    print(json.dumps(stats, indent=2))

    print("\n" + "="*60)
    print("  ✅ Environment & Ecology Department added successfully!")
    print("="*60)

if __name__ == "__main__":
    main()
