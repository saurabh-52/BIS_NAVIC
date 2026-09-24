import json
import asyncio
from phase7_pipeline import azure_client, azure_deployment, GROUPS

q = "Are there any specifications for glass containers used in Homoeopathic pharmaceuticals?"

system_prompt = f"""You are a Triage Agent. Select groups from this list ONLY: {json.dumps(GROUPS)}.
CRITICAL RULES FOR AYUSH STANDARDS:
- Botanical names, roots, leaves, and herbs (e.g. Euphorbia, Pilocarpus, Millefolium, Atibala) MUST be mapped to BOTH 'Agriculture, Agricultural Products and Implements' AND 'Health, Sports and Fitness Services' because BIS splits them inconsistently.
- Ayurvedic glossaries and terminology MUST be mapped to BOTH 'Agriculture...' and 'Health...'.
- Siddha medicine tablets (Curanam, Kudinir) are 'Health, Sports and Fitness Services', NOT Chemicals.
Return valid JSON: {{"groups": ["group1"]}} (or empty list if irrelevant)."""

res = azure_client.chat.completions.create(
    model=azure_deployment,
    messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": q}],
    response_format={"type": "json_object"}
)
predicted_groups = json.loads(res.choices[0].message.content).get("groups", [])
print(f"Predicted Groups by Triage: {predicted_groups}")
