import json
import random
import time
import hashlib
from typing import List, Dict, Tuple

# ------------------ CONFIG ------------------

OUTPUT_DIR = "./behavior_dataset/"

# ------------------ Utilities ------------------

def generate_id(prefix: str) -> str:
    seed = f"{random.random()}{time.time()}"
    return f"{prefix}_{hashlib.md5(seed.encode()).hexdigest()[:8]}"

def estimate_tokens(text: str) -> float:
    return round(len(text) / 4, 1)

# ------------------ Expanded Behavior Library ------------------

BEHAVIOR_LIBRARY = {
    "prefers step-by-step guides": [
        "Walk me through deploying a web app step by step",
        "How do I set up a React project? Step by step please",
        "Guide me through Git workflow from start to finish",
        "Step by step tutorial for Docker setup",
        "Teach me Python basics one step at a time",
        "Break down the CI/CD pipeline process for me",
        "Take me through database normalization step by step",
        "How do I implement authentication? Show each step"
    ],
    "likes quick summaries": [
        "Quick overview of Python async/await",
        "Summarize machine learning in 3 sentences",
        "Brief explanation of blockchain",
        "What's Redux? Short answer please",
        "TL;DR on GraphQL vs REST",
        "Give me the gist of microservices",
        "Kubernetes in a nutshell",
        "Quick rundown of design patterns"
    ],
    "prefers visual learning": [
        "Can you show me a diagram of how DNS works?",
        "Visualize the HTTP request lifecycle",
        "Draw a flowchart for authentication process",
        "Show me a chart comparing SQL databases",
        "Diagram the MVC architecture",
        "Create a visual representation of data structures",
        "Map out the software development lifecycle",
        "Illustrate how websockets work"
    ],
    "avoids technical jargon": [
        "Explain API in simple terms for beginners",
        "What's cloud computing without technical terms?",
        "How does the internet work? Explain like I'm 5",
        "Simple explanation of encryption",
        "What's a database? Use everyday language",
        "Break down machine learning for non-programmers",
        "Explain version control like I'm new to coding",
        "What does scalability mean in plain English?"
    ],
    "prefers detailed technical documentation": [
        "Explain the entire Kubernetes architecture",
        "Give me a comprehensive guide to Docker networking",
        "Detailed OAuth2 explanation with all grant types",
        "Full breakdown of React lifecycle methods",
        "Explain microservices design patterns in depth",
        "Deep dive into PostgreSQL query optimization",
        "Complete guide to AWS Lambda with best practices",
        "Comprehensive analysis of thread safety in Java"
    ],
    "learns by examples": [
        "Show me code examples for async programming",
        "Give me real-world examples of factory pattern",
        "Demonstrate REST API with actual use cases",
        "Show practical examples of recursion",
        "Can you provide sample code for JWT authentication?",
        "Examples of how to use React hooks in practice",
        "Real applications of binary search trees",
        "Show me different ways to handle errors with examples"
    ],
    "prefers comparative analysis": [
        "Compare React vs Vue vs Angular",
        "What's the difference between SQL and NoSQL?",
        "Compare microservices and monolithic architecture",
        "Contrast REST and GraphQL APIs",
        "Docker vs Kubernetes - what's the difference?",
        "Compare different sorting algorithms",
        "Pros and cons of TypeScript vs JavaScript",
        "Difference between authentication and authorization"
    ],
    "focuses on best practices": [
        "What are the best practices for API design?",
        "Best way to structure a React application?",
        "Security best practices for Node.js",
        "How should I organize my Git commits?",
        "Best practices for writing clean code",
        "What's the recommended way to handle errors?",
        "Industry standards for database design",
        "Best practices for test-driven development"
    ],
    "troubleshooting oriented": [
        "Why is my API returning 500 errors?",
        "How do I fix memory leaks in JavaScript?",
        "Debugging CORS issues in my application",
        "My Docker container won't start, help?",
        "Git merge conflicts - how to resolve?",
        "Why isn't my CSS styling applying?",
        "Database query running slow, what's wrong?",
        "React component not re-rendering, why?"
    ],
    "theory and concept focused": [
        "Explain the theory behind neural networks",
        "What is the CAP theorem?",
        "Discuss the principles of functional programming",
        "Explain time complexity in algorithms",
        "What are the SOLID principles?",
        "Theory behind public key cryptography",
        "Explain the concept of eventual consistency",
        "What is the actor model in concurrent programming?"
    ],
    "project-based learning": [
        "Help me build a todo app from scratch",
        "Guide me through creating a REST API project",
        "I want to build a chat application, where do I start?",
        "Let's create an e-commerce site together",
        "Help me develop a portfolio website",
        "Building a blog platform - full project walkthrough",
        "Create a weather app with me step by step",
        "Guide me in building a URL shortener service"
    ],
    "prefers analogies and metaphors": [
        "Explain databases using a real-world analogy",
        "What's a good metaphor for understanding APIs?",
        "Compare programming to something non-technical",
        "Use an analogy to explain cloud computing",
        "Relate microservices to something I can visualize",
        "Explain caching like I'm learning about a library",
        "What's a good analogy for understanding Git?",
        "Compare different data structures to everyday objects"
    ]
}

