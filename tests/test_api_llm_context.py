"""
Quick API Test Script for LLM Context Endpoint
Tests the /api/v1/profile/{user_id}/llm-context endpoint
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_llm_context_endpoint():
    """Test the LLM context generation endpoint"""
    
    print("=" * 80)
    print("Testing LLM Context API Endpoint")
    print("=" * 80)
    print()
    
    # Test 1: Basic request with defaults
    print("Test 1: Basic Request (default parameters)")
    print("-" * 80)
    try:
        response = requests.get(f"{BASE_URL}/profile/user_665390/llm-context")
        response.raise_for_status()
        data = response.json()
        
        print(f"✅ Status: {response.status_code}")
        print(f"✅ User ID: {data['user_id']}")
        print(f"✅ Archetype: {data['metadata']['archetype']}")
        print(f"✅ Behaviors Included: {data['metadata']['included_behaviors']}")
        print(f"✅ Total Clusters: {data['metadata']['total_clusters']}")
        print()
        print("Context Preview (first 300 chars):")
        print(data['context'][:300] + "...")
        print()
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Custom thresholds
    print("\nTest 2: Custom Thresholds (stricter)")
    print("-" * 80)
    try:
        params = {
            "min_strength": 50.0,
            "min_confidence": 0.45,
            "max_behaviors": 3
        }
        response = requests.get(f"{BASE_URL}/profile/user_665390/llm-context", params=params)
        response.raise_for_status()
        data = response.json()
        
        print(f"✅ Status: {response.status_code}")
        print(f"✅ Behaviors Included: {data['metadata']['included_behaviors']}")
        print(f"✅ Filters Applied: {json.dumps(data['metadata']['filters'], indent=2)}")
        print()
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Without archetype
    print("\nTest 3: Without Archetype")
    print("-" * 80)
    try:
        params = {"include_archetype": False}
        response = requests.get(f"{BASE_URL}/profile/user_665390/llm-context", params=params)
        response.raise_for_status()
        data = response.json()
        
        print(f"✅ Status: {response.status_code}")
        print(f"✅ Archetype in metadata: {data['metadata']['archetype']}")
        print(f"✅ Archetype in context: {'Archetype:' in data['context']}")
        print()
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: More behaviors
    print("\nTest 4: More Behaviors (10 max)")
    print("-" * 80)
    try:
        params = {
            "max_behaviors": 10,
            "min_strength": 25.0
        }
        response = requests.get(f"{BASE_URL}/profile/user_665390/llm-context", params=params)
        response.raise_for_status()
        data = response.json()
        
        print(f"✅ Status: {response.status_code}")
        print(f"✅ Behaviors Included: {data['metadata']['included_behaviors']}")
        print(f"✅ Context length: {len(data['context'])} characters")
        print()
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 5: Non-existent user
    print("\nTest 5: Non-existent User")
    print("-" * 80)
    try:
        response = requests.get(f"{BASE_URL}/profile/nonexistent_user/llm-context")
        print(f"❌ Unexpected success: {response.status_code}")
    except requests.exceptions.HTTPError as e:
        if "404" in str(e):
            print(f"✅ Correctly returned 404 for non-existent user")
        else:
            print(f"❌ Unexpected error: {e}")
    
    print()
    print("=" * 80)
    print("All Tests Complete!")
    print("=" * 80)

if __name__ == "__main__":
    test_llm_context_endpoint()
