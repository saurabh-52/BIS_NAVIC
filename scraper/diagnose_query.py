import os
import sys
import json
from dotenv import load_dotenv

load_dotenv()

from query_analyzer import QueryAnalyzer

azure_client = None
azure_deployment = None

try:
    from openai import AzureOpenAI
    api_key = os.environ.get("AZURE_OPENAI_API_KEY")
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    if api_key and endpoint:
        azure_client = AzureOpenAI(
            api_key=api_key,
            api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-08-01-preview"),
            azure_endpoint=endpoint,
        )
        azure_deployment = os.environ.get("AZURE_OPENAI_CHAT_DEPLOYMENT", "gpt-4.1-mini")
except Exception as e:
    print(f"Azure OpenAI connection failed: {e}")

# Initialize the generic Query Analyzer (auto-discovers DB metadata)
analyzer = QueryAnalyzer(
    azure_client=azure_client,
    azure_deployment=azure_deployment
)

# Test query
query = sys.argv[1] if len(sys.argv) > 1 else "Are there any specifications for glass containers used in Homoeopathic pharmaceuticals?"

print(f"\nAnalyzing Query with Generic Query Analyzer:\n'{query}'\n")
result = analyzer.analyze(query)
print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