# Topic domains for more variety
TOPIC_DOMAINS = [
    "web development", "data science", "DevOps", "mobile development",
    "cloud computing", "security", "databases", "machine learning",
    "system design", "testing", "frontend", "backend", "API design"
]

# Complexity levels
COMPLEXITY_LEVELS = ["beginner", "intermediate", "advanced", "expert"]

# Session contexts
SESSION_CONTEXTS = [
    "debugging", "learning", "implementing", "researching",
    "optimizing", "refactoring", "planning", "reviewing"
]

# ------------------ Core Generator ------------------

def calculate_target_profile(num_behaviors: int, profile_type: str = "balanced"):
    """
    Calculate target behavior distribution for different profile types
    
    Profile types:
    - balanced: Mix of primary (2-3), secondary (3-5), noise (remaining)
    - focused: Heavily weighted toward 1-2 primary behaviors
    - exploratory: Many secondary behaviors, few primary
    - noisy: Mostly noise with few clear patterns
    """
    if profile_type == "focused":
        num_primary = min(2, num_behaviors)
        num_secondary = min(3, num_behaviors - num_primary)
    elif profile_type == "exploratory":
        num_primary = min(1, num_behaviors)
        num_secondary = min(num_behaviors - 2, 5)
    elif profile_type == "noisy":
        num_primary = 0
        num_secondary = min(2, num_behaviors)
    else:  # balanced
        num_primary = min(3, max(2, num_behaviors // 4))
        num_secondary = min(5, max(3, num_behaviors // 3))
    
    num_noise = max(0, num_behaviors - num_primary - num_secondary)
    
    return {
        "primary": num_primary,
        "secondary": num_secondary,
        "noise": num_noise
    }

def calculate_reinforcement_target(tier: str, num_prompts: int) -> int:
    """Calculate target reinforcement count based on tier"""
    if tier == "primary":
        # PRIMARY needs high reinforcement: 15-30% of prompts
        min_count = max(3, int(num_prompts * 0.15))
        max_count = max(min_count + 1, min(50, int(num_prompts * 0.30)))
        return random.randint(min_count, max_count)
    elif tier == "secondary":
        # SECONDARY moderate reinforcement: 8-15% of prompts
        min_count = max(2, int(num_prompts * 0.08))
        max_count = max(min_count + 1, min(20, int(num_prompts * 0.15)))
        return random.randint(min_count, max_count)
    else:  # noise
        # NOISE low reinforcement: 2-7% of prompts
        min_count = max(1, int(num_prompts * 0.02))
        max_count = max(min_count + 1, min(8, int(num_prompts * 0.07)))
        return random.randint(min_count, max_count)

def generate_behavior_metadata(tier: str) -> Dict:
    """Generate behavior metadata appropriate for tier"""
    if tier == "primary":
        return {
            "credibility": round(random.uniform(0.88, 0.95), 2),
            "clarity_score": round(random.uniform(0.80, 0.95), 2),
            "extraction_confidence": round(random.uniform(0.75, 0.95), 2),
            "decay_rate": round(random.uniform(0.01, 0.015), 3)  # Low decay
        }
    elif tier == "secondary":
        return {
            "credibility": round(random.uniform(0.70, 0.88), 2),
            "clarity_score": round(random.uniform(0.70, 0.85), 2),
            "extraction_confidence": round(random.uniform(0.65, 0.85), 2),
            "decay_rate": round(random.uniform(0.015, 0.022), 3)  # Medium decay
        }
    else:  # noise
        return {
            "credibility": round(random.uniform(0.45, 0.70), 2),
            "clarity_score": round(random.uniform(0.55, 0.75), 2),
            "extraction_confidence": round(random.uniform(0.50, 0.75), 2),
            "decay_rate": round(random.uniform(0.020, 0.030), 3)  # High decay
        }

def generate_dataset(
    num_prompts: int,
    user_id: str,
    session_id: str,
    profile_type: str = "balanced",
    num_behaviors: int = None
) -> Tuple[List[Dict], List[Dict]]:
    """
    Generate realistic dataset with configurable behavior profiles
    
    Args:
        num_prompts: Total number of prompts to generate
        user_id: User identifier
        session_id: Session identifier
        profile_type: Type of behavior profile (balanced, focused, exploratory, noisy)
        num_behaviors: Number of distinct behaviors (None = use all)
    """
    prompts = []
    behaviors: Dict[str, Dict] = {}
    base_time = int(time.time()) - 86400 * 60  # 60-day history
    
    # Select behaviors
    available_behaviors = list(BEHAVIOR_LIBRARY.keys())
    if num_behaviors:
        num_behaviors = min(num_behaviors, len(available_behaviors))
        available_behaviors = random.sample(available_behaviors, num_behaviors)
    else:
        num_behaviors = len(available_behaviors)
    
    # Calculate target distribution
    distribution = calculate_target_profile(num_behaviors, profile_type)
    print(f"\n📊 Target Profile: {profile_type.upper()}")
    print(f"  PRIMARY: {distribution['primary']} behaviors")
    print(f"  SECONDARY: {distribution['secondary']} behaviors")
    print(f"  NOISE: {distribution['noise']} behaviors")
    
    # Assign tiers to behaviors
    random.shuffle(available_behaviors)
    behavior_tiers = {}
    idx = 0
    
    for tier in ["primary", "secondary", "noise"]:
        count = distribution[tier]
        for _ in range(count):
            if idx < len(available_behaviors):
                behavior_tiers[available_behaviors[idx]] = tier
                idx += 1
    
    # Calculate reinforcement targets
    behavior_targets = {}
    for behavior_text, tier in behavior_tiers.items():
        behavior_targets[behavior_text] = calculate_reinforcement_target(tier, num_prompts)
    
    # Build prompt schedule
    prompt_schedule = []
    for behavior_text, target_count in behavior_targets.items():
        prompt_schedule.extend([behavior_text] * target_count)
    
    # Fill remaining prompts with random behaviors
    remaining = num_prompts - len(prompt_schedule)
    if remaining > 0:
        prompt_schedule.extend(
            random.choices(list(behavior_tiers.keys()), k=remaining)
        )
    
    # Shuffle to randomize order
    random.shuffle(prompt_schedule)
    prompt_schedule = prompt_schedule[:num_prompts]  # Trim to exact count
    
    # Generate prompts
    for i, behavior_text in enumerate(prompt_schedule):
        prompt_text = random.choice(BEHAVIOR_LIBRARY[behavior_text])
        prompt_id = generate_id("prompt")
        
        # Add time variance with temporal clustering
        if i > 0 and random.random() < 0.3:
            timestamp = prompts[-1]["timestamp"] + random.randint(60, 3600)
        else:
            timestamp = base_time + random.randint(0, 86400 * 60)

        prompt = {
            "prompt_id": prompt_id,
            "prompt_text": prompt_text,
            "timestamp": timestamp,
            "tokens": estimate_tokens(prompt_text),
            "user_id": user_id,
            "session_id": session_id
        }

        # Initialize behavior if first occurrence
        if behavior_text not in behaviors:
            tier = behavior_tiers.get(behavior_text, "noise")
            metadata = generate_behavior_metadata(tier)
            
            behaviors[behavior_text] = {
                "behavior_id": generate_id("beh"),
                "behavior_text": behavior_text,
                "credibility": metadata["credibility"],
                "reinforcement_count": 0,
                "decay_rate": metadata["decay_rate"],
                "created_at": timestamp,
                "last_seen": timestamp,
                "prompt_history_ids": [],
                "clarity_score": metadata["clarity_score"],
                "extraction_confidence": metadata["extraction_confidence"],
                "user_id": user_id,
                "session_id": session_id,
                "_tier": tier  # Internal marker for verification
            }

        behavior = behaviors[behavior_text]
        behavior["prompt_history_ids"].append(prompt_id)
        behavior["reinforcement_count"] += 1
        behavior["last_seen"] = max(behavior["last_seen"], timestamp)
        
        prompts.append(prompt)

    return sorted(prompts, key=lambda x: x["timestamp"]), list(behaviors.values())

def clean_behaviors_for_export(behaviors: List[Dict]) -> List[Dict]:
    """Remove internal fields before export"""
    cleaned = []
    for b in behaviors:
        b_clean = {k: v for k, v in b.items() if not k.startswith("_")}
        cleaned.append(b_clean)
    return cleaned

# ------------------ Save to Local Directory ------------------

def save_to_local(data: List[Dict], filename: str):
    import os
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    full_path = os.path.join(OUTPUT_DIR, filename)
    with open(full_path, "w") as f:
        json.dump(data, f, indent=2)

    print(f"✓ Saved {len(data)} records → {full_path}")

def calculate_expected_scores(behaviors: List[Dict], include_tiers: bool = True) -> Dict:
    """Calculate expected BW and ABW for verification"""
    import math
    
    alpha, beta, gamma = 0.35, 0.40, 0.25
    reinforcement_multiplier = 0.01
    current_time = int(time.time())
    
    scored_behaviors = []
    
    for b in behaviors:
        # Calculate BW
        bw = (
            math.pow(b["credibility"], alpha) *
            math.pow(b["clarity_score"], beta) *
            math.pow(b["extraction_confidence"], gamma)
        )
        
        # Calculate ABW
        days_since = (current_time - b["last_seen"]) / 86400
        reinforcement_factor = 1 + (b["reinforcement_count"] * reinforcement_multiplier)
        decay_factor = math.exp(-b["decay_rate"] * days_since)
        abw = bw * reinforcement_factor * decay_factor
        
        # Determine actual tier based on ABW
        actual_tier = "noise"
        if abw >= 1.0:
            actual_tier = "primary"
        elif abw >= 0.7:
            actual_tier = "secondary"
        
        scored_behaviors.append({
            "behavior_text": b["behavior_text"],
            "target_tier": b.get("_tier", "unknown") if include_tiers else None,
            "actual_tier": actual_tier,
            "reinforcement_count": b["reinforcement_count"],
            "credibility": b["credibility"],
            "bw": round(bw, 4),
            "abw": round(abw, 4)
        })
    
    return scored_behaviors

def print_statistics(prompts: List[Dict], behaviors: List[Dict], show_targets: bool = True):
    """Print dataset statistics with tier predictions"""
    print("\n" + "="*50)
    print("DATASET STATISTICS")
    print("="*50)
    
    print(f"\nTotal Prompts: {len(prompts)}")
    print(f"Total Behaviors: {len(behaviors)}")
    
    # Calculate scores
    scored = calculate_expected_scores(behaviors, include_tiers=show_targets)
    
    # Group by actual tier based on ABW
    by_actual = {"primary": [], "secondary": [], "noise": []}
    by_target = {"primary": [], "secondary": [], "noise": [], "unknown": []}
    
    for s in scored:
        actual = s["actual_tier"]
        if actual in by_actual:
            by_actual[actual].append(s)
        
        target = s.get("target_tier", "unknown")
        if target in by_target:
            by_target[target].append(s)
    
    if show_targets:
        print(f"\n🎯 Target Distribution (as designed):")
        print(f"  PRIMARY: {len(by_target['primary'])} behaviors")
        print(f"  SECONDARY: {len(by_target['secondary'])} behaviors")
        print(f"  NOISE: {len(by_target['noise'])} behaviors")
    
    print(f"\n📊 Actual Distribution (based on ABW calculation):")
    print(f"  PRIMARY (ABW ≥ 1.0): {len(by_actual['primary'])} behaviors")
    print(f"  SECONDARY (0.7 ≤ ABW < 1.0): {len(by_actual['secondary'])} behaviors")
    print(f"  NOISE (ABW < 0.7): {len(by_actual['noise'])} behaviors")
    
    # Match analysis
    if show_targets:
        matches = sum(1 for s in scored if s.get("target_tier") == s["actual_tier"])
        print(f"\n✓ Target/Actual Match: {matches}/{len(scored)} ({matches*100//len(scored)}%)")
    
    # Detailed behavior breakdown
    print(f"\n📋 Behavior Details (sorted by ABW):")
    for s in sorted(scored, key=lambda x: x["abw"], reverse=True):
        actual_icon = {"primary": "🟢", "secondary": "🟡", "noise": "🔴"}.get(s["actual_tier"], "⚪")
        
        if show_targets:
            target_icon = {"primary": "🟢", "secondary": "🟡", "noise": "🔴"}.get(s.get("target_tier"), "⚪")
            tier_str = f"{target_icon}→{actual_icon}"
        else:
            tier_str = f"{actual_icon}"
        
        print(f"  {tier_str} {s['behavior_text'][:38]:38} | "
              f"Count: {s['reinforcement_count']:3} | "
              f"Cred: {s['credibility']:.2f} | "
              f"BW: {s['bw']:.4f} | "
              f"ABW: {s['abw']:.4f}")
    
    # Time span
    if prompts:
        time_span_days = (prompts[-1]["timestamp"] - prompts[0]["timestamp"]) / 86400
        print(f"\n⏱️  Time Span: {time_span_days:.1f} days")
    
    # Score thresholds reminder
    print(f"\n📏 Thresholds:")
    print(f"  PRIMARY: Cluster CBI ≥ 1.0")
    print(f"  SECONDARY: 0.7 ≤ Cluster CBI < 1.0")
    print(f"  NOISE: Cluster CBI < 0.7")
    print(f"\n💡 Legend: {('🟢→🟢 = Target→Actual match' if show_targets else '🟢 = Primary, 🟡 = Secondary, 🔴 = Noise')}")
    
    print("="*50 + "\n")

# ------------------ Main ------------------

if __name__ == "__main__":
    USER_ID = f"user_{random.randint(100,999)}"
    SESSION_ID = f"session_{random.randint(1000,9999)}"

    print("\n" + "="*60)
    print("CBIE DATASET GENERATOR v2.0")
    print("="*60)

    NUM_PROMPTS = int(input("\nEnter number of prompts to generate: "))
    
    # Warn if prompt count is too low
    if NUM_PROMPTS < 50:
        print(f"\n⚠️  Warning: {NUM_PROMPTS} prompts may be too few for PRIMARY behaviors")
        print("   Recommendation: Use 150+ prompts for best results")
        proceed = input("   Continue anyway? (y/n) [default: y]: ").lower()
        if proceed == 'n':
            print("\n❌ Cancelled. Please restart with more prompts.")
            import sys
            sys.exit(0)
    
    # Profile type selection
    print("\n📊 Profile Types:")
    print("  1. balanced   - Mix of primary (2-3), secondary (3-5), noise")
    print("  2. focused    - Heavily weighted toward 1-2 primary behaviors")
    print("  3. exploratory - Many secondary behaviors, few primary")
    print("  4. noisy      - Mostly noise with few clear patterns")
    
    profile_input = input("\nSelect profile type (1-4) [default: 1]: ").strip()
    profile_map = {"1": "balanced", "2": "focused", "3": "exploratory", "4": "noisy"}
    PROFILE_TYPE = profile_map.get(profile_input, "balanced")
    
    # Ask for number of behaviors
    total_behaviors = len(BEHAVIOR_LIBRARY)
    print(f"\n📚 Total available behaviors: {total_behaviors}")
    num_beh_input = input(f"Number of behaviors to use (5-{total_behaviors}) [default: 12]: ").strip()
    NUM_BEHAVIORS = int(num_beh_input) if num_beh_input else 12

    print(f"\n🎯 Generating dataset...")
    prompts, behaviors = generate_dataset(
        num_prompts=NUM_PROMPTS,
        user_id=USER_ID,
        session_id=SESSION_ID,
        profile_type=PROFILE_TYPE,
        num_behaviors=NUM_BEHAVIORS
    )

    timestamp = int(time.time())

    save_to_local(prompts, f"prompts_{USER_ID}_{timestamp}.json")
    
    # Print statistics BEFORE cleaning (to show _tier info)
    print_statistics(prompts, behaviors, show_targets=True)
    
    # Clean behaviors before saving (removes internal _tier field)
    behaviors_clean = clean_behaviors_for_export(behaviors)
    save_to_local(behaviors_clean, f"behaviors_{USER_ID}_{timestamp}.json")

    print("\n💡 Tip: Run 'python load_data_to_databases.py' to import into MongoDB/Qdrant")
    
    print("\n📄 Sample prompt:")
    print(json.dumps(prompts[0], indent=2))
    print("\n🎯 Sample behavior:")
    print(json.dumps(behaviors_clean[0], indent=2))