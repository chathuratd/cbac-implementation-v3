"""Test LLM Context Generation"""
import asyncio
import sys
from src.services.llm_context_service import generate_llm_context
from src.database.mongodb_service import mongodb_service

async def test_llm_context():
    # Initialize MongoDB service
    mongodb_service.connect()
    
    try:
        print("Testing LLM context generation for user_665390...\n")
        
        result = await generate_llm_context(
            user_id="user_665390",
            min_strength=30.0,  # Lower threshold to 30%
            min_confidence=0.40,  # Lower confidence to 40%
            max_behaviors=5,
            include_archetype=True
        )
        
        if result:
            print("=" * 80)
            print("LLM CONTEXT OUTPUT")
            print("=" * 80)
            print(result['context'])
            print("\n" + "=" * 80)
            print("METADATA")
            print("=" * 80)
            print(f"User ID: {result['user_id']}")
            print(f"Total Clusters: {result['metadata']['total_clusters']}")
            print(f"Included Behaviors: {result['metadata']['included_behaviors']}")
            print(f"Archetype: {result['metadata']['archetype']}")
            print(f"Filters: {result['metadata']['filters']}")
            print(f"Summary: {result['metadata']['summary']}")
        else:
            print("ERROR: No profile found for user_665390")
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        mongodb_service.disconnect()

if __name__ == "__main__":
    asyncio.run(test_llm_context())
