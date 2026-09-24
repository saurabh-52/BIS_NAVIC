import asyncio
import json
import statistics
from phase9b_eval import ALL_TESTS, ask_pipeline, QueryRequest

async def analyze_cosine_and_triage():
    print("Running distribution analysis...")
    
    passing_scores = []
    failing_scores = []
    out_of_corpus_scores = []
    triage_counts = []
    
    for test in ALL_TESTS:
        q = test["query"]
        expected = test["expected"]
        is_ooc = (len(expected) == 0)
        
        # We run the pipeline for metrics (this will hit Azure and Pinecone)
        # We can just extract the metrics from the pipeline result
        res = await ask_pipeline(QueryRequest(query=q))
        
        # Triage count
        triage_groups_searched = len(res.triage_info["initial_groups_searched"])
        triage_counts.append(triage_groups_searched)
        
        # Max cosine similarity
        max_sim = res.triage_info["max_initial_similarity"]
        
        if is_ooc:
            out_of_corpus_scores.append(max_sim)
        else:
            # Did it retrieve the expected IS?
            retrieved_is_numbers = [c['is_number'] for c in res.contexts_used]
            hit = any(e in retrieved_is_numbers for e in expected)
            if hit:
                passing_scores.append(max_sim)
            else:
                failing_scores.append(max_sim)
                
    print("\n--- TRIAGE STATS ---")
    print(f"Average groups routed to per query: {statistics.mean(triage_counts):.2f}")
    
    print("\n--- COSINE SIMILARITY DISTRIBUTION (PINECONE) ---")
    if passing_scores:
        print(f"Passing Queries (n={len(passing_scores)}): Min={min(passing_scores):.4f}, Max={max(passing_scores):.4f}, Avg={statistics.mean(passing_scores):.4f}")
    if failing_scores:
        print(f"Failing Queries (n={len(failing_scores)}): Min={min(failing_scores):.4f}, Max={max(failing_scores):.4f}, Avg={statistics.mean(failing_scores):.4f}")
    if out_of_corpus_scores:
        print(f"Out-of-Corpus Queries (n={len(out_of_corpus_scores)}): Min={min(out_of_corpus_scores):.4f}, Max={max(out_of_corpus_scores):.4f}, Avg={statistics.mean(out_of_corpus_scores):.4f}")

if __name__ == "__main__":
    asyncio.run(analyze_cosine_and_triage())
