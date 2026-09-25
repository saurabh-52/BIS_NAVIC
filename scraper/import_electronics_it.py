"""
BIS NAVIC — Ingest Electronics & Information Technology Department (LITD)
Fetches standards for ELECTRONICS AND INFORMATION TECHNOLOGY DEPARTMENT (~1,655 standards)
from the official BIS Standards Portal, stores raw JSONs into RawDocumentStore,
and rebuilds the local SQLite FTS5 search index.
"""

import sys
import os
import json
import time
import concurrent.futures
from typing import Dict, Any, List

# Ensure proper console encoding
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from connectors.standards_portal_connector import StandardsPortalConnector, REVIEW_SERVICE
from storage.raw_document_store import RawDocumentStore
from local_search import LocalStandardsSearch


def main():
    print("=" * 65)
    print("  BIS NAVIC: Ingesting Electronics & IT Department (LITD)")
    print("=" * 65)

    store = RawDocumentStore()
    connector = StandardsPortalConnector(store=store, request_delay=0.0)

    # ── Step 1: Discover LITD Department ──
    print("\n1. Discovering Electronics & IT Department...")
    depts = connector.get_departments()
    litd_dept = None
    for d in depts:
        name = d.get("deptName", "").upper()
        alias = d.get("deptAliasName", "").upper()
        if "ELECTRONICS" in name or alias == "LITD":
            litd_dept = d
            break

    if not litd_dept:
        print("❌ Could not find ELECTRONICS AND INFORMATION TECHNOLOGY DEPARTMENT!")
        sys.exit(1)

    dept_name = litd_dept.get("deptName")
    dept_alias = litd_dept.get("deptAliasName")
    enc_dept_id = litd_dept.get("encryptedDepartmentId")
    print(f"   Found: {dept_name} (Alias: {dept_alias})")

    # ── Step 2: Fetch Standards Catalog List with Pagination ──
    print("\n2. Fetching standards catalog list...")
    page_size = 100
    all_standards: List[Dict[str, Any]] = []
    page_num = 1

    t0_list = time.time()
    # Fetch first page to get total count
    first_page = connector.get_standards_list(enc_dept_id, page=1, limit=page_size, offset=0)
    total_records = first_page.get("totalRecord", 0)
    all_standards.extend(first_page.get("data", []))
    print(f"   Total standards reported in department: {total_records}")

    while len(all_standards) < total_records:
        offset = len(all_standards)
        fetch_limit = min(page_size, total_records - offset)
        page_num += 1
        page_data = connector.get_standards_list(enc_dept_id, page=page_num, limit=fetch_limit, offset=offset)
        items = page_data.get("data", [])
        if not items:
            break
        all_standards.extend(items)
        print(f"   Progress: {len(all_standards)}/{total_records} standards cataloged...")

    print(f"   Catalog fetch complete: {len(all_standards)} standards in {round(time.time() - t0_list, 1)}s")

    # Store catalog document
    safe_dept = "".join(c if c.isalnum() else "_" for c in dept_name)[:30]
    catalog_url = f"{REVIEW_SERVICE}/getWebsitePSTechDepartmentWise?dept={safe_dept}"
    store.store_document(
        source_domain=connector.SOURCE_DOMAIN,
        category=connector.CATEGORY,
        source_url=catalog_url,
        doc_name=f"dept_list_{safe_dept}.json",
        content=json.dumps({"data": all_standards, "totalRecord": len(all_standards)}, indent=2).encode("utf-8"),
        doc_type="json",
        metadata={"department": dept_name, "count": len(all_standards)}
    )

    # ── Step 3: Fetch Individual Standard Details Concurrently ──
    print(f"\n3. Fetching detailed specifications for {len(all_standards)} standards...")
    t0_details = time.time()

    # Determine which ones need fetching
    to_fetch = []
    for std in all_standards:
        std_num = std.get("standardNumber", "IS_UNKNOWN")
        std_enc_id = std.get("standardId")
        if not std_enc_id:
            continue
        safe_std = "".join(c if c.isalnum() else "_" for c in std_num)
        std_url = f"{REVIEW_SERVICE}/getWebsiteStandardDetails?stdId={safe_std}"
        if not store.has_document(std_url):
            to_fetch.append((std, std_num, safe_std, std_url, std_enc_id))

    print(f"   Already stored: {len(all_standards) - len(to_fetch)} | Needs fetching: {len(to_fetch)}")

    stored_count = 0
    error_count = 0

    def fetch_worker(item):
        std_dict, std_num, safe_std, std_url, std_enc_id = item
        try:
            details = connector.get_standard_details(std_enc_id)
            if not details:
                return None
            return (item, details)
        except Exception as e:
            return (item, None)

    # Fetch concurrently with thread pool
    batch_size = 100
    for i in range(0, len(to_fetch), batch_size):
        batch = to_fetch[i : i + batch_size]
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(fetch_worker, batch))

        for res in results:
            if not res or not res[1]:
                error_count += 1
                continue
            item, details = res
            std_dict, std_num, safe_std, std_url, std_enc_id = item
            try:
                store.store_document(
                    source_domain=connector.SOURCE_DOMAIN,
                    category=connector.CATEGORY,
                    source_url=std_url,
                    doc_name=f"standard_{safe_std}.json",
                    content=json.dumps(details, indent=2).encode("utf-8"),
                    doc_type="json",
                    metadata={
                        "is_number": std_num,
                        "department": dept_name,
                        "title": std_dict.get("standardName") or details.get("standardName"),
                        "encrypted_id": std_enc_id
                    }
                )
                stored_count += 1
            except Exception as e:
                error_count += 1

        done = min(i + batch_size, len(to_fetch))
        elapsed = round(time.time() - t0_details, 1)
        rate = round(done / max(elapsed, 0.1), 1)
        print(f"   Stored {done}/{len(to_fetch)} standards ({stored_count} new, {error_count} errors) — {rate} std/s")

    total_detail_time = round(time.time() - t0_details, 1)
    print(f"\n   Standard details ingestion finished in {total_detail_time}s:")
    print(f"   - Newly stored: {stored_count}")
    print(f"   - Errors: {error_count}")

    # ── Step 4: Rebuild Local Search Index (SQLite FTS5) ──
    print("\n4. Rebuilding local search index (SQLite FTS5)...")
    search_engine = LocalStandardsSearch()
    build_stats = search_engine.build_index()
    print(f"   Indexed: {build_stats.get('indexed')} standards")
    print(f"   Departments in DB: {build_stats.get('departments')}")

    # ── Step 5: Database Statistics ──
    print("\n5. Current Database Statistics:")
    stats = search_engine.get_stats()
    print(json.dumps(stats, indent=2))

    print("\n" + "=" * 65)
    print("  ✅ Electronics & Information Technology Department ingested successfully!")
    print("=" * 65)


if __name__ == "__main__":
    main()
