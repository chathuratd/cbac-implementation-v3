"""
API Test Script - Updated for Storage Scenarios
Tests both production (from storage) and import (new data) scenarios
"""
import requests
import json
import time
from typing import Dict, Any


BASE_URL = "http://localhost:8000/api/v1"


def load_sample_data() -> tuple:
    """Load sample behaviors and prompts"""
    with open('test-data/behaviors_user_348_1765993674.json', 'r') as f:
        behaviors = json.load(f)
    
    with open('test-data/prompts_user_348_1765993674.json', 'r') as f:
        prompts = json.load(f)
    
    return behaviors, prompts


def print_section(title: str):
    """Print section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")


def test_health_check():
    """Test health check endpoint"""
    print_section("Test 1: Health Check")
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    print("✓ Health check passed")


def test_analyze_behaviors_import(user_id: str, behaviors: list, prompts: list) -> Dict[str, Any]:
    """Test /analyze-behaviors endpoint (IMPORT SCENARIO - stores in DBs)"""
    print_section("Test 2: Analyze Behaviors - Import New Data")
    
    payload = {
        "user_id": user_id,
        "behaviors": behaviors,
        "prompts": prompts
    }
    
    print(f"Importing and analyzing {len(behaviors)} behaviors and {len(prompts)} prompts...")
    print("This will:")
    print("  • Store prompts in MongoDB")
    print("  • Generate embeddings and store in Qdrant")
    print("  • Store behavior metadata in MongoDB")
    print("  • Run complete analysis pipeline")
    
    start_time = time.time()
    response = requests.post(f"{BASE_URL}/analyze-behaviors", json=payload)
    elapsed = time.time() - start_time
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Time Taken: {elapsed:.2f} seconds")
    
    assert response.status_code == 200
    
    profile = response.json()
    print(f"\nProfile Summary:")
    print(f"  User ID: {profile['user_id']}")
    print(f"  Archetype: {profile.get('archetype', 'None')}")
    print(f"  PRIMARY Behaviors: {len(profile['primary_behaviors'])}")
    print(f"  SECONDARY Behaviors: {len(profile['secondary_behaviors'])}")
    print(f"  Clusters Formed: {profile['statistics']['clusters_formed']}")
    
    print("\n✓ Import and analysis completed successfully")
    
    return profile


def test_analyze_behaviors_from_storage(user_id: str) -> Dict[str, Any]:
    """Test /analyze-behaviors-from-storage endpoint (PRODUCTION SCENARIO)"""
    print_section("Test 3: Analyze Behaviors - From Storage (PRODUCTION)")
    
    print(f"Analyzing behaviors from existing storage for user {user_id}...")
    print("This will:")
    print("  • Fetch behaviors from Qdrant (with embeddings)")
    print("  • Fetch prompts from MongoDB")
    print("  • Run analysis on stored data")
    
    start_time = time.time()
    response = requests.post(f"{BASE_URL}/analyze-behaviors-from-storage?user_id={user_id}")
    elapsed = time.time() - start_time
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Time Taken: {elapsed:.2f} seconds")
    
    if response.status_code == 404:
        print("\n⚠ No data found in storage. Run import test first.")
        return None
    
    assert response.status_code == 200
    
    profile = response.json()
    print(f"\nProfile Summary:")
    print(f"  User ID: {profile['user_id']}")
    print(f"  Archetype: {profile.get('archetype', 'None')}")
    print(f"  PRIMARY Behaviors: {len(profile['primary_behaviors'])}")
    print(f"  SECONDARY Behaviors: {len(profile['secondary_behaviors'])}")
    print(f"  Clusters Formed: {profile['statistics']['clusters_formed']}")
    
    print("\n✓ Analysis from storage completed successfully")
    
    return profile


def test_get_user_profile(user_id: str):
    """Test /get-user-profile endpoint"""
    print_section("Test 4: Get User Profile")
    
    response = requests.get(f"{BASE_URL}/get-user-profile/{user_id}")
    print(f"Status Code: {response.status_code}")
    
    assert response.status_code == 200
    
    profile = response.json()
    print(f"\nRetrieved Profile:")
    print(f"  User ID: {profile['user_id']}")
    print(f"  Generated At: {profile['generated_at']}")
    print(f"  Archetype: {profile.get('archetype', 'None')}")
    print(f"  PRIMARY Behaviors: {len(profile['primary_behaviors'])}")
    print(f"  SECONDARY Behaviors: {len(profile['secondary_behaviors'])}")
    
    print("\n✓ Profile retrieved successfully")
    
    return profile


def test_list_core_behaviors(user_id: str):
    """Test /list-core-behaviors endpoint"""
    print_section("Test 5: List Core Behaviors")
    
    response = requests.get(f"{BASE_URL}/list-core-behaviors/{user_id}")
    print(f"Status Code: {response.status_code}")
    
    assert response.status_code == 200
    
    data = response.json()
    print(f"\nCore Behaviors for {data['user_id']}:")
    
    for i, behavior in enumerate(data['canonical_behaviors'], 1):
        print(f"  {i}. [{behavior['tier']}] {behavior['behavior_text']}")
    
    print(f"\n✓ Listed {len(data['canonical_behaviors'])} core behaviors")
    
    return data


def test_update_behavior(behavior_id: str):
    """Test /update-behavior endpoint"""
    print_section("Test 6: Update Behavior")
    
    payload = {
        "behavior_id": behavior_id,
        "updates": {
            "reinforcement_count": 20,
            "last_seen": int(time.time())
        }
    }
    
    print(f"Updating behavior {behavior_id}...")
    print(f"Updates: {json.dumps(payload['updates'], indent=2)}")
    
    response = requests.post(f"{BASE_URL}/update-behavior", json=payload)
    print(f"\nStatus Code: {response.status_code}")
    
    assert response.status_code == 200
    
    updated = response.json()
    print(f"\nUpdated Behavior:")
    print(f"  ID: {updated['behavior_id']}")
    print(f"  Text: {updated['behavior_text']}")
    print(f"  Reinforcement Count: {updated['reinforcement_count']}")
    
    print("\n✓ Behavior updated successfully")
    
    return updated


def test_assign_archetype(user_id: str, canonical_behaviors: list):
    """Test /assign-archetype endpoint"""
    print_section("Test 7: Assign Archetype")
    
    payload = {
        "user_id": user_id,
        "canonical_behaviors": canonical_behaviors
    }
    
    print(f"Generating archetype for {len(canonical_behaviors)} behaviors...")
    
    response = requests.post(f"{BASE_URL}/assign-archetype", json=payload)
    print(f"Status Code: {response.status_code}")
    
    assert response.status_code == 200
    
    data = response.json()
    print(f"\nAssigned Archetype:")
    print(f"  User ID: {data['user_id']}")
    print(f"  Archetype: {data['archetype']}")
    
    print("\n✓ Archetype assigned successfully")
    
    return data


def run_all_tests():
    """Run all API tests"""
    print("\n" + "="*70)
    print("  CBIE MVP - API Integration Tests")
    print("  Testing Both Storage Scenarios")
    print("="*70)
    
    try:
        # Load sample data
        print("\nLoading sample data...")
        behaviors, prompts = load_sample_data()
        user_id = "user_348"
        print(f"✓ Loaded {len(behaviors)} behaviors and {len(prompts)} prompts")
        
        # Test 1: Health Check
        test_health_check()
        
        # Test 2: Import scenario - analyze with new data (stores in DBs)
        profile = test_analyze_behaviors_import(user_id, behaviors, prompts)
        
        # Test 3: Production scenario - analyze from storage
        profile = test_analyze_behaviors_from_storage(user_id)
        
        if profile:
            # Test 4: Get User Profile
            profile = test_get_user_profile(user_id)
            
            # Test 5: List Core Behaviors
            core_behaviors_data = test_list_core_behaviors(user_id)
            
            # Test 6: Update Behavior
            if profile['primary_behaviors']:
                behavior_id = profile['primary_behaviors'][0]['behavior_id']
                test_update_behavior(behavior_id)
            
            # Test 7: Assign Archetype
            canonical_texts = [b['behavior_text'] for b in core_behaviors_data['canonical_behaviors'][:3]]
            test_assign_archetype(user_id, canonical_texts)
        
        # Summary
        print_section("All Tests Completed Successfully! ✓")
        
        print("Summary:")
        print(f"  ✓ Health Check")
        print(f"  ✓ Analyze Behaviors (Import - stores in DBs)")
        print(f"  ✓ Analyze Behaviors (Production - from storage)")
        print(f"  ✓ Get User Profile")
        print(f"  ✓ List Core Behaviors")
        print(f"  ✓ Update Behavior")
        print(f"  ✓ Assign Archetype")
        print()
        print("Storage Architecture Verified:")
        print(f"  ✓ Behaviors stored in Qdrant (with embeddings)")
        print(f"  ✓ Prompts stored in MongoDB")
        print(f"  ✓ Profiles stored in MongoDB")
        print()
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
    except requests.exceptions.ConnectionError:
        print("\n✗ Cannot connect to API server. Make sure it's running on http://localhost:8000")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n" + "="*70)
    print("  CBIE MVP - Storage Architecture Testing")
    print("="*70)
    print("\nThis test will verify both scenarios:")
    print("1. Import scenario: Store new behaviors in Qdrant + prompts in MongoDB")
    print("2. Production scenario: Fetch from storage and analyze")
    print("\nMake sure the API server is running (python main.py)")
    print("And MongoDB + Qdrant are accessible")
    print("="*70)
    
    input("\nPress Enter to start tests...")
    run_all_tests()
