import json
import asyncio
from phase7_pipeline import azure_client, azure_deployment, GROUPS

queries = [
    ("Standard for Ashvagandha root specifications", "IS 18098:2022"),
    ("Specifications for Dhara vrikshamla fruit", "IS 18172:2023"),
    ("Do we have standards for PILOCARPUS JABORANDI HOLMES LEAVES?", "IS 19344:2025"),
    ("Specifications for Millefolium whole plant", "IS 18975:2024"),
    ("Can you provide the standard for Atibala root?", "IS 18414:2023"),
    ("What is the standard for dried stem of Euphorbia neriifolia?", "IS 19248:2025"),
    ("Is there a standard for analyzing Uromacroscopy (Nirkuri)?", "IS 19368:2025"),
    ("Glossary of Ayurvedic Terminology", "IS 17424 (Part 1):2020"),
    ("Standards for preparing Siddha medicine tablets like Curanam or Kudinir", "IS 19856:2026"),
    ("Standards for dried fruit used in health services", "IS 18782:2024")
]

# Load chunks to get the actual groups
with open("ayush_chunks.json") as f:
    chunks = json.load(f)

is_to_group = {c['is_number']: c['group'] for c in chunks}

for q, expected_is in queries:
    expected_group = is_to_group.get(expected_is)
    
    system_prompt = f"You are a Triage Agent. Select groups from this list ONLY: {json.dumps(GROUPS)}.\nReturn valid JSON: {{\"groups\": [\"group1\"]}}"
    res = azure_client.chat.completions.create(
        model=azure_deployment,
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": q}],
        response_format={"type": "json_object"}
    )
    predicted_groups = json.loads(res.choices[0].message.content).get("groups", [])
    
    print(f"Q: {q}")
    print(f"  Expected Group: {expected_group}")
    print(f"  Predicted Groups: {predicted_groups}")
    print(f"  Triage Correct? {expected_group in predicted_groups}")
