"""
Verification script to check that complete behavior data is saved in Qdrant
"""
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

import os
os.chdir(parent_dir)

from src.database.qdrant_service import QdrantService


def main():
    """Verify Qdrant contains complete behavior data"""
    print("Connecting to Qdrant...")
    qdrant_service = QdrantService()
    qdrant_service.connect()
    
    try:
        # Get all behaviors for user_332
        user_id = "user_332"
        print(f"\nFetching behaviors for {user_id}...")
        
        behaviors = qdrant_service.get_embeddings_by_user(user_id)
        
        print(f"\nFound {len(behaviors)} behaviors in Qdrant\n")
        print("=" * 80)
        
        if behaviors:
            # Display first behavior in detail
            first_behavior = behaviors[0]
            
            print("\n📊 FIRST BEHAVIOR (Complete Data):\n")
            print(f"ID: {first_behavior.get('id')}")
            print(f"\n🔢 Vector (first 10 dimensions): {first_behavior.get('vector', [])[:10]}...")
            print(f"Vector length: {len(first_behavior.get('vector', []))} dimensions")
            
            print("\n📦 PAYLOAD (All Metadata):")
            payload = first_behavior.get('payload', {})
            
            for key, value in sorted(payload.items()):
                if key == 'prompt_history_ids':
                    print(f"  • {key}: {value[:3]}... ({len(value)} total)")
                else:
                    print(f"  • {key}: {value}")
            
            print("\n" + "=" * 80)
            print("\n📋 ALL BEHAVIORS SUMMARY:\n")
            
            for i, behavior in enumerate(behaviors, 1):
                payload = behavior.get('payload', {})
                print(f"{i}. {payload.get('behavior_text')}")
                print(f"   └─ Credibility: {payload.get('credibility')}, "
                      f"Reinforcement: {payload.get('reinforcement_count')}, "
                      f"Clarity: {payload.get('clarity_score')}")
            
            # Verify all expected fields are present
            print("\n" + "=" * 80)
            print("\n✅ FIELD VERIFICATION:\n")
            
            expected_fields = [
                'behavior_id', 'behavior_text', 'user_id', 'session_id',
                'credibility', 'reinforcement_count', 'decay_rate',
                'created_at', 'last_seen', 'clarity_score',
                'extraction_confidence', 'prompt_history_ids'
            ]
            
            first_payload = behaviors[0].get('payload', {})
            missing_fields = [field for field in expected_fields if field not in first_payload]
            
            if missing_fields:
                print(f"⚠️  Missing fields: {', '.join(missing_fields)}")
            else:
                print("✅ All expected fields are present!")
            
            # Show sample JSON structure
            print("\n" + "=" * 80)
            print("\n📄 SAMPLE JSON STRUCTURE:\n")
            sample = {
                "id": first_behavior.get('id'),
                "payload": first_payload,
                "vector": first_behavior.get('vector', [])[:10] + ["..."]
            }
            print(json.dumps(sample, indent=2))
            
        else:
            print("❌ No behaviors found in Qdrant!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        qdrant_service.disconnect()
        print("\n✅ Disconnected from Qdrant")


if __name__ == "__main__":
    main()
