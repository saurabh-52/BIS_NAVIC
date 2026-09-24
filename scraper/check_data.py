"""Quick script to check what data is stored in raw_documents.db"""
import sqlite3
import json

conn = sqlite3.connect('raw_documents.db')
conn.row_factory = sqlite3.Row

# Check AYUSH-related data
print("="*80)
print("AYUSH / Health / Department-related documents in standards_portal")
print("="*80)

rows = conn.execute("""
    SELECT doc_name, metadata_json, file_size
    FROM raw_documents 
    WHERE category='standards_portal'
    AND (
        LOWER(metadata_json) LIKE '%ayush%' 
        OR LOWER(metadata_json) LIKE '%health%'
        OR LOWER(doc_name) LIKE '%ayush%'
        OR LOWER(doc_name) LIKE '%health%'
    )
    ORDER BY created_at DESC
""").fetchall()

print(f"\nFound {len(rows)} AYUSH/Health related documents")
for r in rows:
    meta = json.loads(r['metadata_json']) if r['metadata_json'] else {}
    dept = meta.get('department', '')
    title = meta.get('title', '')
    print(f"  - {r['doc_name'][:50]:50s} | {dept[:30]:30s} | {r['file_size']:6d} bytes")
    if title:
        print(f"    Title: {title[:80]}")

# Show all departments
print("\n" + "="*80)
print("All departments with standard details stored:")
print("="*80)

rows = conn.execute("""
    SELECT json_extract(metadata_json, '$.department') as dept, COUNT(*) as cnt
    FROM raw_documents
    WHERE category='standards_portal' 
    AND json_extract(metadata_json, '$.department') IS NOT NULL
    GROUP BY dept
    ORDER BY cnt DESC
""").fetchall()

for r in rows:
    print(f"  {r['dept']:60s} | {r['cnt']:4d} standards")

# Check bis_standards.db too
print("\n" + "="*80)
print("Checking bis_standards.db (structured DB)...")
print("="*80)

import os
bis_db = 'bis_standards.db'
if os.path.exists(bis_db):
    conn2 = sqlite3.connect(bis_db)
    conn2.row_factory = sqlite3.Row
    
    try:
        total = conn2.execute("SELECT COUNT(*) FROM standards").fetchone()[0]
        print(f"Total standards in structured DB: {total}")
        
        rows = conn2.execute("""
            SELECT department_name, COUNT(*) as cnt 
            FROM standards 
            WHERE department_name IS NOT NULL
            GROUP BY department_name
            ORDER BY cnt DESC
        """).fetchall()
        for r in rows:
            print(f"  {r['department_name']:60s} | {r['cnt']:4d} standards")
            
        # AYUSH specific
        ayush = conn2.execute("""
            SELECT COUNT(*) FROM standards 
            WHERE LOWER(department_name) LIKE '%ayush%'
        """).fetchone()[0]
        print(f"\nAYUSH department standards in structured DB: {ayush}")
        
        if ayush > 0:
            rows = conn2.execute("""
                SELECT is_number, title, department_name
                FROM standards
                WHERE LOWER(department_name) LIKE '%ayush%'
                LIMIT 10
            """).fetchall()
            for r in rows:
                print(f"  IS {r['is_number']}: {r['title'][:70]}")
    except Exception as e:
        print(f"Error querying bis_standards.db: {e}")
    conn2.close()
else:
    print(f"  bis_standards.db does not exist at: {os.path.abspath(bis_db)}")

conn.close()
