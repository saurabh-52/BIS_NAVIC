import asyncio
from phase7_pipeline import ask_pipeline, QueryRequest

async def test():
    q1 = "Are there any specifications for glass containers used in Homoeopathic pharmaceuticals?"
    print(f"TESTING: {q1}")
    res = await ask_pipeline(QueryRequest(query=q1))
    print(f"ANSWER:\n{res.answer}")
    
    q2 = "Is there a standardized terminology glossary for Siddha preventative medicine?"
    print(f"\nTESTING: {q2}")
    res = await ask_pipeline(QueryRequest(query=q2))
    print(f"ANSWER:\n{res.answer}")

asyncio.run(test())
