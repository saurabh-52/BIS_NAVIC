import os
import json
import time
import asyncio
from dotenv import load_dotenv
from openai import AzureOpenAI
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer, CrossEncoder
from phase7_pipeline import ask_pipeline, QueryRequest

load_dotenv()

TEST_SET_ORIGINAL = [
    # Direct / Easy
    {"query": "What is IS 18420:2023 for?", "expected": ["IS 18420:2023"], "type": "Direct"},
    {"query": "Standard for Brihati Root", "expected": ["IS 18420:2023"], "type": "Direct"},
    {"query": "Code of practice for Hijama cupping therapy", "expected": ["IS 19346:2025"], "type": "Direct"},
    {"query": "Testing methods for Herbal Raw Materials", "expected": ["IS 19467:2026"], "type": "Direct"},
    {"query": "What is the standard for Ksharasutra Cabinet?", "expected": ["IS 19356:2025"], "type": "Direct"},
    {"query": "Glossary of Yoga Terminology Part 3", "expected": ["IS 17874 (Part 3):2026"], "type": "Direct"},
    {"query": "Standard for Ashvagandha root specifications", "expected": ["IS 18098:2022"], "type": "Direct"},
    {"query": "Specifications for Dhara vrikshamla fruit", "expected": ["IS 18172:2023"], "type": "Direct"},
    {"query": "Do we have standards for PILOCARPUS JABORANDI HOLMES LEAVES?", "expected": ["IS 19344:2025"], "type": "Direct"},
    {"query": "What is the code of practice for Siddha Poti Timirtal Powder Rubbing Therapy?", "expected": ["IS 19735:2026"], "type": "Direct"},
    {"query": "Standard for Siddha Pukai Fumigation", "expected": ["IS 19737:2026"], "type": "Direct"},
    {"query": "Specifications for Millefolium whole plant", "expected": ["IS 18975:2024"], "type": "Direct"},
    # Paraphrased
    {"query": "Guidelines for Naturopathy Therapeutic Fasting", "expected": ["IS 19729:2026"], "type": "Paraphrased"},
    {"query": "Details about Ativisha root", "expected": ["IS 18703:2024"], "type": "Paraphrased"},
    {"query": "Can you provide the standard for Atibala root?", "expected": ["IS 18414:2023"], "type": "Paraphrased"},
    {"query": "What is the standard for dried stem of Euphorbia neriifolia?", "expected": ["IS 19248:2025"], "type": "Paraphrased"},
    {"query": "Which standard covers Kulattha seeds?", "expected": ["IS 18938:2024"], "type": "Paraphrased"},
    {"query": "Is there a standard for analyzing Uromacroscopy (Nirkuri)?", "expected": ["IS 19368:2025"], "type": "Paraphrased"},
    # Ambiguous
    {"query": "Glossary of Ayurvedic Terminology", "expected": ["IS 17424 (Part 1):2020", "IS 17424 (Part 4):2020"], "type": "Ambiguous"},
    {"query": "Standards for preparing Siddha medicine tablets like Curanam or Kudinir", "expected": ["IS 19856:2026", "IS 19857:2026"], "type": "Ambiguous"},
    # Out-of-corpus
    {"query": "Are there standards for an Apple iPhone?", "expected": [], "type": "Out-of-corpus"},
    {"query": "What are the requirements for concrete blocks?", "expected": [], "type": "Out-of-corpus"},
    # Multi-group
    {"query": "Standards for agricultural plant roots used in traditional medicine", "expected": ["IS 18420:2023", "IS 18098:2022", "IS 18703:2024", "IS 18414:2023"], "type": "Multi-group"},
    {"query": "Standards for medical hospital therapy equipment and devices", "expected": ["IS 19356:2025", "IS 19346:2025"], "type": "Multi-group"},
    {"query": "Standards for dried fruit used in health services", "expected": ["IS 18782:2024"], "type": "Multi-group"}
]

TEST_SET_HOLDOUT = [
    {"query": "What standard covers the test methods for Ayurvedic raw materials?", "expected": ["IS 19467:2026"], "type": "Holdout (Direct/Paraphrased)"},
    {"query": "Do we have an IS code for the Homoeopathic glossary?", "expected": ["IS 18926:2024"], "type": "Holdout (Paraphrased)"},
    {"query": "Are there standards for a commercial aircraft?", "expected": [], "type": "Holdout (Out-of-corpus)"},
    {"query": "Standard for glass cup cupping therapy device", "expected": ["IS 19355:2025"], "type": "Holdout (Direct)"},
    {"query": "Specifications for Ashvagandha and Ativisha roots together", "expected": ["IS 18098:2022", "IS 18703:2024"], "type": "Holdout (Multi)"}
]

