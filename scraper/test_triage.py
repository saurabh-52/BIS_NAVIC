import os
import json
from dotenv import load_dotenv
from openai import AzureOpenAI
from pydantic import BaseModel, Field

# Load environment
load_dotenv()

# We will try to use Structured Outputs with Pydantic if supported by the model version,
# else we'll fallback to JSON mode or manual JSON parsing.
# Azure API version 2024-08-01-preview supports Structured Outputs for newer models (like gpt-4o).
# gpt-4.1-mini might support it. We'll try JSON mode at a minimum.

GROUPS = [
    "Agriculture, Agricultural Products and Implements",
    "Chemicals, Plastics and their Products including packaging and Environment",
    "Coal and Petroleum products",
    "Education, Educational Services and other related Services",
    "Health, Sports and Fitness Services",
    "Medical and Hospital Equipments",
    "Textile, Textile Products and Machinery"
]

class TriageResponse(BaseModel):
    groups: list[str] = Field(description="List of matching groups from the allowed list, or an empty list if none match.")
    reasoning: str = Field(description="Short reasoning for why these groups were chosen or why none matched.")

def classify_query(query: str):
    client = AzureOpenAI(
        api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
        api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-08-01-preview"),
        azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT")
    )
    
    deployment = os.environ.get("AZURE_OPENAI_CHAT_DEPLOYMENT", "gpt-4.1-mini")
    
    system_prompt = f"""You are the Triage Classification Agent for BIS NAVIC.
Your job is to route user queries to the relevant standards group(s).
You must select from the exact following list of groups ONLY:
{json.dumps(GROUPS, indent=2)}

If the query matches one or more groups, return them.
If the query is vague, off-topic, or matches NO groups, return an empty list.

Return ONLY a valid JSON object matching this schema:
{{
  "groups": ["group1", "group2"],
  "reasoning": "brief explanation"
}}
"""

    try:
        # Try response_format JSON_OBJECT first (supported by most recent APIs)
        response = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        return json.loads(content), "Native JSON Mode"
    except Exception as e:
        # Fallback to normal parsing if json_object format is not supported
        try:
            response = client.chat.completions.create(
                model=deployment,
                messages=[
                    {"role": "system", "content": system_prompt + "\nDO NOT wrap in markdown blocks, just return raw JSON."},
                    {"role": "user", "content": query}
                ]
            )
            content = response.choices[0].message.content.strip()
            if content.startswith("```json"):
                content = content[7:-3].strip()
            return json.loads(content), "Fallback Manual Parsing"
        except Exception as fallback_e:
            return {"groups": [], "reasoning": f"Failed: {str(fallback_e)}"}, "Failed"

def main():
    queries = [
        "What are the standards for surgical face masks?", # Clear single-category (Medical)
        "Do you have guidelines on Ayurvedic hospital management?", # Single (Health)
        "Are there standards for cotton packaging of fertilizers?", # Multi (Textile + Agriculture + Chemicals)
        "Standards for sports equipment in schools.", # Multi (Sports/Health + Education)
        "Is there a standard for domestic appliance safety?", # Off-topic (No match in AYUSH)
        "Tell me a joke about standards.", # Vague/Off-topic (No match)
        "Give me the ICS code for plastic surgery beds.", # Medical
        "Standards for coal-based textile dye." # Multi (Coal + Textile + Chemical)
    ]
    
    print("Testing Triage Agent against 8 sample queries...\n")
    
    for q in queries:
        print(f"Query: '{q}'")
        result, mode = classify_query(q)
        print(f"Mode: {mode}")
        print(f"Matching Groups: {result.get('groups')}")
        print(f"Reasoning: {result.get('reasoning')}")
        print("-" * 50)

if __name__ == "__main__":
    main()
