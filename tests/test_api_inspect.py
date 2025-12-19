"""
Simple test to call the cluster-centric API and see cluster data in the response
Uses the existing /analyze-behaviors endpoint
"""
import requests
import json
import time


BASE_URL = "http://localhost:8000/api/v1"


def load_sample_data():
    """Load sample behaviors and prompts"""
    with open('test-data/behavior_dataset/behaviors_user_102_1766084125.json', 'r') as f:
        behaviors = json.load(f)
    
    with open('test-data/behavior_dataset/prompts_user_102_1766084125.json', 'r') as f:
        prompts = json.load(f)
    
    return behaviors, prompts


def test_existing_api():
    """Test the existing API and inspect response for cluster data"""
    
    print("="*70)
    print("  TESTING EXISTING API - Inspecting for Cluster Data")
    print("="*70)
    
    # Load sample data
    print("\n1. Loading sample data...")
    behaviors, prompts = load_sample_data()
    print(f"   Loaded {len(behaviors)} behaviors and {len(prompts)} prompts")
    
    # Prepare request
    payload = {
        "user_id": "test_user_api_check",
        "behaviors": behaviors,
        "prompts": prompts
    }
    
    # Call API
    print("\n2. Calling /analyze-behaviors API...")
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{BASE_URL}/analyze-behaviors",
            json=payload,
            timeout=30
        )
        
        elapsed = time.time() - start_time
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response Time: {elapsed:.2f} seconds")
        
        if response.status_code != 200:
            print(f"\n❌ ERROR: {response.text}")
            return
        
        profile = response.json()
        
        # Display results
        print("\n" + "="*70)
        print("  CURRENT API RESPONSE STRUCTURE")
        print("="*70)
        
        print(f"\n📦 Top-level fields in response:")
        for key in profile.keys():
            print(f"   - {key}")
        
        print(f"\n📊 Statistics:")
        stats = profile['statistics']
        print(f"   Total behaviors: {stats['total_behaviors_analyzed']}")
        print(f"   Clusters formed: {stats['clusters_formed']}")
        print(f"   Total prompts: {stats['total_prompts_analyzed']}")
        
        # Check for behavior_clusters
        if 'behavior_clusters' in profile:
            clusters = profile['behavior_clusters']
            print(f"\n✅ NEW: behavior_clusters[] field found!")
            print(f"   Number of clusters: {len(clusters)}")
            
            if clusters:
                print(f"\n   First cluster structure:")
                c = clusters[0]
                for key in c.keys():
                    value = c[key]
                    if isinstance(value, list):
                        print(f"     - {key}: [{len(value)} items]")
                    elif isinstance(value, (int, float)):
                        print(f"     - {key}: {value}")
                    else:
                        print(f"     - {key}: {str(value)[:50]}...")
        else:
            print(f"\n⚠️  behavior_clusters[] not in response (old format)")
        
        # Check legacy fields
        print(f"\n📋 Legacy fields:")
        print(f"   primary_behaviors: {len(profile.get('primary_behaviors', []))}")
        print(f"   secondary_behaviors: {len(profile.get('secondary_behaviors', []))}")
        
        if profile.get('primary_behaviors'):
            print(f"\n   Primary behavior structure:")
            b = profile['primary_behaviors'][0]
            for key in b.keys():
                print(f"     - {key}")
        
        print("\n" + "="*70)
        print("  To see FULL cluster-centric data, use:")
        print("  python test_cluster_pipeline.py")
        print("  (bypasses API, uses pipeline directly)")
        print("="*70)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to API")
        print("   Make sure the server is running")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")


if __name__ == "__main__":
    test_existing_api()