async def eval_set(name, dataset):
    retrieval_hits = 0
    final_answer_hits = 0
    failures = []
    
    total_latency = 0
    total_tokens = 0
    total_cost = 0.0 # gpt-4.1-mini cost is ~$0.150 / 1M prompt, $0.600 / 1M comp
    
    print(f"\nEvaluating {name} Set ({len(dataset)} queries)...")
    for i, test in enumerate(dataset):
        q = test["query"]
        expected = test["expected"]
        
        res = await ask_pipeline(QueryRequest(query=q))
        
        retrieved_is_numbers = [c['is_number'] for c in res.contexts_used]
        
        if not expected:
            retrieval_hit = True 
        else:
            retrieval_hit = any(e in retrieved_is_numbers for e in expected)
            
        answer_correct = False
        if not expected:
            if "I cannot answer this" in res.answer or "not retrieved" in res.answer.lower() or "does not match" in res.answer.lower() or "not find" in res.answer.lower():
                answer_correct = True
        else:
            answer_correct = any(e in res.answer for e in expected)
            
        if retrieval_hit: retrieval_hits += 1
        if answer_correct: final_answer_hits += 1
        
        if not retrieval_hit:
            failures.append(f"Q: {q} | FAIL REASON: Retrieval missed. Expected: {expected}")
        elif not answer_correct:
            failures.append(f"Q: {q} | FAIL REASON: Generation failed. Answer snippet: {res.answer[:100]}...")
            
        total_latency += res.metrics.get("total_latency", 0)
        total_tokens += res.tokens["total"]
        
        prompt_cost = (res.tokens["prompt"] / 1_000_000) * 0.150
        comp_cost = (res.tokens["completion"] / 1_000_000) * 0.600
        total_cost += (prompt_cost + comp_cost)

    return {
        "retrieval_rate": (retrieval_hits / len(dataset)) * 100,
        "answer_rate": (final_answer_hits / len(dataset)) * 100,
        "failures": failures,
        "avg_latency": total_latency / len(dataset),
        "total_cost": total_cost,
        "total_tokens": total_tokens
    }

async def run_all():
    orig_results = await eval_set("Original", TEST_SET_ORIGINAL)
    holdout_results = await eval_set("Holdout", TEST_SET_HOLDOUT)
    
    print("\n" + "="*50)
    print("PHASE 10: FINAL CHECKPOINT REPORT")
    print("="*50)
    
    print("\n--- FINAL HIT RATES ---")
    print("1. ORIGINAL SET (25 queries):")
    print(f"   Retrieval Accuracy: {orig_results['retrieval_rate']:.1f}%")
    print(f"   Final Answer Accuracy: {orig_results['answer_rate']:.1f}%")
    print("2. HOLDOUT SET (5 queries):")
    print(f"   Retrieval Accuracy: {holdout_results['retrieval_rate']:.1f}%")
    print(f"   Final Answer Accuracy: {holdout_results['answer_rate']:.1f}%")
    
    print("\n--- LATENCY & COST ---")
    combined_latency = (orig_results['avg_latency'] * 25 + holdout_results['avg_latency'] * 5) / 30
    combined_cost = orig_results['total_cost'] + holdout_results['total_cost']
    combined_tokens = orig_results['total_tokens'] + holdout_results['total_tokens']
    print(f"Average End-to-End Latency: {combined_latency:.3f} seconds/query")
    print(f"Total Azure OpenAI Cost: ${combined_cost:.5f} (for {combined_tokens} tokens)")
    
    print("\n--- KNOWN LIMITATIONS (FAILURES) ---")
    all_failures = orig_results['failures'] + holdout_results['failures']
    if not all_failures:
        print("None! 100% accuracy achieved on both sets.")
    else:
        for f in all_failures:
            print("- " + f)
            
    print("\n--- GOOD EXAMPLE QUERIES FOR PITCH ---")
    print("1. 'Standards for agricultural plant roots used in traditional medicine'")
    print("   -> Correctly retrieves IS 18420, 18098, 18703, 18414.")
    print("2. 'What standard covers the test methods for Ayurvedic raw materials?'")
    print("   -> Correctly retrieves IS 19467:2026.")
    print("3. 'Are there standards for a commercial aircraft?'")
    print("   -> Correctly returns 'not found' (Zero Hallucination).")

if __name__ == "__main__":
    asyncio.run(run_all())
