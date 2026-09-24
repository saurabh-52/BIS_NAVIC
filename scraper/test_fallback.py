import asyncio
from phase9b_pipeline import ask_pipeline, QueryRequest

async def test():
    q = "Are there standards for a commercial aircraft?"
    res = await ask_pipeline(QueryRequest(query=q))
    print(f"\n--- FALLBACK TRIGGER TEST ---")
    print(f"Triggered? {res.triage_info['fallback_triggered']}")
    print(f"Max Initial Sim: {res.triage_info['max_initial_similarity']:.4f}")
    
asyncio.run(test())
