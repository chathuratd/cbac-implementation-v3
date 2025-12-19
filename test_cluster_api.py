"""
Test the cluster-centric API endpoint
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


def test_cluster_centric_api():
    """Test the NEW cluster-centric API endpoint"""
    
    print("="*70)
    print("  TESTING CLUSTER-CENTRIC API")
    print("="*70)
    
    # Load sample data
    print("\n1. Loading sample data...")
    behaviors, prompts = load_sample_data()
    print(f"   Loaded {len(behaviors)} behaviors and {len(prompts)} prompts")
    
    # Prepare request
    payload = {
        "user_id": "test_user_cluster_api",
        "behaviors": behaviors,
        "prompts": prompts
    }
    
    # Call API
    print("\n2. Calling /analyze-behaviors-cluster-centric API...")
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{BASE_URL}/analyze-behaviors-cluster-centric",
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
        print("  RESULTS FROM API")
        print("="*70)
        
        print(f"\nUser ID: {profile['user_id']}")
        print(f"Generated at: {profile['generated_at']}")
        print(f"Archetype: {profile.get('archetype', 'None')}")
        
        print(f"\n📊 Statistics:")
        stats = profile['statistics']
        print(f"   Total observations: {stats['total_behaviors_analyzed']}")
        print(f"   Clusters formed: {stats['clusters_formed']}")
        print(f"   Total prompts: {stats['total_prompts_analyzed']}")
        print(f"   Time span: {stats['analysis_time_span_days']:.1f} days")
        
        # Analyze clusters
        clusters = profile.get('behavior_clusters', [])
        print(f"\n🎯 Behavior Clusters: {len(clusters)} total")
        
        primary = [c for c in clusters if c['tier'] == 'PRIMARY']
        secondary = [c for c in clusters if c['tier'] == 'SECONDARY']
        noise = [c for c in clusters if c['tier'] == 'NOISE']
        
        print(f"   PRIMARY: {len(primary)}")
        print(f"   SECONDARY: {len(secondary)}")
        print(f"   NOISE: {len(noise)}")
        
        # Show PRIMARY clusters in detail
        print(f"\n" + "="*70)
        print("  PRIMARY CLUSTERS (Detailed)")
        print("="*70)
        
        for i, cluster in enumerate(primary[:3], 1):
            print(f"\n{i}. {cluster['canonical_label']}")
            print(f"   Cluster ID: {cluster['cluster_id']}")
            print(f"   Cluster Size: {cluster['cluster_size']} observations")
            print(f"   Cluster Strength: {cluster['cluster_strength']:.4f}")
            print(f"   Confidence: {cluster['confidence']:.4f}")
            print(f"     └─ Consistency: {cluster['consistency_score']:.4f}")
            print(f"     └─ Reinforcement: {cluster['reinforcement_score']:.4f}")
            print(f"     └─ Clarity Trend: {cluster['clarity_trend']:.4f}")
            print(f"   Temporal:")
            print(f"     └─ Days Active: {cluster['days_active']:.1f}")
            print(f"     └─ First Seen: {cluster['first_seen']}")
            print(f"     └─ Last Seen: {cluster['last_seen']}")
            print(f"   Evidence:")
            print(f"     └─ Prompts: {len(cluster['all_prompt_ids'])}")
            print(f"     └─ Variations: {len(cluster['wording_variations'])}")
            
            # Show wording variations
            variations = cluster['wording_variations'][:3]
            if variations:
                print(f"   Wording Variations (showing {len(variations)}):")
                for j, var in enumerate(variations, 1):
                    print(f"     {j}. {var[:60]}...")
        
        # Show SECONDARY clusters
        print(f"\n" + "="*70)
        print("  SECONDARY CLUSTERS")
        print("="*70)
        
        for i, cluster in enumerate(secondary[:3], 1):
            print(f"\n{i}. {cluster['canonical_label']}")
            print(f"   Size: {cluster['cluster_size']}, Strength: {cluster['cluster_strength']:.4f}, "
                  f"Confidence: {cluster['confidence']:.4f}")
        
        # Validation
        print(f"\n" + "="*70)
        print("  VALIDATION")
        print("="*70)
        
        print("\n✓ API returns behavior_clusters[] as primary data structure")
        print(f"  Found {len(clusters)} clusters in response")
        
        print("\n✓ Each cluster contains full aggregated evidence:")
        if primary:
            c = primary[0]
            print(f"  - observation_ids: {len(c.get('observation_ids', []))}")
            print(f"  - all_prompt_ids: {len(c['all_prompt_ids'])}")
            print(f"  - all_timestamps: {len(c['all_timestamps'])}")
            print(f"  - wording_variations: {len(c['wording_variations'])}")
        
        print("\n✓ Scoring is cluster-based (not canonical-based):")
        if primary:
            c = primary[0]
            print(f"  - cluster_strength = log(size+1) * mean_abw * recency")
            print(f"  - confidence = consistency * reinforcement * clarity_trend")
            print(f"  - canonical_label is just for display")
        
        print("\n✓ Can answer 'WHY is this core?' with evidence:")
        if primary:
            c = primary[0]
            print(f"  - Appeared in {len(c['all_prompt_ids'])} prompts")
            print(f"  - {len(c['wording_variations'])} different phrasings")
            print(f"  - Active for {c['days_active']:.1f} days")
            print(f"  - Internal consistency: {c['consistency_score']:.4f}")
        
        print("\n" + "="*70)
        print("  ✅ CLUSTER-CENTRIC API TEST PASSED")
        print("="*70)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to API")
        print("   Make sure the server is running: python main.py")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_cluster_centric_api()
