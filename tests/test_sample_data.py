"""
Test script to analyze sample behaviors
Tests the complete pipeline with the provided test data
"""
import json
import asyncio
import time
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.models.schemas import BehaviorModel, PromptModel
from src.services.analysis_pipeline import analysis_pipeline
from src.database.mongodb_service import mongodb_service
from src.database.qdrant_service import qdrant_service
from src.services.embedding_service import embedding_service
from src.services.archetype_service import archetype_service


async def test_with_sample_data():
    """Test the complete pipeline with sample data"""
    
    print("="*60)
    print("CBIE MVP - Test with Sample Data")
    print("="*60)
    print()
    
    # Connect to services
    print("Connecting to services...")
    try:
        mongodb_service.connect()
        qdrant_service.connect()
        embedding_service.connect()
        archetype_service.connect()
        print("✓ All services connected\n")
    except Exception as e:
        print(f"✗ Failed to connect to services: {e}")
        return
    
    # Load sample data
    print("Loading sample data...")
    try:
        with open('test-data/behaviors_user_348_1765993674.json', 'r') as f:
            behaviors_data = json.load(f)
        
        with open('test-data/prompts_user_348_1765993674.json', 'r') as f:
            prompts_data = json.load(f)
        
        behaviors = [BehaviorModel(**b) for b in behaviors_data]
        prompts = [PromptModel(**p) for p in prompts_data]
        
        print(f"✓ Loaded {len(behaviors)} behaviors")
        print(f"✓ Loaded {len(prompts)} prompts\n")
        
    except Exception as e:
        print(f"✗ Failed to load sample data: {e}")
        return
    
    # Display sample behaviors
    print("Sample Behaviors:")
    print("-" * 60)
    for i, behavior in enumerate(behaviors[:3], 1):
        print(f"{i}. {behavior.behavior_text}")
        print(f"   Credibility: {behavior.credibility:.2f}, "
              f"Clarity: {behavior.clarity_score:.2f}, "
              f"Confidence: {behavior.extraction_confidence:.2f}")
        print(f"   Reinforcement: {behavior.reinforcement_count}, "
              f"Decay: {behavior.decay_rate}")
    print(f"   ... and {len(behaviors) - 3} more\n")
    
    # Run analysis
    print("Running analysis pipeline...")
    print("-" * 60)
    
    start_time = time.time()
    
    try:
        profile = await analysis_pipeline.analyze_behaviors(
            user_id="user_348",
            behaviors=behaviors,
            prompts=prompts,
            generate_archetype=True,
            current_timestamp=int(time.time())
        )
        
        elapsed = time.time() - start_time
        
        print(f"✓ Analysis complete in {elapsed:.2f} seconds\n")
        
        # Display results
        print("="*60)
        print("ANALYSIS RESULTS")
        print("="*60)
        print()
        
        print(f"User ID: {profile.user_id}")
        print(f"Generated At: {profile.generated_at}")
        print(f"Archetype: {profile.archetype or 'None'}")
        print()
        
        print("Statistics:")
        print(f"  Total Behaviors Analyzed: {profile.statistics.total_behaviors_analyzed}")
        print(f"  Clusters Formed: {profile.statistics.clusters_formed}")
        print(f"  Total Prompts Analyzed: {profile.statistics.total_prompts_analyzed}")
        print(f"  Analysis Time Span: {profile.statistics.analysis_time_span_days:.1f} days")
        print()
        
        print(f"PRIMARY Behaviors ({len(profile.primary_behaviors)}):")
        print("-" * 60)
        for i, behavior in enumerate(profile.primary_behaviors, 1):
            print(f"{i}. {behavior.behavior_text}")
            print(f"   Cluster: {behavior.cluster_id}")
            print(f"   Individual ABW: {behavior.cbi_original:.4f}")
            print(f"   Cluster CBI: {behavior.cluster_cbi:.4f}")
            print(f"   Days Active: {behavior.temporal_span.days_active:.1f}")
            print()
        
        if profile.secondary_behaviors:
            print(f"SECONDARY Behaviors ({len(profile.secondary_behaviors)}):")
            print("-" * 60)
            for i, behavior in enumerate(profile.secondary_behaviors, 1):
                print(f"{i}. {behavior.behavior_text}")
                print(f"   Cluster: {behavior.cluster_id}")
                print(f"   Individual ABW: {behavior.cbi_original:.4f}")
                print(f"   Cluster CBI: {behavior.cluster_cbi:.4f}")
                print(f"   Days Active: {behavior.temporal_span.days_active:.1f}")
                print()
        
        print("="*60)
        print("✓ Test completed successfully!")
        print("="*60)
        
    except Exception as e:
        print(f"✗ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        print("\nDisconnecting from services...")
        mongodb_service.disconnect()
        qdrant_service.disconnect()
        print("✓ Disconnected\n")


if __name__ == "__main__":
    asyncio.run(test_with_sample_data())
