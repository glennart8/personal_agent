import asyncio
from backend.rag_agent import diary_agent

async def main():
    query = "Vad finns det för samband mellan träning/fysisk aktivitet och mitt humör?"
    
    print(f"Query: {query}\n")
    
    result = await diary_agent.run(query)
    
    print("\nSvar från agenten:")
    print(result.output)

if __name__ == "__main__":
    asyncio.run(main())