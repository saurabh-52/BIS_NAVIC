import json

def analyze_chunks():
    with open('ayush_chunks.json') as f:
        chunks = json.load(f)
        
    distinct_groups = set()
    is_19085_chunks = []
    
    for c in chunks:
        distinct_groups.add(c['group'])
        if c['is_number'] == 'IS 19085:2024':
            is_19085_chunks.append(c)
            
    print(f"Total distinct groups in DB: {len(distinct_groups)}")
    print(f"Groups: {list(distinct_groups)}")
    
    print(f"\nIS 19085:2024 Chunk Count: {len(is_19085_chunks)}")
    for i, c in enumerate(is_19085_chunks):
        print(f"Chunk {i+1} Clause: {c['clause']}")
        print(f"Chunk {i+1} Text snippet: {c['text'][:150]}...")

if __name__ == "__main__":
    analyze_chunks()
