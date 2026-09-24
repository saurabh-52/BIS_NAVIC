import time
from sentence_transformers import CrossEncoder

def main():
    print("Loading local CrossEncoder 'cross-encoder/ms-marco-MiniLM-L-6-v2'...")
    model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2', max_length=512)
    
    query = "Standards for sports equipment in schools."
    
    # These are the Phase 5 merged unranked results for the multi-namespace query
    # I am recreating the exact outputs we got from Phase 5 to show before/after
    merged_results = [
        {
            "id": "chunk-19311",
            "score": 0.7649,
            "namespace": "Education",
            "is_number": "IS 19311:2025",
            "text": "Standard IS 19311:2025: Standard Abbreviations of Homoeopathic Drugs. Type: Others. Developed by the..."
        },
        {
            "id": "chunk-18926",
            "score": 0.7598,
            "namespace": "Education",
            "is_number": "IS 18926:2024",
            "text": "Standard IS 18926:2024: Homoeopathy - Glossary of Terms Standardized Terminology for Commonly Used T..."
        },
        {
            "id": "chunk-19355",
            "score": 0.7926,
            "namespace": "Health/Sports",
            "is_number": "IS 19355:2025",
            "text": "Standard IS 19355:2025: UNANI MEDICINE - GLASS CUP MI?JAMA (CUPPING THERAPY) DEVICE. Type: Product S..."
        },
        {
            "id": "chunk-19114",
            "score": 0.7860,
            "namespace": "Health/Sports",
            "is_number": "IS 19114:2025",
            "text": "Standard IS 19114:2025: Common Yoga Protocol -Yoga Practices. Type: Code of Practice. Developed by t..."
        }
    ]
    
    print("\n--- Before Reranking (Ordered by Pinecone Cosine Score) ---")
    # Sort by Pinecone score descending to simulate the merge sort
    merged_results.sort(key=lambda x: x["score"], reverse=True)
    for i, res in enumerate(merged_results):
        print(f"{i+1}. [{res['namespace']}] {res['is_number']} (Pinecone Score: {res['score']:.4f})")
        
    print(f"\nRunning CrossEncoder for query: '{query}'")
    
    # Prepare pairs for cross-encoder
    model_inputs = [[query, res["text"]] for res in merged_results]
    
    start_time = time.time()
    rerank_scores = model.predict(model_inputs)
    rerank_time = time.time() - start_time
    
    # Assign new scores and sort
    for res, new_score in zip(merged_results, rerank_scores):
        res["rerank_score"] = float(new_score)
        
    reranked_results = sorted(merged_results, key=lambda x: x["rerank_score"], reverse=True)
    
    print("\n--- After Reranking (Ordered by CrossEncoder) ---")
    for i, res in enumerate(reranked_results):
        print(f"{i+1}. [{res['namespace']}] {res['is_number']} (CrossEncoder Score: {res['rerank_score']:.4f})")
        
    print(f"\n[Local Reranking Latency]: {rerank_time:.4f} seconds for {len(merged_results)} documents.")

if __name__ == "__main__":
    main()
