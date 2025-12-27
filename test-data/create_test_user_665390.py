"""
Create comprehensive test dataset for user_665390
This will create behaviors and prompts for testing the frontend
"""
import json
import time
from pathlib import Path

# Base timestamp (30 days ago)
base_time = int(time.time()) - (30 * 24 * 60 * 60)

# Create varied behaviors that will cluster into PRIMARY, SECONDARY, and NOISE
behaviors = [
    # Cluster 1: Visual Learning Preference (PRIMARY - high reinforcement)
    {
        "behavior_id": "beh_001",
        "behavior_text": "prefers visual diagrams and charts",
        "credibility": 0.95,
        "reinforcement_count": 12,
        "last_seen": base_time + (25 * 24 * 60 * 60),
        "timestamp": base_time + (25 * 24 * 60 * 60),
        "prompt_history_ids": ["prompt_001", "prompt_005", "prompt_010", "prompt_015", "prompt_020", "prompt_025", "prompt_030", "prompt_035", "prompt_040", "prompt_045", "prompt_050", "prompt_055"],
        "clarity_score": 0.98,
        "confidence": 0.92,
        "extraction_confidence": 0.92,
        "decay_rate": 0.01,
        "user_id": "user_665390",
        "session_id": "sess_001"
    },
    {
        "behavior_id": "beh_002",
        "behavior_text": "learns best through visual examples",
        "credibility": 0.93,
        "reinforcement_count": 10,
        "last_seen": base_time + (24 * 24 * 60 * 60),
        "timestamp": base_time + (24 * 24 * 60 * 60),
        "prompt_history_ids": ["prompt_003", "prompt_008", "prompt_013", "prompt_018", "prompt_023", "prompt_028", "prompt_033", "prompt_038", "prompt_043", "prompt_048"],
        "clarity_score": 0.96,
        "confidence": 0.88,
        "extraction_confidence": 0.88,
        "decay_rate": 0.01,
        "user_id": "user_665390",
        "session_id": "sess_001"
    },
    {
        "behavior_id": "beh_003",
        "behavior_text": "requests flowcharts and infographics",
        "credibility": 0.90,
        "reinforcement_count": 8,
        "last_seen": base_time + (23 * 24 * 60 * 60),
        "timestamp": base_time + (23 * 24 * 60 * 60),
        "prompt_history_ids": ["prompt_007", "prompt_012", "prompt_017", "prompt_022", "prompt_027", "prompt_032", "prompt_037", "prompt_042"],
        "clarity_score": 0.94,
        "confidence": 0.85,
        "extraction_confidence": 0.85,
        "decay_rate": 0.01,
        "user_id": "user_665390",
        "session_id": "sess_002"
    },
    
    # Cluster 2: Step-by-Step Learning (PRIMARY - high reinforcement)
    {
        "behavior_id": "beh_004",
        "behavior_text": "prefers step-by-step explanations",
        "credibility": 0.98,
        "reinforcement_count": 15,
        "last_seen": base_time + (27 * 24 * 60 * 60),
        "timestamp": base_time + (27 * 24 * 60 * 60),
        "prompt_history_ids": ["prompt_002", "prompt_006", "prompt_011", "prompt_016", "prompt_021", "prompt_026", "prompt_031", "prompt_036", "prompt_041", "prompt_046", "prompt_051", "prompt_056", "prompt_058", "prompt_060", "prompt_062"],
        "clarity_score": 0.99,
        "confidence": 0.94,
        "extraction_confidence": 0.94,
        "decay_rate": 0.01,
        "user_id": "user_665390",
        "session_id": "sess_001"
    },
    {
        "behavior_id": "beh_005",
        "behavior_text": "requests detailed instructions with examples",
        "credibility": 0.94,
        "reinforcement_count": 11,
        "last_seen": base_time + (26 * 24 * 60 * 60),
        "timestamp": base_time + (26 * 24 * 60 * 60),
        "prompt_history_ids": ["prompt_004", "prompt_009", "prompt_014", "prompt_019", "prompt_024", "prompt_029", "prompt_034", "prompt_039", "prompt_044", "prompt_049", "prompt_054"],
        "clarity_score": 0.97,
        "confidence": 0.90,
        "extraction_confidence": 0.90,
        "decay_rate": 0.01,
        "user_id": "user_665390",
        "session_id": "sess_001"
    },
    {
        "behavior_id": "beh_006",
        "behavior_text": "breaks complex topics into smaller parts",
        "credibility": 0.92,
        "reinforcement_count": 9,
        "last_seen": base_time + (25 * 24 * 60 * 60),
        "timestamp": base_time + (25 * 24 * 60 * 60),
        "prompt_history_ids": ["prompt_015", "prompt_020", "prompt_025", "prompt_030", "prompt_035", "prompt_040", "prompt_045", "prompt_050", "prompt_055"],
        "clarity_score": 0.95,
        "confidence": 0.87,
        "extraction_confidence": 0.87,
        "decay_rate": 0.01,
        "user_id": "user_665390",
        "session_id": "sess_002"
    },
    
    # Cluster 3: Practical Application Focus (SECONDARY - medium reinforcement)
    {
        "behavior_id": "beh_007",
        "behavior_text": "focuses on practical real-world applications",
        "credibility": 0.88,
        "reinforcement_count": 6,
        "last_seen": base_time + (22 * 24 * 60 * 60),
        "timestamp": base_time + (22 * 24 * 60 * 60),
        "prompt_history_ids": ["prompt_008", "prompt_018", "prompt_028", "prompt_038", "prompt_048", "prompt_058"],
        "clarity_score": 0.91,
        "confidence": 0.82,
        "extraction_confidence": 0.82,
        "decay_rate": 0.01,
        "user_id": "user_665390",
        "session_id": "sess_003"
    },
    {
        "behavior_id": "beh_008",
        "behavior_text": "asks for use cases and practical examples",
        "credibility": 0.86,
        "reinforcement_count": 5,
        "last_seen": base_time + (21 * 24 * 60 * 60),
        "timestamp": base_time + (21 * 24 * 60 * 60),
        "prompt_history_ids": ["prompt_012", "prompt_022", "prompt_032", "prompt_042", "prompt_052"],
        "clarity_score": 0.89,
        "confidence": 0.80,
        "extraction_confidence": 0.80,
        "decay_rate": 0.01,
        "user_id": "user_665390",
        "session_id": "sess_003"
    },
    
    # Cluster 4: Code-First Learning (SECONDARY - medium reinforcement)
    {
        "behavior_id": "beh_009",
        "behavior_text": "prefers code examples over theory",
        "credibility": 0.85,
        "reinforcement_count": 7,
        "last_seen": base_time + (20 * 24 * 60 * 60),
        "timestamp": base_time + (20 * 24 * 60 * 60),
        "prompt_history_ids": ["prompt_005", "prompt_015", "prompt_025", "prompt_035", "prompt_045", "prompt_055", "prompt_060"],
        "clarity_score": 0.90,
        "confidence": 0.81,
        "extraction_confidence": 0.81,
        "decay_rate": 0.01,
        "user_id": "user_665390",
        "session_id": "sess_004"
    },
    {
        "behavior_id": "beh_010",
        "behavior_text": "learns through hands-on coding",
        "credibility": 0.83,
        "reinforcement_count": 5,
        "last_seen": base_time + (19 * 24 * 60 * 60),
        "timestamp": base_time + (19 * 24 * 60 * 60),
        "prompt_history_ids": ["prompt_010", "prompt_020", "prompt_030", "prompt_040", "prompt_050"],
        "clarity_score": 0.88,
        "confidence": 0.78,
        "extraction_confidence": 0.78,
        "decay_rate": 0.01,
        "user_id": "user_665390",
        "session_id": "sess_004"
    },
    
    # Cluster 5: Avoids Technical Jargon (SECONDARY - medium reinforcement)
    {
        "behavior_id": "beh_011",
        "behavior_text": "avoids technical jargon",
        "credibility": 0.82,
        "reinforcement_count": 4,
        "last_seen": base_time + (18 * 24 * 60 * 60),
        "timestamp": base_time + (18 * 24 * 60 * 60),
        "prompt_history_ids": ["prompt_007", "prompt_017", "prompt_027", "prompt_037"],
        "clarity_score": 0.95,
        "confidence": 0.81,
        "extraction_confidence": 0.81,
        "decay_rate": 0.01,
        "user_id": "user_665390",
        "session_id": "sess_005"
    },
    {
        "behavior_id": "beh_012",
        "behavior_text": "prefers simple language explanations",
        "credibility": 0.80,
        "reinforcement_count": 4,
        "last_seen": base_time + (17 * 24 * 60 * 60),
        "timestamp": base_time + (17 * 24 * 60 * 60),
        "prompt_history_ids": ["prompt_011", "prompt_021", "prompt_031", "prompt_041"],
        "clarity_score": 0.93,
        "confidence": 0.79,
        "extraction_confidence": 0.79,
        "decay_rate": 0.01,
        "user_id": "user_665390",
        "session_id": "sess_005"
    },
    
    # Noise behaviors (low reinforcement, should be NOISE tier)
    {
        "behavior_id": "beh_013",
        "behavior_text": "occasionally asks about advanced algorithms",
        "credibility": 0.65,
        "reinforcement_count": 1,
        "last_seen": base_time + (10 * 24 * 60 * 60),
        "timestamp": base_time + (10 * 24 * 60 * 60),
        "prompt_history_ids": ["prompt_047"],
        "clarity_score": 0.70,
        "confidence": 0.60,
        "extraction_confidence": 0.60,
        "decay_rate": 0.01,
        "user_id": "user_665390",
        "session_id": "sess_006"
    },
    {
        "behavior_id": "beh_014",
        "behavior_text": "sometimes mentions system architecture",
        "credibility": 0.68,
        "reinforcement_count": 2,
        "last_seen": base_time + (8 * 24 * 60 * 60),
        "timestamp": base_time + (8 * 24 * 60 * 60),
        "prompt_history_ids": ["prompt_053", "prompt_059"],
        "clarity_score": 0.72,
        "confidence": 0.62,
        "extraction_confidence": 0.62,
        "decay_rate": 0.01,
        "user_id": "user_665390",
        "session_id": "sess_006"
    },
    {
        "behavior_id": "beh_015",
        "behavior_text": "rarely discusses database optimization",
        "credibility": 0.70,
        "reinforcement_count": 1,
        "last_seen": base_time + (5 * 24 * 60 * 60),
        "timestamp": base_time + (5 * 24 * 60 * 60),
        "prompt_history_ids": ["prompt_061"],
        "clarity_score": 0.75,
        "confidence": 0.64,
        "extraction_confidence": 0.64,
        "decay_rate": 0.01,
        "user_id": "user_665390",
        "session_id": "sess_007"
    }
]

