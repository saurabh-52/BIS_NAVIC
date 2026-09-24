import os
import time
import json
import asyncio
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer

load_dotenv()
pinecone_key = os.environ.get("PINECONE_API_KEY")

def ensure_data_upserted(model, index):
    stats = index.describe_index_stats()
    # Check if we already upserted data
    if stats.total_vector_count > 100:
        print("Data already upserted to Pinecone.")
        return

    print("Upserting Phase 3 data to Pinecone...")
    with open("ayush_chunks.json", "r") as f:
        chunks = json.load(f)

    # Prepend "passage: " to text
    texts = ["passage: " + c["text"] for c in chunks]
    
    start_time = time.time()
    print("Embedding 247 chunks...")
    embeddings = model.encode(texts, batch_size=32).tolist()
    print(f"Embedding took {time.time() - start_time:.2f} seconds")

    # Group vectors by namespace
    from collections import defaultdict
    namespace_vectors = defaultdict(list)
    
    for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
        namespace = chunk["group"]
        if not namespace:
            namespace = "Uncategorized"
            
        namespace_vectors[namespace].append({
            "id": f"chunk-{i}",
            "values": emb,
            "metadata": {
                "is_number": chunk["is_number"],
                "clause": chunk["clause"],
                "sub_group": chunk["sub_group"],
                "ics_code": chunk["ics_code"],
                "text": chunk["text"]
            }
        })
        
    # Upsert by namespace
    for ns, vectors in namespace_vectors.items():
        print(f"Upserting {len(vectors)} chunks to namespace '{ns}'...")
        # Batch into smaller chunks of 100 just to be safe
        for i in range(0, len(vectors), 100):
            batch = vectors[i:i+100]
            index.upsert(vectors=batch, namespace=ns)
    print("Upsert complete.")

async def async_query_namespace(index, vector, namespace, top_k=2):
    # Pinecone python client doesn't have native asyncio yet, but we can run it in a threadpool
    # However, for the sake of the exercise, we can wrap the sync call in to_thread
    loop = asyncio.get_event_loop()
    start = time.time()
    res = await loop.run_in_executor(None, lambda: index.query(
        vector=vector,
        namespace=namespace,
        top_k=top_k,
        include_metadata=True
    ))
    return res, time.time() - start

async def run_parallel_retrieval(model, index, query, namespaces):
    print(f"\n--- Testing Query: '{query}' ---")
    
    # 1. Local Embedding
    start_embed = time.time()
    query_vector = model.encode("query: " + query).tolist()
    embed_time = time.time() - start_embed
    print(f"[Local Embedding Latency]: {embed_time:.3f} seconds")
    
    # 2. Parallel Pinecone Query
    print(f"Querying {len(namespaces)} namespaces concurrently: {namespaces}")
    start_pinecone = time.time()
    
    tasks = [async_query_namespace(index, query_vector, ns) for ns in namespaces]
    results = await asyncio.gather(*tasks)
    
    pinecone_time = time.time() - start_pinecone
    print(f"[Pinecone Parallel Query Latency]: {pinecone_time:.3f} seconds")
    
    # Merge results
    merged = []
    for (res, latency), ns in zip(results, namespaces):
        for match in res.matches:
            merged.append({
                "id": match.id,
                "score": match.score,
                "namespace": ns,
                "metadata": match.metadata
            })
            
    # Print results
    print("\nMerged Results (Unranked):")
    for m in merged:
        print(f" - [{m['namespace']}] Score: {m['score']:.4f} | IS Number: {m['metadata'].get('is_number')}")
        print(f"   Text Snippet: {m['metadata'].get('text')[:100]}...")

def main():
    pc = Pinecone(api_key=pinecone_key)
    index = pc.Index("bis-standards-test")
    
    print("Loading model 'intfloat/e5-large-v2'...")
    model = SentenceTransformer('intfloat/e5-large-v2')
    
    ensure_data_upserted(model, index)
    
    # Single namespace query (from Phase 4 test)
    query_1 = "Give me the ICS code for plastic surgery beds."
    ns_1 = ["Medical and Hospital Equipments"]
    
    # Multi namespace query (from Phase 4 test)
    query_2 = "Standards for sports equipment in schools."
    ns_2 = ["Education, Educational Services and other related Services", "Health, Sports and Fitness Services"]
    
    asyncio.run(run_parallel_retrieval(model, index, query_1, ns_1))
    asyncio.run(run_parallel_retrieval(model, index, query_2, ns_2))

if __name__ == "__main__":
    main()
