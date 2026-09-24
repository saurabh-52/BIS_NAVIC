import asyncio
import os
import json
from phase9b_pipeline import ask_pipeline, QueryRequest

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

ALL_TESTS = TEST_SET_ORIGINAL + TEST_SET_HOLDOUT

async def run_eval():
    retrieval_hits = 0
    final_answer_hits = 0
    fallback_count = 0
    fallback_latency = []
    normal_latency = []
    
    print(f"Starting Phase 9b Evaluation on {len(ALL_TESTS)} queries...")
    for i, test in enumerate(ALL_TESTS):
        q = test["query"]
        expected = test["expected"]
        print(f"[{i+1}/{len(ALL_TESTS)}] Testing: '{q}'")
        
        res = await ask_pipeline(QueryRequest(query=q))
        
        retrieved_is_numbers = [c['is_number'] for c in res.contexts_used]
        
        # Check retrieval
        if not expected:
            retrieval_hit = True 
        else:
            retrieval_hit = any(e in retrieved_is_numbers for e in expected)
            
        # Check generation
        answer_correct = False
        if not expected:
            if "I cannot answer this" in res.answer or "not retrieved" in res.answer.lower() or "does not match" in res.answer.lower() or "not find" in res.answer.lower():
                answer_correct = True
        else:
            answer_correct = any(e in res.answer for e in expected)
            
        # Stats
        if retrieval_hit: retrieval_hits += 1
        if answer_correct: final_answer_hits += 1
        
        triggered = res.triage_info.get("fallback_triggered", False)
        if triggered:
            fallback_count += 1
            fallback_latency.append(res.metrics.get("total_latency", 0))
            print(f"   -> FALLBACK TRIGGERED! (Max initial score: {res.triage_info.get('max_initial_similarity', 0):.3f})")
            print(f"      Initial groups: {[g['group'] for g in res.triage_info['initial_groups_searched']]}")
            print(f"      Fallback groups: {res.triage_info['fallback_groups_searched']}")
        else:
            normal_latency.append(res.metrics.get("total_latency", 0))
            
    print("\n" + "="*50)
    print("PHASE 9B: MULTI-LABEL TRIAGE & FALLBACK REPORT")
    print("="*50)
    
    print("\n--- METRICS ---")
    print(f"Total Queries: {len(ALL_TESTS)}")
    print(f"Retrieval Hit Rate: {(retrieval_hits/len(ALL_TESTS))*100:.1f}%")
    print(f"Final Answer Accuracy: {(final_answer_hits/len(ALL_TESTS))*100:.1f}%")
    
    print(f"\n--- FALLBACK STATS ---")
    print(f"Fallback Trigger Rate: {fallback_count}/{len(ALL_TESTS)} ({(fallback_count/len(ALL_TESTS))*100:.1f}%)")
    
    avg_norm = sum(normal_latency)/len(normal_latency) if normal_latency else 0
    avg_fall = sum(fallback_latency)/len(fallback_latency) if fallback_latency else 0
    print(f"Avg Latency (No Fallback): {avg_norm:.3f}s")
    print(f"Avg Latency (With Fallback): {avg_fall:.3f}s")
    print(f"Latency Penalty: +{avg_fall - avg_norm:.3f}s")

if __name__ == "__main__":
    # Test the specific glass container query first
    async def test_glass():
        print("\n--- QUICK TEST: Glass Containers Query ---")
        q = "Are there any specifications for glass containers used in Homoeopathic pharmaceuticals?"
        res = await ask_pipeline(QueryRequest(query=q))
        print("ANSWER:\n", res.answer)
        print("TRIAGE INFO:\n", json.dumps(res.triage_info, indent=2))
        print("------------------------------------------\n")
    
    asyncio.run(test_glass())
    asyncio.run(run_eval())
