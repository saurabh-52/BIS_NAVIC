import os
import time
import json
import asyncio
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import AzureOpenAI
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer, CrossEncoder

load_dotenv()

app = FastAPI()

# 1. Global Init
print("Initializing Models & Connections...")
pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
index = pc.Index("bis-standards-test")

azure_client = AzureOpenAI(
    api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
    api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-08-01-preview"),
    azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT")
)
azure_deployment = os.environ.get("AZURE_OPENAI_CHAT_DEPLOYMENT", "gpt-4.1-mini")

embedder = SentenceTransformer('intfloat/e5-large-v2')
reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2', max_length=512)

GROUPS = [
    "Agriculture, Agricultural Products and Implements",
    "Chemicals, Plastics and their Products including packaging and Environment",
    "Coal and Petroleum products",
    "Education, Educational Services and other related Services",
    "Health, Sports and Fitness Services",
    "Medical and Hospital Equipments",
    "Textile, Textile Products and Machinery"
]

class QueryRequest(BaseModel):
    query: str

class PipelineResult(BaseModel):
    answer: str
    contexts_used: list[dict]
    metrics: dict
    tokens: dict

async def query_namespace(query_vector, namespace):
    loop = asyncio.get_event_loop()
    res = await loop.run_in_executor(None, lambda: index.query(
        vector=query_vector,
        namespace=namespace,
        top_k=25,
        include_metadata=True
    ))
    return res, namespace

@app.post("/ask", response_model=PipelineResult)
async def ask_pipeline(req: QueryRequest):
    query = req.query
    metrics = {}
    tokens = {"prompt": 0, "completion": 0, "total": 0}
    t_start = time.time()
    
    # 1. Triage (Classification)
    t_triage_start = time.time()
    system_prompt = f"""You are a Triage Agent. Select groups from this list ONLY: {json.dumps(GROUPS)}.
CRITICAL RULES FOR AYUSH STANDARDS:
- Botanical names, roots, leaves, and herbs (e.g. Euphorbia, Pilocarpus, Millefolium, Atibala) MUST be mapped to BOTH 'Agriculture, Agricultural Products and Implements' AND 'Health, Sports and Fitness Services' because BIS splits them inconsistently.
- Ayurvedic glossaries and terminology MUST be mapped to BOTH 'Agriculture...' and 'Health...'.
- Siddha medicine tablets (Curanam, Kudinir) are 'Health, Sports and Fitness Services', NOT Chemicals.
Return valid JSON: {{"groups": ["group1"]}} (or empty list if irrelevant)."""
    
    triage_res = azure_client.chat.completions.create(
        model=azure_deployment,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ],
        response_format={"type": "json_object"}
    )
    tokens["prompt"] += triage_res.usage.prompt_tokens
    tokens["completion"] += triage_res.usage.completion_tokens
    
    try:
        namespaces = json.loads(triage_res.choices[0].message.content).get("groups", [])
    except:
        namespaces = []
    
    namespaces = [ns for ns in namespaces if ns in GROUPS]
    metrics["azure_triage_time"] = time.time() - t_triage_start
    
    if not namespaces:
        return PipelineResult(
            answer="I'm sorry, your query does not match any of the standard departments we cover.",
            contexts_used=[],
            metrics=metrics,
            tokens=tokens
        )
        
    # 2. Local Embedding
    t_embed_start = time.time()
    query_vector = embedder.encode("query: " + query).tolist()
    metrics["local_embedding_time"] = time.time() - t_embed_start
    
    # 3. Pinecone Parallel Retrieval
    t_pinecone_start = time.time()
    tasks = [query_namespace(query_vector, ns) for ns in namespaces]
    results = await asyncio.gather(*tasks)
    
    merged = []
    for res, ns in results:
        for match in res.matches:
            merged.append({
                "id": match.id,
                "text": match.metadata.get("text", ""),
                "is_number": match.metadata.get("is_number", "Unknown"),
                "clause": match.metadata.get("clause", "Unknown"),
                "namespace": ns
            })
    metrics["pinecone_parallel_time"] = time.time() - t_pinecone_start
    
    if not merged:
         return PipelineResult(
            answer="I found relevant departments, but could not retrieve specific standards for your query.",
            contexts_used=[],
            metrics=metrics,
            tokens=tokens
        )
    
    # 4. Reranking
    t_rerank_start = time.time()
    model_inputs = [[query, m["text"]] for m in merged]
    scores = reranker.predict(model_inputs)
    for i, score in enumerate(scores):
        merged[i]["rerank_score"] = float(score)
        
    merged.sort(key=lambda x: x["rerank_score"], reverse=True)
    top_k_chunks = merged[:5]
    metrics["local_reranking_time"] = time.time() - t_rerank_start
    
    # 5. Answer Generation
    t_gen_start = time.time()
    context_text = ""
    for i, c in enumerate(top_k_chunks):
        context_text += f"\n[Doc {i+1}] IS Number: {c['is_number']} | Clause: {c['clause']} | Text: {c['text']}"
        
    gen_system_prompt = """You are an expert on Indian Standards (BIS). 
Answer the user's question using ONLY the provided context chunks.
Since the context chunks are just titles and metadata summaries, you may infer answers if a standard's title strongly matches the user's request.
If there are no relevant standards at all, say "I cannot answer this based on the retrieved standards."
CRITICAL: For every factual claim, you must add an inline citation using the IS Number and Clause (e.g. [IS 19356:2025, Clause: Metadata Summary])."""

    gen_res = azure_client.chat.completions.create(
        model=azure_deployment,
        messages=[
            {"role": "system", "content": gen_system_prompt},
            {"role": "user", "content": f"Context chunks:\n{context_text}\n\nQuery: {query}"}
        ]
    )
    
    tokens["prompt"] += gen_res.usage.prompt_tokens
    tokens["completion"] += gen_res.usage.completion_tokens
    metrics["azure_generation_time"] = time.time() - t_gen_start
    
    tokens["total"] = tokens["prompt"] + tokens["completion"]
    metrics["total_latency"] = time.time() - t_start
    
    return PipelineResult(
        answer=gen_res.choices[0].message.content,
        contexts_used=top_k_chunks,
        metrics=metrics,
        tokens=tokens
    )

async def test_pipeline():
    queries = [
        "What are the standards for surgical face masks?",
        "Are there standards for cotton packaging of fertilizers?",
        "Standards for sports equipment in schools."
    ]
    
    for q in queries:
        print(f"\n{'='*60}\nTESTING QUERY: {q}\n{'='*60}")
        req = QueryRequest(query=q)
        res = await ask_pipeline(req)
        
        print("\n--- METRICS ---")
        for k, v in res.metrics.items():
            print(f"{k}: {v:.3f}s")
        print(f"Total Tokens: {res.tokens['total']} (Prompt: {res.tokens['prompt']}, Comp: {res.tokens['completion']})")
        
        print("\n--- ANSWER ---")
        print(res.answer)
        
        print("\n--- CITED CHUNKS ---")
        for c in res.contexts_used:
            print(f"- {c['is_number']} ({c['namespace']})")

if __name__ == "__main__":
    asyncio.run(test_pipeline())
