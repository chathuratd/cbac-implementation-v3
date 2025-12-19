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

def add_metadata_variety(behavior: Dict) -> Dict:
    """Add varied metadata to behaviors"""
    
    # Vary behavior credibility growth (internal tracking only)
    behavior["_credibility_growth_rate"] = round(random.uniform(0.03, 0.08), 3)
    
    return behavior

def generate_dataset(
    num_prompts: int,
    user_id: str,
    session_id: str,
    variety_level: str = "high",
    num_behaviors: int = None,
    target_tier: str = "PRIMARY"
) -> Tuple[List[Dict], List[Dict]]:

    prompts = []
    behaviors: Dict[str, Dict] = {}
    base_time = int(time.time()) - 86400 * 60  # 60-day history
    
    # Configure parameters based on target tier
    if target_tier == "PRIMARY":
        # Need CBI ≥ 1.0: high credibility, low decay, recent, high reinforcement
        base_credibility = 0.80  # Start higher
        credibility_increment = 0.015  # Slower growth but more increments
        decay_range = (0.001, 0.005)  # Very low decay
        clarity_range = (0.85, 0.95)  # High clarity
        confidence_range = (0.85, 0.95)  # High confidence
        time_window_days = 14  # Recent activity (last 2 weeks)
        clustering_probability = 0.6  # 60% chance to cluster prompts
    elif target_tier == "SECONDARY":
        # Need 0.7 ≤ CBI < 1.0: moderate values
        base_credibility = 0.60
        credibility_increment = 0.04
        decay_range = (0.005, 0.015)
        clarity_range = (0.70, 0.85)
        confidence_range = (0.70, 0.85)
        time_window_days = 30
        clustering_probability = 0.4
    else:  # NOISE or MIXED
        # Original parameters for variety
        base_credibility = 0.30
        credibility_increment = 0.05
        decay_range = (0.01, 0.025)
        clarity_range = (0.65, 0.95)
        confidence_range = (0.65, 0.95)
        time_window_days = 60
        clustering_probability = 0.3
    
    # Select subset of behaviors if specified
    available_behaviors = list(BEHAVIOR_LIBRARY.keys())
    if num_behaviors and num_behaviors < len(available_behaviors):
        available_behaviors = random.sample(available_behaviors, num_behaviors)
    
    # Determine behavior distribution based on variety level
    if variety_level == "low":
        behavior_weights = [10] + [1] * (len(available_behaviors) - 1)
    elif variety_level == "medium":
        behavior_weights = [3] * len(available_behaviors)
    else:  # high
        behavior_weights = [1] * len(available_behaviors)

    for i in range(num_prompts):
        # Select behavior with weighted distribution
        behavior_text = random.choices(
            available_behaviors,
            weights=behavior_weights
        )[0]
        
        prompt_text = random.choice(BEHAVIOR_LIBRARY[behavior_text])

        prompt_id = generate_id("prompt")
        
        # Adjust time variance based on target tier
        if i > 0 and random.random() < clustering_probability:
            # Cluster prompts close together
            timestamp = prompts[-1]["timestamp"] + random.randint(60, 3600)
        else:
            # Space within time window
            timestamp = base_time + random.randint(
                86400 * (60 - time_window_days), 
                86400 * 60
            )

        prompt = {
            "prompt_id": prompt_id,
            "prompt_text": prompt_text,
            "timestamp": timestamp,
            "tokens": estimate_tokens(prompt_text),
            "user_id": user_id,
            "session_id": session_id
        }

        if behavior_text not in behaviors:
            behaviors[behavior_text] = {
                "behavior_id": generate_id("beh"),
                "behavior_text": behavior_text,
                "credibility": base_credibility,
                "reinforcement_count": 0,
                "decay_rate": round(random.uniform(*decay_range), 4),
                "created_at": timestamp,
                "last_seen": timestamp,
                "prompt_history_ids": [],
                "clarity_score": round(random.uniform(*clarity_range), 2),
                "extraction_confidence": round(random.uniform(*confidence_range), 2),
                "user_id": user_id,
                "session_id": session_id
            }

        behavior = behaviors[behavior_text]
        
        # Add metadata variety (internal use)
        behavior = add_metadata_variety(behavior)
        
        behavior["prompt_history_ids"].append(prompt_id)
        behavior["reinforcement_count"] += 1
        behavior["last_seen"] = max(behavior["last_seen"], timestamp)
        
        # Use configured credibility increment
        behavior["credibility"] = round(
            min(0.98, behavior["credibility"] + credibility_increment), 
            2
        )
        
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

def print_statistics(prompts: List[Dict], behaviors: List[Dict]):
    """Print dataset statistics"""
    print("\n" + "="*50)
    print("DATASET STATISTICS")
    print("="*50)
    
    print(f"\nTotal Prompts: {len(prompts)}")
    print(f"Total Behaviors: {len(behaviors)}")
    
    # Behavior frequency
    print(f"\nBehavior Distribution:")
    for b in sorted(behaviors, key=lambda x: x["reinforcement_count"], reverse=True):
        print(f"  {b['behavior_text']}: {b['reinforcement_count']} occurrences (credibility: {b['credibility']})")
    
    # Time span
    if prompts:
        time_span_days = (prompts[-1]["timestamp"] - prompts[0]["timestamp"]) / 86400
        print(f"\nTime Span: {time_span_days:.1f} days")
    
    print("="*50 + "\n")

# ------------------ Main ------------------

if __name__ == "__main__":
    USER_ID = f"user_{random.randint(100,999)}"
    SESSION_ID = f"session_{random.randint(1000,9999)}"

    NUM_PROMPTS = int(input("Enter number of prompts to generate: "))
    VARIETY = input("Variety level (low/medium/high) [default: high]: ").lower() or "high"
    
    # Ask for target tier
    print("\nTarget Tier:")
    print("  PRIMARY   - CBI ≥ 1.0 (high credibility, recent, low decay)")
    print("  SECONDARY - 0.7 ≤ CBI < 1.0 (moderate values)")
    print("  MIXED     - Mix of all tiers (original behavior)")
    TARGET_TIER = input("Select tier (PRIMARY/SECONDARY/MIXED) [default: PRIMARY]: ").upper() or "PRIMARY"
    
    # Ask for number of behaviors
    total_behaviors = len(BEHAVIOR_LIBRARY)
    print(f"\nTotal available behaviors: {total_behaviors}")
    num_beh_input = input(f"Number of behaviors to use (1-{total_behaviors}) [default: all]: ").strip()
    NUM_BEHAVIORS = int(num_beh_input) if num_beh_input else None

    prompts, behaviors = generate_dataset(
        num_prompts=NUM_PROMPTS,
        user_id=USER_ID,
        session_id=SESSION_ID,
        variety_level=VARIETY,
        num_behaviors=NUM_BEHAVIORS,
        target_tier=TARGET_TIER
    )

    timestamp = int(time.time())

    save_to_local(prompts, f"prompts_{USER_ID}_{timestamp}.json")
    
    # Clean behaviors before saving
    behaviors_clean = clean_behaviors_for_export(behaviors)
    save_to_local(behaviors_clean, f"behaviors_{USER_ID}_{timestamp}.json")

    print_statistics(prompts, behaviors_clean)

    print("\nSample prompt:")
    print(json.dumps(prompts[0], indent=2))
    print("\nSample behavior:")
    print(json.dumps(behaviors_clean[0], indent=2))