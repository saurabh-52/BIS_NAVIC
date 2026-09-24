"""
BIS Standards Scraper — Phase 5: Scrape Department
Fetches the list of all standards in AYUSH and scrapes each one into the database.
"""

import sys
import time
import json
import db
from scrape_department_list import find_ayush_department, fetch_ayush_standards_list
from scrape_single import scrape_single_standard

def main():
    print("Initializing Database...", file=sys.stderr)
    db.init_db()

    print("Finding AYUSH department...", file=sys.stderr)
    ayush_dept = find_ayush_department()
    if not ayush_dept:
        print("❌ Could not find AYUSH department!", file=sys.stderr)
        sys.exit(1)
        
    enc_dept_id = ayush_dept.get("encryptedDepartmentId")
    dept_name = ayush_dept.get("deptName")
    
    print(f"\nFetching standards list for {dept_name}...", file=sys.stderr)
    standards_list = fetch_ayush_standards_list(enc_dept_id)
    total_standards = len(standards_list)
    print(f"Total standards to scrape: {total_standards}\n", file=sys.stderr)
    
    success_count = 0
    fail_count = 0
    failed_standards = []

    for i, std in enumerate(standards_list, 1):
        is_num = std.get("standardNumber")
        enc_id = std.get("standardId")
        
        print(f"[{i}/{total_standards}] Scraping {is_num}...", file=sys.stderr)
        
        try:
            # Scrape the full JSON for the standard
            data = scrape_single_standard(enc_id)
            
            # Insert it into the DB
            internal_id = db.insert_standard(data)
            
            success_count += 1
            print(f"    ✅ Inserted as ID: {internal_id}", file=sys.stderr)
            
        except Exception as e:
            fail_count += 1
            failed_standards.append({"is_number": is_num, "error": str(e)})
            print(f"    ❌ Failed: {str(e)}", file=sys.stderr)
            
        # Optional: wait a moment before the next standard to be gentle on the server
        # (the internal API calls already have a 1s delay in bis_api.py, but we add a small extra buffer here)
        time.sleep(0.5)
        
    print("\n" + "="*50, file=sys.stderr)
    print(f"PHASE 5 RUN COMPLETE", file=sys.stderr)
    print(f"Total Attempted: {total_standards}", file=sys.stderr)
    print(f"Success: {success_count}", file=sys.stderr)
    print(f"Failed:  {fail_count}", file=sys.stderr)
    
    if fail_count > 0:
        print("\nFailed Standards:", file=sys.stderr)
        for fail in failed_standards:
            print(f" - {fail['is_number']}: {fail['error']}", file=sys.stderr)

    # Dump the results summary to stdout
    result = {
        "department": dept_name,
        "total": total_standards,
        "success": success_count,
        "failed": fail_count,
        "failed_list": failed_standards
    }
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
