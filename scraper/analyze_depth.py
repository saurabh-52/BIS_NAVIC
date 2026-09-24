import json

def analyze_chunk_depth():
    with open('ayush_chunks.json') as f:
        chunks = json.load(f)
        
    # Group chunks by IS Number
    standards = {}
    for c in chunks:
        is_num = c['is_number']
        if is_num not in standards:
            standards[is_num] = []
        standards[is_num].append(c)
        
    total_standards = len(standards)
    metadata_only_count = 0
    body_text_count = 0
    
    metadata_only_examples = []
    
    for is_num, std_chunks in standards.items():
        # Check if it has any chunk that is NOT "Metadata Summary"
        has_body = False
        for c in std_chunks:
            # Usually we assigned "Metadata Summary" if no clause was found, or if it was just the DB title/abstract
            if c['clause'] != 'Metadata Summary':
                has_body = True
                break
                
        if has_body:
            body_text_count += 1
        else:
            metadata_only_count += 1
            if len(metadata_only_examples) < 5:
                metadata_only_examples.append(is_num)
                
    print(f"Total Standards in JSON: {total_standards}")
    print(f"Standards with Body Text Chunks: {body_text_count} ({(body_text_count/total_standards)*100:.1f}%)")
    print(f"Standards with ONLY Metadata Chunks: {metadata_only_count} ({(metadata_only_count/total_standards)*100:.1f}%)")
    
    if metadata_only_count > 0:
        print(f"\nExamples of Metadata-Only Standards: {metadata_only_examples}")

if __name__ == "__main__":
    analyze_chunk_depth()
