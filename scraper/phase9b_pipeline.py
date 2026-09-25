import os
import json
import time
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import AzureOpenAI
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer, CrossEncoder

load_dotenv()

app = FastAPI(title="BIS NAVIC AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# Provide context mapping to Triage Agent
GROUP_CONTEXT = {
  "Health, Sports and Fitness Services": "Includes Sub-groups like Health care, Dietary, traditional therapies, Siddha terminology.",
  "Agriculture, Agricultural Products and Implements": "Includes Raw Agricultural products, botanicals, roots, seeds, extracts, Pesticides.",
  "Medical and Hospital Equipments": "Includes Health care facilities, Hospital devices, physical medical instruments.",
  "Education, Educational Services and other related Services": "Includes Higher Education, Education services, glossaries occasionally.",
  "Chemicals, Plastics and their Products including packaging and Environment": "Includes Chemical Products, plastic and glass containers, packaging materials.",
  "Coal and Petroleum products": "Includes Coal and related products.",
  "Textile, Textile Products and Machinery": "Includes Cotton, wool, fabrics, packaging textiles."
}

class QueryRequest(BaseModel):
    query: str

class PipelineResult(BaseModel):
    answer: str
    contexts_used: list[dict]
    metrics: dict
    tokens: dict
    triage_info: dict

async def query_namespace(query_vector, namespace):
    loop = asyncio.get_event_loop()
    try:
        res = await loop.run_in_executor(None, lambda: index.query(
            vector=query_vector,
            namespace=namespace,
            top_k=25,
            include_metadata=True
        ))
        return res, namespace
    except Exception as e:
        print(f"Error querying namespace {namespace}: {e}")
        return None, namespace

@app.post("/ask", response_model=PipelineResult)
async def ask_pipeline(req: QueryRequest):
    query = req.query
    metrics = {}
    tokens = {"prompt": 0, "completion": 0, "total": 0}
    t_start = time.time()
    
    # 1. Triage (Classification)
    t_triage_start = time.time()
    
    context_str = json.dumps(GROUP_CONTEXT, indent=2)
    system_prompt = f"""You are a Triage Agent. You route user queries to the correct document namespaces.
Available Groups and Context: {context_str}

CRITICAL RULES:
- Identify ALL plausible groups for the query.
- For packaging (glass, containers) for medicines, ALWAYS include "Chemicals, Plastics..."
- For botanical/ayurvedic herbs (roots, leaves, extracts), ALWAYS include both "Agriculture..." and "Health..."
- Siddha medicines/tablets (Curanam, Kudinir) belong in "Health...", NOT Chemicals.

Return a JSON ranked list of up to 4 plausible groups with confidence scores (0.0 to 1.0).
Format: {{"groups": [{{"group": "GroupName", "confidence": 0.95}}]}}
ONLY use exact group names from the provided list."""
    
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
        triage_data = json.loads(triage_res.choices[0].message.content).get("groups", [])
    except:
        triage_data = []
    
    # Filter and cap
    # Threshold for initial search: 0.20
    valid_initial_groups = [g for g in triage_data if g["group"] in GROUPS and g.get("confidence", 0) >= 0.20]
    # Sort by confidence descending
    valid_initial_groups.sort(key=lambda x: x.get("confidence", 0), reverse=True)
    valid_initial_groups = valid_initial_groups[:4]
    
    initial_namespaces = [g["group"] for g in valid_initial_groups]
    metrics["azure_triage_time"] = time.time() - t_triage_start
    
    triage_info = {
        "initial_groups_searched": valid_initial_groups,
        "fallback_triggered": False,
        "fallback_groups_searched": [],
        "max_initial_similarity": 0.0
    }
    
    # If triage gave nothing, default to searching all
    if not initial_namespaces:
        initial_namespaces = GROUPS
    
    # 2. Local Embedding
    t_embed_start = time.time()
    query_vector = embedder.encode("query: " + query).tolist()
    metrics["local_embedding_time"] = time.time() - t_embed_start
    
    # Helper to fetch and merge
    async def fetch_and_merge(namespaces_to_search):
        tasks = [query_namespace(query_vector, ns) for ns in namespaces_to_search]
        results = await asyncio.gather(*tasks)
        merged = []
        max_score = 0.0
        for res, ns in results:
            if not res: continue
            for match in res.matches:
                score = match.score
                if score > max_score: max_score = score
                merged.append({
                    "id": match.id,
                    "text": match.metadata.get("text", ""),
                    "is_number": match.metadata.get("is_number", "Unknown"),
                    "clause": match.metadata.get("clause", "Unknown"),
                    "namespace": ns,
                    "pinecone_score": score
                })
        return merged, max_score
        
    # 3. Pinecone Parallel Retrieval (Initial)
    t_pinecone_start = time.time()
    merged, max_score = await fetch_and_merge(initial_namespaces)
    
    triage_info["max_initial_similarity"] = float(max_score)
    
    # Fallback Check
    # Threshold for "strong match" using e5-large-v2 cosine similarity.
    # From gap analysis: Passing Min=0.844, Out-of-Corpus Max=0.784
    # Setting threshold at 0.795 to definitively trigger on out-of-corpus/weak signals.
    FALLBACK_THRESHOLD = 0.795
    fallback_triggered = False
    
    if len(merged) == 0 or max_score < FALLBACK_THRESHOLD:
        fallback_triggered = True
        triage_info["fallback_triggered"] = True
        
        remaining_namespaces = [g for g in GROUPS if g not in initial_namespaces]
        triage_info["fallback_groups_searched"] = remaining_namespaces
        
        if remaining_namespaces:
            # Query the rest
            fallback_merged, fallback_max_score = await fetch_and_merge(remaining_namespaces)
            merged.extend(fallback_merged)
            
    metrics["pinecone_parallel_time"] = time.time() - t_pinecone_start
    
    if not merged:
         return PipelineResult(
            answer="I found relevant departments, but could not retrieve specific standards for your query.",
            contexts_used=[],
            metrics=metrics,
            tokens=tokens,
            triage_info=triage_info
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
        tokens=tokens,
        triage_info=triage_info
    )

async def test_pipeline():
    # specifically test the failing query
    q = "Are there any specifications for glass containers used in Homoeopathic pharmaceuticals?"
    req = QueryRequest(query=q)
    res = await ask_pipeline(req)
    print("ANSWER:", res.answer)
    print("TRIAGE:", json.dumps(res.triage_info, indent=2))

if __name__ == "__main__":
    asyncio.run(test_pipeline())
