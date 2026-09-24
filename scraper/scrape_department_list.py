"""
BIS Standards Scraper — Phase 4: Fetch Department Standards List
"""

import sys
import json
from bis_api import get_departments, get_standards_list


def find_ayush_department():
    """Fetch all departments and find the one for AYUSH."""
    departments = get_departments()
    for dept in departments:
        # e.g., "AYUSH DEPARTMENT (AYD)" or similar
        if "AYUSH" in dept.get("deptName", "").upper():
            return dept
    return None


def fetch_ayush_standards_list(enc_dept_id: str):
    """
    Fetch the complete list of standards for a department.
    Uses pagination to get all of them.
    """
    print(f"Fetching page 1 to get total count...", file=sys.stderr)
    # page=1, limit=12
    first_page = get_standards_list(enc_dept_id, page=1, limit=12)
    
    pagination = first_page.get("pagination", {})
    total_records = pagination.get("totalRecord", 0)
    total_pages = pagination.get("totalPages", 1)
    
    print(f"Found {total_records} standards across {total_pages} pages.", file=sys.stderr)
    
    all_standards = []
    all_standards.extend(first_page.get("standards", []))
    
    for page_num in range(2, total_pages + 1):
        print(f"Fetching page {page_num}/{total_pages}...", file=sys.stderr)
        page_data = get_standards_list(enc_dept_id, page=page_num, limit=12)
        all_standards.extend(page_data.get("standards", []))
        
    return all_standards


def main():
    print("Finding AYUSH department...", file=sys.stderr)
    ayush_dept = find_ayush_department()
    
    if not ayush_dept:
        print("❌ Could not find AYUSH department!", file=sys.stderr)
        sys.exit(1)
        
    enc_dept_id = ayush_dept.get("encryptedDepartmentId")
    dept_name = ayush_dept.get("deptName")
    print(f"Found: {dept_name} (encId: {enc_dept_id[:30]}...)", file=sys.stderr)
    
    print(f"\nFetching standards list for {dept_name}...", file=sys.stderr)
    standards_list = fetch_ayush_standards_list(enc_dept_id)
    
    # Print the result list (metadata only, not full details)
    result = {
        "department_name": dept_name,
        "total_fetched": len(standards_list),
        "standards": standards_list
    }
    
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
