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

# We will use the already written ask_pipeline from phase7_pipeline.py
# We just need to define the test set and evaluate it.

TEST_SET = [
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

async def run_eval():
    results_table = []
    failures = []
    
    retrieval_hits = 0
    final_answer_hits = 0
    
    print(f"Starting Evaluation on {len(TEST_SET)} queries...")
    for i, test in enumerate(TEST_SET):
        q = test["query"]
        expected = test["expected"]
        print(f"[{i+1}/{len(TEST_SET)}] Testing: '{q}'")
        
        res = await ask_pipeline(QueryRequest(query=q))
        
        retrieved_is_numbers = [c['is_number'] for c in res.contexts_used]
        
        # Retrieval Hit (Is expected in top 5?)
        # For out-of-corpus, hit means retrieved NOTHING or retrieved irrelevant things but generator rejected it
        if not expected:
            retrieval_hit = True # Not applicable really, but let's count it
            top_1_correct = True
        else:
            # Check if ANY of the expected is in top 5
            retrieval_hit = any(e in retrieved_is_numbers for e in expected)
            top_1_correct = len(retrieved_is_numbers) > 0 and retrieved_is_numbers[0] in expected
            
        # Final answer hit
        answer_correct = False
        if not expected:
            # Should refuse to answer
            if "I cannot answer this" in res.answer or "not retrieved" in res.answer.lower() or "does not match" in res.answer.lower() or "not find" in res.answer.lower():
                answer_correct = True
        else:
            # Should mention at least one expected IS number
            answer_correct = any(e in res.answer for e in expected)
            
        # Citation matches retrieved
        # Check if every IS number mentioned in the answer bracket [...] actually is in retrieved_is_numbers
        # For simplicity, if it refused, it's True. Otherwise check string matches.
        citation_matches = True
        if not answer_correct and not expected:
            pass # Refused properly
        elif answer_correct:
            # We just assume True if it cited the expected one, we will visually inspect failing ones.
            # A strict regex could parse the [IS XXXX:YYYY, Clause: ZZZ] format.
            import re
            citations = re.findall(r'\[IS (.*?)(?:,|\])', res.answer)
            citations = [f"IS {c}" for c in citations]
            for c in citations:
                if c not in retrieved_is_numbers:
                    citation_matches = False
                    
        # Update metrics
        if retrieval_hit: retrieval_hits += 1
        if answer_correct: final_answer_hits += 1
        
        results_table.append({
            "query": q,
            "expected": expected,
            "retrieval_top_5": retrieval_hit,
            "top_1_correct": top_1_correct,
            "answer_correct": answer_correct,
            "citation_matches": citation_matches
        })
        
        if not retrieval_hit:
            failures.append(f"Q: {q} | FAIL REASON: Retrieval missed entirely. Expected: {expected}")
        elif not answer_correct:
            if expected:
                failures.append(f"Q: {q} | FAIL REASON: Generation failed to cite expected IS {expected}. Output: {res.answer[:100]}...")
            else:
                failures.append(f"Q: {q} | FAIL REASON: Hallucination! Output: {res.answer[:100]}...")
                
    print("\n--- RESULTS TABLE ---")
    print(f"{'Query':<60} | {'Expected':<30} | {'Retrieved Top 5?':<18} | {'Ranked #1?':<12} | {'Answer Correct?':<15} | {'Citation Valid?'}")
    print("-" * 170)
    for r in results_table:
        q_trunc = r['query'][:57] + "..." if len(r['query']) > 60 else r['query']
        exp_trunc = ", ".join(r['expected'])[:27] + "..." if len(", ".join(r['expected'])) > 30 else ", ".join(r['expected'])
        if not exp_trunc: exp_trunc = "NONE"
        print(f"{q_trunc:<60} | {exp_trunc:<30} | {str(r['retrieval_top_5']):<18} | {str(r['top_1_correct']):<12} | {str(r['answer_correct']):<15} | {str(r['citation_matches'])}")
        
    print("\n--- METRICS ---")
    print(f"Total Queries: {len(TEST_SET)}")
    print(f"Retrieval Hit Rate (Top-5): {(retrieval_hits/len(TEST_SET))*100:.1f}%")
    print(f"Final Answer Accuracy: {(final_answer_hits/len(TEST_SET))*100:.1f}%")
    
    print("\n--- FAILURES ---")
    for f in failures:
        print("-", f)

if __name__ == "__main__":
    asyncio.run(run_eval())
