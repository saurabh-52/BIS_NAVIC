"""
BIS NAVIC — Ingestion Orchestrator CLI
Implements the Source Connector & Raw Document Store ingestion system matching
the system architecture:
  - Standards Portal (standards.bis.gov.in)
  - BIS Main Website (bis.gov.in: QCO, Manuals, Hallmarking)
  - BIS LIMS (lims.bis.gov.in)
  - Raw Document Store (Filesystem / SQLite / S3 metadata & blob storage)
"""

import sys
import argparse
import json

# Ensure Windows terminal doesn't crash on unicode/emojis
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from storage.raw_document_store import RawDocumentStore
from connectors.standards_portal_connector import StandardsPortalConnector
from connectors.bis_main_connector import BisMainConnector
from connectors.lims_connector import LimsConnector


def print_stats(store: RawDocumentStore):
    stats = store.get_stats()
    print("\n" + "=" * 60)
    print(" 📦 RAW DOCUMENT STORE STATUS")
    print("=" * 60)
    print(f" Total Documents Stored : {stats['total_documents']}")
    print(f" Total Storage Size     : {stats['total_storage_mb']} MB ({stats['total_storage_bytes']} bytes)")
    print(f" Database Catalog Path  : {stats['db_path']}")
    print(f" Storage Directory      : {stats['storage_directory']}")
    
    print("\n Breakdown by Category:")
    for cat, info in stats["by_category"].items():
        mb = round(info["total_bytes"] / (1024 * 1024), 3)
        print(f"   • {cat:<18}: {info['count']:>4} files ({mb:>6.3f} MB)")
        
    print("\n Breakdown by Source Domain:")
    for domain, count in stats["by_source"].items():
        print(f"   • {domain:<22}: {count:>4} documents")
    print("=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(description="BIS NAVIC Source Connector & Ingestion Engine")
    parser.add_argument("--status", action="store_true", help="Print current status of Raw Document Store")
    parser.add_argument(
        "--source",
        choices=["all", "standards", "main", "qco", "manuals", "hallmarking", "lims"],
        default="all",
        help="Which official source to ingest from"
    )
    parser.add_argument("--dept", type=str, default=None, help="Filter department by name (e.g. AYUSH, Chemical, Food)")
    parser.add_argument("--limit", type=int, default=5, help="Limit number of items to fetch per source/category")
    parser.add_argument("--max-depts", type=int, default=2, help="Max departments to query from Standards Portal")
    args = parser.parse_args()

    store = RawDocumentStore()

    if args.status:
        print_stats(store)
        return

    print("=" * 60)
    print(f"🚀 INGESTION STARTING — Source: {args.source.upper()} (Limit: {args.limit})")
    print("=" * 60)

    # 1. Standards Portal
    if args.source in ("all", "standards"):
        print("\n[1/3] Connecting to Standards Portal (standards.bis.gov.in)...")
        sp_connector = StandardsPortalConnector(store=store)
        res_sp = sp_connector.fetch_and_store(
            department_filter=args.dept,
            limit_per_dept=args.limit,
            max_depts=args.max_depts
        )
        print(f"  ✅ Standards Portal: {json.dumps(res_sp)}")

    # 2. BIS Main Website
    if args.source in ("all", "main", "qco", "manuals", "hallmarking"):
        print("\n[2/3] Connecting to BIS Main Website (bis.gov.in)...")
        main_connector = BisMainConnector(store=store)
        if args.source == "qco":
            res_main = main_connector.fetch_qcos(download_sample_pdfs=args.limit)
        elif args.source == "manuals":
            res_main = main_connector.fetch_product_manuals(download_sample_pdfs=args.limit)
        elif args.source == "hallmarking":
            res_main = main_connector.fetch_hallmarking()
        else:
            res_main = main_connector.fetch_and_store(limit=args.limit)
        print(f"  ✅ BIS Main Website: {json.dumps(res_main, indent=2)}")

    # 3. BIS LIMS
    if args.source in ("all", "lims"):
        print("\n[3/3] Connecting to BIS LIMS (lims.bis.gov.in)...")
        lims_connector = LimsConnector(store=store)
        res_lims = lims_connector.fetch_and_store()
        print(f"  ✅ BIS LIMS: {json.dumps(res_lims)}")

    # Final summary
    print_stats(store)


if __name__ == "__main__":
    main()
