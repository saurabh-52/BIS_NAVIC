import os
import time
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec
from openai import AzureOpenAI

def main():
    # Load environment variables
    load_dotenv()
    
    # Verify we have the required keys
    azure_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    azure_key = os.environ.get("AZURE_OPENAI_API_KEY")
    azure_deployment = os.environ.get("AZURE_OPENAI_CHAT_DEPLOYMENT", "gpt-4.1-mini")
    azure_api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-08-01-preview") # Fallback version
    pinecone_key = os.environ.get("PINECONE_API_KEY")
    
    if not pinecone_key:
        print("❌ PINECONE_API_KEY not found in .env")
        return
        
    print(f"✅ Found Pinecone key.")
    if azure_endpoint and azure_key:
        print(f"✅ Found Azure OpenAI credentials. Using API version: {azure_api_version}")
    else:
        print("⚠️ Azure OpenAI credentials missing, will skip chat completion test.")

    print("\n--- 1. Testing Local Embeddings ---")
    start_time = time.time()
    print("Loading model 'intfloat/e5-large-v2'...")
    model = SentenceTransformer('intfloat/e5-large-v2')
    load_time = time.time() - start_time
    print(f"Model loaded in {load_time:.2f} seconds.")
    
    # e5 models require 'passage: ' and 'query: ' prefixes
    test_passage = "passage: this is a test standard about domestic appliance safety"
    test_query = "query: is there a standard for domestic appliance safety"
    
    start_time = time.time()
    passage_embedding = model.encode(test_passage).tolist()
    embed_time = time.time() - start_time
    print(f"Embedded passage in {embed_time:.2f} seconds.")
    print(f"Embedding dimension: {len(passage_embedding)}")
    
    if len(passage_embedding) != 1024:
        print(f"❌ Expected dimension 1024, got {len(passage_embedding)}")
        return
        
    query_embedding = model.encode(test_query).tolist()
    
    print("\n--- 2. Testing Pinecone ---")
    pc = Pinecone(api_key=pinecone_key)
    index_name = "bis-standards-test"
    
    if index_name not in pc.list_indexes().names():
        print(f"Creating index '{index_name}'...")
        pc.create_index(
            name=index_name,
            dimension=1024,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
    
    index = pc.Index(index_name)
    
    print("Upserting test passage...")
    index.upsert(
        vectors=[
            {"id": "test-doc-1", "values": passage_embedding, "metadata": {"is_number": "TEST-001", "group": "test"}}
        ]
    )
    
    print("Waiting 3 seconds for index consistency...")
    time.sleep(3)
    
    print("Querying Pinecone...")
    results = index.query(
        vector=query_embedding,
        top_k=1,
        include_metadata=True
    )
    
    print("Query Results:")
    for match in results.matches:
        print(f" - ID: {match.id}, Score: {match.score:.4f}, Meta: {match.metadata}")
        
    if results.matches and results.matches[0].id == "test-doc-1":
        print("✅ Pinecone round-trip successful!")
    else:
        print("❌ Pinecone round-trip failed to retrieve the document.")
        
    print("\n--- 3. Testing Azure OpenAI ---")
    if azure_endpoint and azure_key:
        client = AzureOpenAI(
            api_key=azure_key,
            api_version=azure_api_version,
            azure_endpoint=azure_endpoint
        )
        try:
            print(f"Sending test completion to deployment '{azure_deployment}'...")
            response = client.chat.completions.create(
                model=azure_deployment,
                messages=[
                    {"role": "user", "content": "Say 'Azure OpenAI is working'"}
                ]
            )
            print("Response:", response.choices[0].message.content)
            print("✅ Azure OpenAI test successful!")
        except Exception as e:
            print(f"❌ Azure OpenAI test failed: {e}")

if __name__ == "__main__":
    main()
