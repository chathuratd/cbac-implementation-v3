# Behaviors, Clusters, and Archetypes - System Overview

## 📖 Table of Contents
1. [Core Concepts](#core-concepts)
2. [Behaviors vs Clusters](#behaviors-vs-clusters)
3. [Clusters vs Core Behaviors](#clusters-vs-core-behaviors)
4. [Archetype Generation](#archetype-generation)
5. [Complete Processing Flow](#complete-processing-flow)
6. [Real-World Example](#real-world-example)
7. [UI Display Logic](#ui-display-logic)

---

## 🎯 Core Concepts

### Three Fundamental Components

```
BEHAVIORS → CLUSTERS → ARCHETYPE
(Individual)  (Patterns)  (Identity)
```

| Component | Definition | Count | Example |
|-----------|------------|-------|---------|
| **Behavior** | Single detected behavioral trait from one interaction | 10-50+ | "Prefers step-by-step explanations" |
| **Cluster** | Group of similar behaviors forming a pattern | 2-8 | "Sequential Learning Preference" (contains 5 behaviors) |
| **Archetype** | User's synthesized behavioral identity | 1 | "Practical Visual Experimenter" |

---

## 🔍 Behaviors vs Clusters

### What Are Behaviors?

**Behaviors** are individual behavioral observations detected from user interactions.

```python
# Each prompt interaction can generate 1-3 behaviors
Prompt 1: "Can you explain step by step?"
  → Behavior Detected: "Requests sequential instruction"

Prompt 2: "Walk me through this process"
  → Behavior Detected: "Prefers guided learning approach"

Prompt 3: "Show me a visual diagram"
  → Behavior Detected: "Visual learning preference"

Prompt 4: "Break this down for me"
  → Behavior Detected: "Seeks structured breakdown"

Prompt 5: "Can you visualize this?"
  → Behavior Detected: "Prefers graphical explanations"
```

**Key Characteristics:**
- ✅ Raw, unprocessed observations
- ✅ One behavior = one detection event
- ✅ Stored in MongoDB with embeddings in Qdrant
- ✅ Total count = all detected behaviors

### What Are Clusters?

**Clusters** are groups of similar behaviors that form coherent behavioral patterns.

```python
# Same 5 behaviors from above, now clustered:

15 Individual Behaviors
       ↓
[HDBSCAN Clustering Algorithm]
       ↓
3 Distinct Clusters Formed

Cluster 1: "Sequential Learning Preference"
├─ "Requests sequential instruction"
├─ "Prefers guided learning approach"
└─ "Seeks structured breakdown"
(3 behaviors, 53% strength, 85% confidence)

Cluster 2: "Visual Learning Style"
├─ "Visual learning preference"
└─ "Prefers graphical explanations"
(2 behaviors, 47% strength, 78% confidence)

Cluster 3: "Code-First Approach"
├─ "Prefers working examples"
├─ "Requests executable code"
└─ "Focuses on implementation"
(3 behaviors, 42% strength, 65% confidence)
```

**Key Characteristics:**
- ✅ Processed, grouped patterns
- ✅ One cluster = multiple similar behaviors
- ✅ Measured by strength (cluster size %) and confidence (quality %)
- ✅ Total count = number of distinct patterns

### The Relationship

```
Many Behaviors → Few Clusters

Example:
15 behaviors → 3 clusters
20 behaviors → 4 clusters
50 behaviors → 6 clusters
```

**Visual Representation:**

```
BEHAVIORS (Individual Detections)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔵 "explain step by step"
🔵 "walk me through"
🔵 "break it down"
🔴 "show diagram"
🔴 "visualize this"
🟢 "give me code"
🟢 "working example"
🔵 "sequential steps"
       ↓
CLUSTERS (Grouped Patterns)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔵 Cluster A: Sequential Learning (3 behaviors)
🔴 Cluster B: Visual Preference (2 behaviors)
🟢 Cluster C: Code-First Style (2 behaviors)
```

---

## 🎖️ Clusters vs Core Behaviors

### Not All Clusters Are Core Behaviors!

After clustering, each cluster is assigned a **tier** based on its strength and confidence:

```python
# Tier Assignment Logic (from clustering_service.py)

def _assign_tier(strength: float, confidence: float) -> TierEnum:
    """
    Assign tier based on strength and confidence thresholds
    
    Thresholds:
    - PRIMARY: ≥60% strength AND ≥75% confidence
    - SECONDARY: ≥40% strength AND ≥60% confidence
    - NOISE: Below thresholds
    """
    if strength >= 60.0 and confidence >= 0.75:
        return TierEnum.PRIMARY
    elif strength >= 40.0 and confidence >= 0.60:
        return TierEnum.SECONDARY
    else:
        return TierEnum.NOISE
```

### The Three Tiers

| Tier | Criteria | Meaning | Is Core Behavior? |
|------|----------|---------|-------------------|
| **PRIMARY** | ≥60% strength, ≥75% confidence | Dominant, consistent patterns | ✅ **YES** |
| **SECONDARY** | ≥40% strength, ≥60% confidence | Supporting, moderate patterns | ⚠️ **Supportive** |
| **NOISE** | Below thresholds | Weak, inconsistent patterns | ❌ **NO** |

### Example Scenario

```
User Profile Analysis Result:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Behaviors: 25
Total Clusters: 6

Cluster Breakdown:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ PRIMARY (Core Behaviors):
   Cluster A: "Sequential Problem Solving"
   - Strength: 68%
   - Confidence: 85%
   - Behaviors: 8

   Cluster B: "Visual Learning Preference"
   - Strength: 62%
   - Confidence: 78%
   - Behaviors: 7

⚠️ SECONDARY (Supporting Behaviors):
   Cluster C: "Code Documentation Interest"
   - Strength: 48%
   - Confidence: 65%
   - Behaviors: 5

   Cluster D: "Collaborative Learning"
   - Strength: 42%
   - Confidence: 62%
   - Behaviors: 3

❌ NOISE (Discarded):
   Cluster E: "Random Pattern 1"
   - Strength: 25%
   - Confidence: 45%
   - Behaviors: 1

   Cluster F: "Random Pattern 2"
   - Strength: 18%
   - Confidence: 38%
   - Behaviors: 1

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Summary:
- 6 clusters detected
- 2 are core behaviors (PRIMARY)
- 4 are not core behaviors (2 SECONDARY, 2 NOISE)
```

### Core Behavior Definition

```
Core Behavior = PRIMARY Tier Cluster

A cluster is considered a "core behavior" when:
1. It represents ≥60% of user's behavioral data (strong)
2. The clustering quality is ≥75% confident (reliable)
3. It's dominant enough to define the user's identity
```

---

## 👤 Archetype Generation

### How Archetype Is Created

**Archetype** = A concise label that captures the user's behavioral identity, generated from **PRIMARY clusters only**.

### The Process

**File:** `src/services/archetype_service.py`

```python
async def generate_archetype(user_id: str) -> str:
    """
    Generate archetype name from user's PRIMARY clusters
    
    Steps:
    1. Retrieve all clusters for user
    2. Filter to PRIMARY tier only (core behaviors)
    3. Extract canonical labels from PRIMARY clusters
    4. Send to LLM to synthesize concise archetype name
    5. Store and return archetype
    """
    
    # Step 1 & 2: Get PRIMARY clusters
    clusters = await get_user_clusters(user_id)
    primary_clusters = [
        c for c in clusters 
        if c.tier == TierEnum.PRIMARY
    ]
    
    if not primary_clusters:
        return "Undefined Archetype"
    
    # Step 3: Extract canonical labels
    behavior_descriptions = [
        f"- {cluster.canonical_label} (strength: {cluster.strength}%, confidence: {cluster.confidence}%)"
        for cluster in primary_clusters
    ]
    
    # Step 4: LLM synthesis
    prompt = f"""
    Based on these core behavioral patterns:
    {chr(10).join(behavior_descriptions)}
    
    Create a concise archetype name (3-5 words) that captures the essence of this user's learning/interaction style.
    
    Guidelines:
    - Focus on the dominant patterns
    - Use descriptive, professional language
    - Emphasize the unique combination
    - Keep it memorable and specific
    
    Return only the archetype name.
    """
    
    archetype = await llm_service.generate(prompt)
    
    # Step 5: Store
    await mongodb_service.update_user_profile(
        user_id=user_id,
        archetype=archetype
    )
    
    return archetype
```

### Example Synthesis

```python
Input (PRIMARY Clusters):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- "Prefers step-by-step, sequential instruction format"
  (strength: 68%, confidence: 85%)
  
- "Strong visual learning preference with diagrams"
  (strength: 62%, confidence: 78%)
  
- "Hands-on experimentation over theoretical reading"
  (strength: 59%, confidence: 76%)

LLM Processing:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"The user exhibits strong sequential learning, visual processing, 
and practical experimentation tendencies. They learn best through 
structured, visual, hands-on experiences."

Output (Archetype):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"Practical Visual Experimenter"
```

### Why Only PRIMARY Clusters?

```
SECONDARY and NOISE clusters are excluded because:

✅ PRIMARY = Defining characteristics
   → Strong, consistent, reliable
   → Essential to user identity
   
⚠️ SECONDARY = Contextual modifiers
   → Moderate, situational
   → Not defining traits
   
❌ NOISE = Random variations
   → Weak, unreliable
   → Not real patterns
```

**Analogy:**
```
If you're describing a person:

PRIMARY clusters = "Athletic, intellectual, creative"
  → Archetype: "Creative Athletic Scholar"

SECONDARY clusters = "Sometimes likes cooking, occasionally plays guitar"
  → Not included in core identity

NOISE = "Once tried knitting, mentioned yoga in 2019"
  → Definitely not included
```

---

## 🔄 Complete Processing Flow

### End-to-End Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: BEHAVIOR DETECTION                                  │
├─────────────────────────────────────────────────────────────┤
│ User Interaction → LLM Analysis → Behavior Extraction       │
│                                                              │
│ Input:  "Can you explain this step by step?"                │
│ Output: Behavior: "Prefers sequential instruction"          │
│                                                              │
│ Result: 25 individual behaviors detected over time          │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 2: EMBEDDING GENERATION                                │
├─────────────────────────────────────────────────────────────┤
│ Each behavior → OpenAI Embedding (1536 dimensions)          │
│                                                              │
│ Behavior text → Vector representation                        │
│ Stored in: Qdrant vector database                           │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 3: CLUSTERING (HDBSCAN)                                │
├─────────────────────────────────────────────────────────────┤
│ 25 behavior vectors → HDBSCAN algorithm → 6 clusters        │
│                                                              │
│ Algorithm analyzes:                                          │
│ - Semantic similarity (cosine distance)                      │
│ - Density-based grouping                                     │
│ - Hierarchical structure                                     │
│                                                              │
│ Result: 25 behaviors grouped into 6 distinct patterns       │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 4: STRENGTH & CONFIDENCE CALCULATION                   │
├─────────────────────────────────────────────────────────────┤
│ For each cluster:                                            │
│                                                              │
│ Strength = (cluster_size / total_behaviors) × 100           │
│ Confidence = (HDBSCAN_prob × 0.6) + (Silhouette × 0.4)     │
│                                                              │
│ Example:                                                     │
│ Cluster A: 8 behaviors / 25 total = 32% strength            │
│            HDBSCAN: 0.85, Silhouette: 0.72                  │
│            Confidence: (0.85×0.6) + (0.72×0.4) = 79.8%     │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 5: TIER ASSIGNMENT                                     │
├─────────────────────────────────────────────────────────────┤
│ Apply thresholds to classify clusters:                      │
│                                                              │
│ Cluster A: 68% strength, 85% confidence → PRIMARY ✅         │
│ Cluster B: 62% strength, 78% confidence → PRIMARY ✅         │
│ Cluster C: 48% strength, 65% confidence → SECONDARY ⚠️      │
│ Cluster D: 42% strength, 62% confidence → SECONDARY ⚠️      │
│ Cluster E: 25% strength, 45% confidence → NOISE ❌           │
│ Cluster F: 18% strength, 38% confidence → NOISE ❌           │
│                                                              │
│ Result: 2 PRIMARY, 2 SECONDARY, 2 NOISE                     │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 6: ARCHETYPE GENERATION                                │
├─────────────────────────────────────────────────────────────┤
│ Input: Only PRIMARY clusters                                │
│                                                              │
│ Cluster A: "Sequential Problem Solving"                     │
│ Cluster B: "Visual Learning Preference"                     │
│                     ↓                                        │
│              [LLM Synthesis]                                 │
│                     ↓                                        │
│ Output: "Structured Visual Learner"                         │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 7: PROFILE STORAGE                                     │
├─────────────────────────────────────────────────────────────┤
│ MongoDB Document:                                            │
│ {                                                            │
│   "user_id": "user_665390",                                 │
│   "archetype": "Structured Visual Learner",                 │
│   "total_behaviors": 25,                                     │
│   "total_clusters": 6,                                       │
│   "primary_clusters": 2,                                     │
│   "clusters": [...]                                          │
│ }                                                            │
└─────────────────────────────────────────────────────────────┘
```

### Flow Diagram

```
USER INTERACTIONS (Prompts)
           ↓
    [Behavior Detection]
           ↓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   25 Individual Behaviors
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  • Sequential instruction
  • Step-by-step guidance
  • Visual diagrams
  • Code examples
  • ... (21 more)
           ↓
    [Vector Embeddings]
           ↓
  25 × 1536-dim vectors
           ↓
   [HDBSCAN Clustering]
           ↓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
      6 Behavior Clusters
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 Cluster A: 8 behaviors
 Cluster B: 7 behaviors
 Cluster C: 5 behaviors
 Cluster D: 3 behaviors
 Cluster E: 1 behavior
 Cluster F: 1 behavior
           ↓
 [Strength & Confidence]
           ↓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
      Tier Assignment
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 ✅ PRIMARY (2 clusters)
    └─ Core behaviors
 
 ⚠️ SECONDARY (2 clusters)
    └─ Supporting behaviors
 
 ❌ NOISE (2 clusters)
    └─ Ignored
           ↓
  [Archetype Generation]
  (Uses PRIMARY only)
           ↓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"Structured Visual Learner"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 📊 Real-World Example

### User: user_665390

#### Raw Data
```
Behaviors Tracked: 15
Observations (Prompts): 62
Time Period: 2 weeks
```

#### Processing Results

```python
STEP 1: Behavior Detection
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
15 behaviors detected from 62 prompts:
1. "Requests step-by-step explanations"
2. "Prefers sequential instruction format"
3. "Seeks structured breakdowns"
4. "Visual learning preference"
5. "Asks for diagrams and visualizations"
6. "Code-first approach to problems"
7. "Prefers working examples over theory"
8. "Hands-on experimentation style"
9. "Practical implementation focus"
10. "Iterative problem solving"
... (5 more)

STEP 2: Clustering
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HDBSCAN groups 15 behaviors → 2 distinct clusters

Cluster 0:
- Contains behaviors: 1, 2, 3, 10 (and 4 more)
- Pattern: "Sequential, structured learning approach"
- Size: 8 behaviors

Cluster 1:
- Contains behaviors: 4, 5, 6, 7, 8, 9
- Pattern: "Visual, practical, hands-on style"
- Size: 7 behaviors

STEP 3: Metrics Calculation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Cluster 0:
  Strength: (8 / 15) × 100 = 53.3%
  HDBSCAN Probability: 0.88
  Silhouette Score: 0.48 (normalized to 0.74)
  Confidence: (0.88 × 0.6) + (0.74 × 0.4) = 52.8% + 29.6% = 56.6%
  
Cluster 1:
  Strength: (7 / 15) × 100 = 46.7%
  HDBSCAN Probability: 0.82
  Silhouette Score: 0.52 (normalized to 0.76)
  Confidence: (0.82 × 0.6) + (0.76 × 0.4) = 49.2% + 30.4% = 58.6%

STEP 4: Tier Assignment
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Cluster 0: 53.3% strength, 56.6% confidence
  → Does NOT meet PRIMARY (need ≥60% AND ≥75%)
  → Does NOT meet SECONDARY (need ≥40% AND ≥60%)
  → Assigned: NOISE ❌

Cluster 1: 46.7% strength, 58.6% confidence
  → Does NOT meet PRIMARY (need ≥60% AND ≥75%)
  → Does NOT meet SECONDARY (need ≥40% AND ≥60%)
  → Assigned: NOISE ❌

Result: No PRIMARY or SECONDARY clusters!

STEP 5: Archetype Generation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
No PRIMARY clusters found
Fallback archetype: "Emerging Behavioral Profile"

Note: This user needs more data to establish core behaviors.
```

#### Interpretation

```
Why are both clusters NOISE?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Low Strength (<60%):
   - 8/15 and 7/15 are both below 9/15 (60%) threshold
   - Behaviors are split too evenly between patterns
   - No single pattern is dominant

2. Low Confidence (<75% for PRIMARY, <60% for SECONDARY):
   - Silhouette scores indicate clusters aren't well-separated
   - Behaviors have some semantic overlap
   - Clustering quality needs improvement

3. Insufficient Data:
   - 15 behaviors is relatively small sample size
   - Need ~25-50 behaviors for stable patterns
   - Current patterns may shift with more data

Solution: Collect more behavioral data over time
```

---

## 🖥️ UI Display Logic

### Frontend Display (Profile Insights Tab)

```jsx
// ProfileInsights.jsx

const ProfileInsights = ({ userId }) => {
  const [profile, setProfile] = useState(null);
  
  // Display logic
  return (
    <div className="profile-stats">
      {/* Behaviors Count */}
      <StatCard
        label="Behaviors Tracked"
        value={profile.total_behaviors}
        description="Individual behavioral observations"
        icon={<Activity />}
      />
      
      {/* Clusters Count */}
      <StatCard
        label="Clusters Detected"
        value={profile.total_clusters}
        description="Distinct behavioral patterns"
        icon={<Network />}
      />
      
      {/* Archetype */}
      <ArchetypeCard
        archetype={profile.archetype}
        primaryClusters={profile.clusters.filter(c => c.tier === "PRIMARY")}
        description="Based on core behavioral patterns"
      />
    </div>
  );
};
```

### What User Sees

```
┌─────────────────────────────────────────────────────────────┐
│                     PROFILE INSIGHTS                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  📊 Behaviors Tracked: 25                                   │
│     Individual behavioral observations                       │
│                                                              │
│  🔗 Clusters Detected: 6                                    │
│     Distinct behavioral patterns                             │
│                                                              │
│  👤 Archetype: "Structured Visual Learner"                  │
│     Based on 2 core behavioral patterns                      │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│                    CLUSTER BREAKDOWN                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ✅ PRIMARY CLUSTERS (Core Behaviors)                       │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Sequential Problem Solving                             │ │
│  │ Strength: 68% | Confidence: 85%                        │ │
│  │ 8 behaviors                                            │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Visual Learning Preference                             │ │
│  │ Strength: 62% | Confidence: 78%                        │ │
│  │ 7 behaviors                                            │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ⚠️ SECONDARY CLUSTERS (Supporting Behaviors)              │
│  [2 clusters collapsed]                                      │
│                                                              │
│  ❌ NOISE (Not significant)                                 │
│  [2 clusters hidden]                                         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Interpretation Guide for Users

```
┌─────────────────────────────────────────────────────────────┐
│ UNDERSTANDING YOUR PROFILE METRICS                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ Behaviors Tracked (25)                                       │
│ ├─ What: Individual observations from your interactions     │
│ ├─ Example: Each "explain step by step" = 1 behavior       │
│ └─ More = Better profile accuracy                           │
│                                                              │
│ Clusters Detected (6)                                        │
│ ├─ What: Patterns formed from similar behaviors            │
│ ├─ Example: 5 "step-by-step" behaviors = 1 cluster         │
│ └─ Shows your distinct behavioral patterns                  │
│                                                              │
│ Core Behaviors (2 PRIMARY clusters)                          │
│ ├─ What: Your dominant, defining characteristics           │
│ ├─ Criteria: Strong (≥60%) AND Confident (≥75%)            │
│ └─ These define your archetype                              │
│                                                              │
│ Archetype ("Structured Visual Learner")                      │
│ ├─ What: Summary of your behavioral identity               │
│ ├─ Source: Generated from PRIMARY clusters only            │
│ └─ Use: Personalize AI responses to your style             │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎓 Summary

### Key Takeaways

1. **Behaviors ≠ Clusters**
   - Behaviors = Individual observations (many)
   - Clusters = Grouped patterns (few)
   - Relationship: Many → Few

2. **Clusters ≠ Core Behaviors**
   - All Clusters = Any behavioral pattern
   - Core Behaviors = PRIMARY tier only
   - Not all clusters are core behaviors

3. **Archetype = Identity**
   - Generated from PRIMARY clusters
   - Ignores SECONDARY and NOISE
   - Synthesized by LLM into concise name

### Quick Reference

```
HIERARCHY:
User Interactions
  └─ Behaviors (Individual)
      └─ Clusters (Patterns)
          └─ Tiers (Quality)
              ├─ PRIMARY → Core Behaviors
              ├─ SECONDARY → Supporting
              └─ NOISE → Discarded
                  └─ Archetype (Identity)

COUNTS:
50 interactions → 25 behaviors → 6 clusters → 2 PRIMARY → 1 archetype

THRESHOLDS:
PRIMARY:   ≥60% strength AND ≥75% confidence
SECONDARY: ≥40% strength AND ≥60% confidence
NOISE:     Below thresholds
```

### Analogy

```
Think of it like a photo album:

Behaviors = Individual photos (100 photos)
Clusters = Themed albums (5 albums: Travel, Family, Work, etc.)
Tiers = Quality rating (Travel & Family are favorites)
Core Behaviors = Favorite albums only (Travel, Family)
Archetype = Album collection title ("Adventure-Loving Family Person")

The title describes you based on your FAVORITE albums,
not all albums, and definitely not the blurry photos.
```

---

## 📚 Related Documentation

- [Confidence Calculation Explained](./CONFIDENCE_CALCULATION_EXPLAINED.md) - Deep dive into strength and confidence metrics
- [Clustering Implementation](./CLUSTER_IMPLEMENTATION.md) - Technical details of HDBSCAN clustering
- [API Documentation](./API_DOCUMENTATION.md) - How to access profile data via API
- [Frontend Integration](./FRONTEND_INTEGRATION_UPDATE.md) - UI components and display logic

---

**Document Version:** 1.0  
**Last Updated:** December 28, 2025  
**Maintained By:** CBIE Development Team
