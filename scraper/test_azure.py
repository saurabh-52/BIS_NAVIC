import os
import time
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()
try:
    client = AzureOpenAI(
        api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
        api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-08-01-preview"),
        azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT")
    )
    
    start_time = time.time()
    response = client.chat.completions.create(
        model=os.environ.get("AZURE_OPENAI_CHAT_DEPLOYMENT", "gpt-4.1-mini"),
        messages=[{"role": "user", "content": "What is the Bureau of Indian Standards (BIS) in one short sentence?"}]
    )
    end_time = time.time()
    
    print(f"✅ SUCCESS (Time taken: {end_time - start_time:.2f} seconds)")
    print("-" * 50)
    print("Response:\n" + response.choices[0].message.content)
    print("-" * 50)
except Exception as e:
    print("❌ ERROR:", type(e).__name__, "-", e)
