import sqlite3
import json

def generate_chunks():
    conn = sqlite3.connect('bis_standards.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    standards = cursor.execute("SELECT * FROM standards").fetchall()
    
    chunks = []
    
    for std in standards:
        # We don't have full text, so we generate a comprehensive metadata chunk
        text_content = f"Standard {std['is_number']}: {std['title']}. "
        
        if std['type_of_standard']:
            text_content += f"Type: {std['type_of_standard']}. "
        
        if std['department_name'] and std['technical_committee_name']:
            text_content += f"Developed by the {std['technical_committee_name']} under the {std['department_name']}. "
        
        if std['published_on']:
            text_content += f"Published on {std['published_on']} with status {std['life_cycle_status']}. "
            
        # Get cross references
        refs = cursor.execute("SELECT referred_standard_number, referred_standard_name FROM standards_referred WHERE standard_id = ?", (std['id'],)).fetchall()
        if refs:
            ref_texts = [f"{r['referred_standard_number']} ({r['referred_standard_name']})" for r in refs]
            text_content += f"It references the following standards: {'; '.join(ref_texts)}. "
            
        group_name = std['group_name'] or "Uncategorized"
            
        chunk = {
            "is_number": std['is_number'],
            "clause": "Metadata Summary",
            "text": text_content,
            "group": group_name,
            "sub_group": std['sub_group_name'] or "",
            "sub_sub_group": std['sub_sub_group_name'] or "",
            "ics_code": std['ics_code'] or ""
        }
        chunks.append(chunk)
        
    with open('ayush_chunks.json', 'w') as f:
        json.dump(chunks, f, indent=2)
        
    print(f"Generated {len(chunks)} chunks.")

if __name__ == "__main__":
    generate_chunks()
