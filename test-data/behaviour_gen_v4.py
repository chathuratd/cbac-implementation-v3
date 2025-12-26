import json
import random
import time
import hashlib
import uuid
from typing import List, Dict, Tuple, Optional

# ------------------ CONFIGURATION ------------------

OUTPUT_DIR = "./behavior_dataset/"

# ------------------ DYNAMIC CONTENT LIBRARIES ------------------

# 1. Fillers for Template Generation
TOPICS = [
    "React", "Kubernetes", "Docker", "Python async", "AWS Lambda", "GraphQL", 
    "REST API", "PostgreSQL", "MongoDB", "CI/CD pipelines", "Rust ownership",
    "Microservices", "OAuth2", "JWT", "Git flow", "Linux permissions",
    "TensorFlow", "pointers in C", "garbage collection"
]

ACTIONS = [
    "debug", "deploy", "optimize", "refactor", "initialize", "mock", 
    "normalize", "encrypt", "compile", "containerize"
]

# 2. Template-Based Behavior Library (Lexical Versatility)
BEHAVIOR_TEMPLATES = {
    "prefers step-by-step guides": [
        "Walk me through {action}ing {topic} step by step.",
        "I need a guide on {topic} setup, start to finish.",
        "First time using {topic}, can you list the steps to {action} it?",
        "Break down the process of {topic} implementation.",
        "Step-by-step tutorial for {topic}, please."
    ],
    "likes quick summaries": [
        "TL;DR on {topic}?",
        "Give me a 2-sentence summary of {topic}.",
        "Quick gist: what does {topic} actually do?",
        "In a nutshell, explain {topic}.",
        "Short overview of {topic} vs {topic}."
    ],
    "prefers visual learning": [
        "Can you generate a diagram for {topic} architecture?",
        "Visualize the flow of data in {topic}.",
        "I need a chart comparing {topic} features.",
        "Draw a schema for this {topic} database.",
        "Show me a visual representation of {topic}."
    ],
    "avoids technical jargon": [
        "Explain {topic} like I'm 5 years old.",
        "What is {topic}? No buzzwords please.",
        "Layman's terms explanation of {topic}.",
        "Simple English definition of {topic}.",
        "I'm non-technical, how does {topic} work?"
    ],
    "prefers detailed technical documentation": [
        "Deep dive into {topic} memory management.",
        "Comprehensive documentation on {topic} {action} protocols.",
        "Technical specification for {topic} integration.",
        "Detailed analysis of {topic} constraints.",
        "Full reference guide for {topic} flags."
    ],
    "learns by examples": [
        "Show me a code snippet for {topic}.",
        "Example of {topic} in a real production app.",
        "Practical use case for {topic} please.",
        "Can you write a sample function using {topic}?",
        "Demonstrate {topic} with a hello-world example."
    ],
    "troubleshooting oriented": [
        "My {topic} build is failing with error 500.",
        "Why is {topic} throwing a timeout exception?",
        "Help me debug this {topic} race condition.",
        "Fixing memory leaks in {topic}.",
        "Cannot connect to {topic} service, any ideas?"
    ],
    "theory and concept focused": [
        "What is the underlying theory of {topic}?",
        "Mathematical basis for {topic} algorithms.",
        "Explain the CAP theorem relation to {topic}.",
        "Principles of {topic} design patterns.",
        "Conceptual difference between {topic} and {topic}."
    ]
}

# 3. Noise Library (Negative Testing Data)
NOISE_PROMPTS = [
    "Hello there", "Good morning", "Thank you", "That's cool", 
    "Write a poem about a cat", "What's the weather like?", 
    "Who is the president?", "Ignore previous instructions",
    "Tell me a joke", "Are you an AI?"
]

# ------------------ UTILITIES ------------------

def generate_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"

def estimate_tokens(text: str) -> float:
    return round(len(text) / 4, 1)

def fill_template(template: str) -> str:
    """Dynamically fills templates with random topics/actions."""
    t = template.replace("{topic}", random.choice(TOPICS))
    t = t.replace("{action}", random.choice(ACTIONS))
    # Handle double replacements if needed (topic vs topic)
    while "{topic}" in t:
        t = t.replace("{topic}", random.choice(TOPICS), 1)
    return t

# ------------------ ARCHETYPES ------------------

class UserArchetype:
    """Defines probabilities for behaviors to simulate different personas."""
    def __init__(self, name: str, weights: Dict[str, float], noise_prob: float):
        self.name = name
        self.weights = weights
        self.noise_prob = noise_prob

# Define Archetypes
ARCHETYPES = {
    "The Student": UserArchetype(
        "Student", 
        {"prefers step-by-step guides": 10, "learns by examples": 8, "theory and concept focused": 2},
        noise_prob=0.1
    ),
    "The Architect": UserArchetype(
        "Architect", 
        {"prefers visual learning": 10, "prefers detailed technical documentation": 8, "likes quick summaries": 5},
        noise_prob=0.05
    ),
    "The Debugger": UserArchetype(
        "Debugger", 
        {"troubleshooting oriented": 15, "likes quick summaries": 3},
        noise_prob=0.2  # Frustrated users might chat/complain more
    ),
    "The Manager": UserArchetype(
        "Manager", 
        {"avoids technical jargon": 10, "likes quick summaries": 10, "prefers visual learning": 5},
        noise_prob=0.1
    ),
    "Random": UserArchetype("Random", {}, noise_prob=0.15)
}