# Create corresponding prompts
prompts = []
for i in range(1, 63):
    prompts.append({
        "prompt_id": f"prompt_{i:03d}",
        "prompt_text": f"Sample prompt {i} for testing user behavior analysis",
        "timestamp": base_time + (i * 12 * 60 * 60),  # Spread over 30 days
        "tokens": 10.0 + (i % 5),
        "user_id": "user_665390",
        "session_id": f"sess_{(i % 7) + 1:03d}"
    })

# Save to files
output_dir = Path(__file__).parent / "behavior_dataset"
output_dir.mkdir(exist_ok=True)

with open(output_dir / "behaviors_user_665390.json", "w") as f:
    json.dump(behaviors, f, indent=2)

with open(output_dir / "prompts_user_665390.json", "w") as f:
    json.dump(prompts, f, indent=2)

print(f"✓ Created test dataset for user_665390")
print(f"  - {len(behaviors)} behaviors (will form ~5 clusters)")
print(f"  - {len(prompts)} prompts")
print(f"  - Saved to: {output_dir}")
print(f"\nBehavior distribution:")
print(f"  - Visual Learning (PRIMARY): 3 behaviors, 30 total observations")
print(f"  - Step-by-Step (PRIMARY): 3 behaviors, 35 total observations")
print(f"  - Practical Focus (SECONDARY): 2 behaviors, 11 total observations")
print(f"  - Code-First (SECONDARY): 2 behaviors, 12 total observations")
print(f"  - Simple Language (SECONDARY): 2 behaviors, 8 total observations")
print(f"  - Noise behaviors: 3 behaviors, 4 total observations")