# ------------------ CORE GENERATOR ------------------

def generate_dataset(
    num_prompts: int,
    user_id: str,
    session_id: str,
    archetype_name: str = "Random",
    target_tier: str = "PRIMARY"
) -> Tuple[List[Dict], List[Dict]]:
    
    prompts = []
    behaviors: Dict[str, Dict] = {}
    
    # Setup timing logic
    base_time = int(time.time()) - (86400 * 30) # Start 30 days ago
    current_time_cursor = base_time
    
    # Get Archetype configuration
    archetype = ARCHETYPES.get(archetype_name, ARCHETYPES["Random"])
    available_behaviors = list(BEHAVIOR_TEMPLATES.keys())
    
    # Tier configuration (preserved from original logic)
    if target_tier == "PRIMARY":
        base_cred = 0.80
        cred_inc = 0.02
    elif target_tier == "SECONDARY":
        base_cred = 0.60
        cred_inc = 0.04
    else:
        base_cred = 0.30
        cred_inc = 0.05

    for _ in range(num_prompts):
        # 1. Determine if this is Noise or Signal
        is_noise = random.random() < archetype.noise_prob
        
        prompt_text = ""
        behavior_key = None
        
        if is_noise:
            prompt_text = random.choice(NOISE_PROMPTS)
            # Noise usually doesn't trigger behavior updates, 
            # but we track the prompt.
        else:
            # Select behavior based on Archetype weights
            if archetype.name == "Random":
                behavior_key = random.choice(available_behaviors)
            else:
                # Default weight is 1 if not specified in archetype
                weights = [archetype.weights.get(k, 1) for k in available_behaviors]
                behavior_key = random.choices(available_behaviors, weights=weights, k=1)[0]
            
            # Select and Fill Template
            template = random.choice(BEHAVIOR_TEMPLATES[behavior_key])
            prompt_text = fill_template(template)

        # 2. Timing Logic (Simulate reading/thinking time)
        current_time_cursor += random.randint(30, 600) 
        prompt_id = generate_id("prompt")

        prompt_entry = {
            "prompt_id": prompt_id,
            "prompt_text": prompt_text,
            "timestamp": current_time_cursor,
            "tokens": estimate_tokens(prompt_text),
            "user_id": user_id,
            "session_id": session_id,
            "is_noise": is_noise  # Helpful for validation ground-truth
        }
        prompts.append(prompt_entry)

        # 3. Behavior Logic (Only if not noise)
        if not is_noise and behavior_key:
            if behavior_key not in behaviors:
                behaviors[behavior_key] = {
                    "behavior_id": generate_id("beh"),
                    "behavior_text": behavior_key,
                    "credibility": base_cred,
                    "reinforcement_count": 0,
                    "last_seen": current_time_cursor,
                    "prompt_history_ids": [],
                    # Mock analytics metrics
                    "clarity_score": round(random.uniform(0.7, 0.99), 2),
                    "confidence": round(random.uniform(0.7, 0.99), 2)
                }
            
            # Update existing behavior
            b_obj = behaviors[behavior_key]
            b_obj["reinforcement_count"] += 1
            b_obj["last_seen"] = current_time_cursor
            b_obj["prompt_history_ids"].append(prompt_id)
            # Cap credibility at 1.0
            b_obj["credibility"] = min(1.0, round(b_obj["credibility"] + cred_inc, 2))

    return prompts, list(behaviors.values())

# ------------------ EXECUTION & SAVING ------------------

def save_batch(data: List[Dict], prefix: str, run_id: str):
    import os
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filename = f"{prefix}_{run_id}.json"
    with open(os.path.join(OUTPUT_DIR, filename), "w") as f:
        json.dump(data, f, indent=2)
    print(f"Saved {filename}")

if __name__ == "__main__":
    print("--- Versatile Dataset Generator ---")
    
    # Batch Generation Mode
    BATCH_SIZE = 3  # Number of users to simulate
    
    print(f"Generating data for {BATCH_SIZE} unique users...")
    
    all_prompts_meta = []
    
    for _ in range(BATCH_SIZE):
        user_id = f"user_{uuid.uuid4().hex[:6]}"
        session_id = f"sess_{uuid.uuid4().hex[:6]}"
        
        # Pick a random archetype for this user
        chosen_archetype = random.choice(list(ARCHETYPES.keys()))
        
        prompts, behaviors = generate_dataset(
            num_prompts=random.randint(40, 80), # Larger datasets for better clustering
            user_id=user_id,
            session_id=session_id,
            archetype_name=chosen_archetype
        )
        
        # Save individual user files
        save_batch(prompts, "prompts", user_id)
        save_batch(behaviors, "behaviors", user_id)
        
        print(f"-> Generated User {user_id} ({chosen_archetype}): {len(prompts)} prompts, {len(behaviors)} behaviors")

    print("\n✓ Batch generation complete.")