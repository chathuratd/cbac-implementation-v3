# CBIE System - Current Implementation Documentation

**Last Updated:** December 19, 2025  
**Version:** Cluster-Centric MVP v1.0

---

## Overview

The CBIE (Core Behavior Identification Engine) system has been fully migrated to a **cluster-centric architecture**. This document describes the current implementation, logic, and data flow.

### Key Principle
**Clusters are the primary entities** - individual observations are grouped semantically, and ALL observations within a cluster are preserved and contribute to scoring. The canonical label is purely for UI display.

---

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                      API Layer (routes.py)                   │
│  /analyze-behaviors-from-storage → cluster_analysis_pipeline │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│           Cluster Analysis Pipeline (NEW)                    │
│  1. Fetch from Qdrant (source of truth)                     │
│  2. Calculate observation metrics                            │
│  3. Perform clustering (HDBSCAN)                             │
│  4. Build BehaviorCluster objects (preserve ALL obs)         │
│  5. Calculate cluster_strength & confidence                  │
│  6. Select canonical_label (UI only)                         │
│  7. Assign tiers based on cluster_strength                   │
│  8. Generate archetype                                       │
│  9. Return CoreBehaviorProfile with behavior_clusters        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────┬──────────────┬──────────────┬───────────────┐
│   MongoDB    │    Qdrant    │ Calculation  │  Clustering   │
│   Service    │   Service    │   Engine     │    Engine     │
└──────────────┴──────────────┴──────────────┴───────────────┘
```

---

## Data Models

### 1. BehaviorObservation (src/models/schemas.py)

A single observation of a behavior - **NOT the primary entity**.

```python
class BehaviorObservation(BaseModel):
    # Identity
    observation_id: str              # Unique identifier
    user_id: str
    session_id: Optional[str]
    
    # Content
    behavior_text: str               # The observed behavior
    embedding: Optional[List[float]] # Vector representation
    
    # Temporal
    timestamp: int                   # When observed (Unix)
    prompt_id: str                   # Which prompt triggered it
    
    # Individual metrics
    credibility: float               # 0.0-1.0
    clarity_score: float             # 0.0-1.0
    extraction_confidence: float     # 0.0-1.0
    decay_rate: float                # Default 0.01
    
    # Calculated (populated during analysis)
    bw: Optional[float]              # Behavior Weight
    abw: Optional[float]             # Adjusted Behavior Weight
```

**Field Migration:**
- Old: `behavior_id` → New: `observation_id`
- Old: `created_at` → New: `timestamp`
- Old: `last_seen` → Removed (single point in time)

---

### 2. BehaviorCluster (src/models/schemas.py)

**THE PRIMARY ENTITY** - represents a semantic group of observations.

```python
class BehaviorCluster(BaseModel):
    # Identity
    cluster_id: str
    user_id: str
    
    # Members (ALL preserved - NEVER discard)
    observations: List[BehaviorObservation]
    cluster_size: int                # len(observations)
    
    # Display
    canonical_label: str             # UI ONLY - highest clarity + closest to centroid
    wording_variations: List[str]    # All unique phrasings
    
    # Scoring (THESE drive tier assignment)
    cluster_strength: float          # log(size+1) * mean(ABW) * recency_factor
    cluster_confidence: float        # consistency * reinforcement * clarity_trend
    
    # Confidence breakdown
    consistency_score: float         # Semantic similarity (0-1)
    reinforcement_score: float       # Multiple evidence (0-1)
    clarity_trend: float            # Improving over time (0-1)
    
    # Temporal
    first_seen: int
    last_seen: int
    all_timestamps: List[int]
    
    # Evidence
    all_prompt_ids: List[str]        # All prompts that triggered observations
    
    # Tier (assigned based on cluster_strength)
    tier: TierEnum                   # PRIMARY / SECONDARY / NOISE
```

---

### 3. CoreBehaviorProfile (src/models/schemas.py)

The analysis result returned to the user.

```python
class CoreBehaviorProfile(BaseModel):
    user_id: str
    generated_at: int
    
    # NEW: Primary data (cluster-centric)
    behavior_clusters: List[BehaviorCluster]
    
    # DEPRECATED: Kept for backward compatibility
    primary_behaviors: List[CanonicalBehavior] = []
    secondary_behaviors: List[CanonicalBehavior] = []
    
    archetype: Optional[str]
    statistics: ProfileStatistics
```

---

## Core Logic

### Cluster Strength Calculation (calculation_engine.py)

**Purpose:** Replace naive ABW averaging with size-aware, recency-weighted scoring.

```python
def calculate_cluster_strength(
    cluster_size: int,
    mean_abw: float,
    timestamps: List[int],
    current_timestamp: int
) -> float:
    """
    Formula: cluster_strength = log(cluster_size + 1) * mean(ABW) * recency_factor
    
    Example:
    - Single observation: log(1+1) * 0.85 * 1.0 = 0.589
    - 4 observations:     log(4+1) * 0.85 * 1.0 = 1.369
    
    This ensures larger clusters get logarithmic boost.
    """
    size_factor = math.log(cluster_size + 1)
    
    # Recency factor (weight recent observations higher)
    latest_timestamp = max(timestamps)
    days_since = (current_timestamp - latest_timestamp) / 86400
    recency_factor = math.exp(-0.01 * days_since)
    
    return size_factor * mean_abw * recency_factor
```

**Why logarithmic?**
- Single observation: log(2) = 0.693
- Two observations: log(3) = 1.099 (58% boost)
- Four observations: log(5) = 1.609 (132% boost)
- Ten observations: log(11) = 2.398 (246% boost)

Prevents linear explosion while rewarding genuine patterns.

---

### Cluster Confidence Calculation (calculation_engine.py)

**Purpose:** Quantify how reliable the cluster is.

```python
def calculate_cluster_confidence(
    intra_cluster_distances: List[float],
    cluster_size: int,
    clarity_scores: List[float]
) -> tuple[float, float, float, float]:
    """
    Returns: (confidence, consistency, reinforcement, clarity_trend)
    
    Confidence = consistency * reinforcement * clarity_trend
    """
    
    # 1. Consistency: How semantically similar are observations?
    mean_distance = np.mean(intra_cluster_distances)
    consistency_score = 1.0 - mean_distance  # Lower distance = higher consistency
    
    # 2. Reinforcement: Multiple observations = stronger signal
    reinforcement_score = math.log(cluster_size + 1) / math.log(11)
    # Size 1 → 0.0, Size 10 → 1.0
    
    # 3. Clarity Trend: Are observations getting clearer over time?
    clarity_trend = np.mean(clarity_scores[-3:])  # Recent clarity
    
    confidence = consistency_score * reinforcement_score * clarity_trend
    
    return confidence, consistency_score, reinforcement_score, clarity_trend
```

---

### Canonical Label Selection (calculation_engine.py)

**Purpose:** Choose the best display label - **DOES NOT affect scoring**.

```python
def select_canonical_label(
    observations: List[BehaviorObservation],
    cluster_centroid: np.ndarray,
    normalized_embeddings: np.ndarray
) -> tuple[str, int]:
    """
    Select based on:
    1. Highest clarity_score
    2. Closest to cluster centroid
    
    Returns: (canonical_label, canonical_index)
    """
    
    scores = []
    for i, obs in enumerate(observations):
        # Distance to centroid (lower is better)
        distance = np.linalg.norm(normalized_embeddings[i] - cluster_centroid)
        
        # Combined score: clarity - distance
        score = obs.clarity_score - distance
        scores.append(score)
    
    canonical_idx = np.argmax(scores)
    return observations[canonical_idx].behavior_text, canonical_idx
```

**Key Point:** This is ONLY for UI. A cluster's strength is calculated from ALL observations, regardless of which one becomes the label.

---

### Tier Assignment (cluster_analysis_pipeline.py)

**Purpose:** Classify clusters by importance.

```python
def _assign_tier_by_strength(cluster_strength: float) -> TierEnum:
    """
    Thresholds:
    - PRIMARY:   cluster_strength >= 1.0
    - SECONDARY: cluster_strength >= 0.7
    - NOISE:     cluster_strength < 0.7
    """
    if cluster_strength >= 1.0:
        return TierEnum.PRIMARY
    elif cluster_strength >= 0.7:
        return TierEnum.SECONDARY
    else:
        return TierEnum.NOISE
```

**Examples:**
- 4 observations, mean ABW=0.85, recent → strength=1.369 → **PRIMARY**
- 2 observations, mean ABW=0.80, recent → strength=0.879 → **SECONDARY**
- 2 observations, mean ABW=0.55, old → strength=0.485 → **NOISE**

---

## Data Flow

### 1. User Analysis Request

```
POST /api/v1/analyze-behaviors-from-storage?user_id=user_102
```

### 2. Pipeline Execution (cluster_analysis_pipeline.py)

```python
async def analyze_behaviors_from_storage(user_id, generate_archetype):
    # Step 1: Fetch from Qdrant (source of truth)
    qdrant_behaviors = qdrant.get_embeddings_by_user(user_id)
    
    # Step 2: Construct BehaviorObservation objects
    observations = _construct_from_qdrant_payload(qdrant_behaviors)
    
    # Step 3: Fetch prompts from MongoDB
    prompts = mongodb.get_prompts_by_user(user_id)
    
    # Step 4: Calculate observation metrics (BW, ABW)
    for obs in observations:
        metrics = calculation_engine.calculate_behavior_metrics(obs)
        obs.bw = metrics['bw']
        obs.abw = metrics['abw']
    
    # Step 5: Perform clustering
    embeddings = [obs.embedding for obs in observations]
    clustering_result = clustering_engine.cluster_behaviors(
        embeddings=embeddings,
        behavior_ids=[obs.observation_id for obs in observations]
    )
    
    # Step 6: Build BehaviorCluster objects
    behavior_clusters = []
    for cluster_id, member_indices in clustering_result['clusters'].items():
        # Get ALL observations in cluster
        cluster_observations = [observations[i] for i in member_indices]
        
        # Calculate cluster metrics
        abw_values = [obs.abw for obs in cluster_observations]
        timestamps = [obs.timestamp for obs in cluster_observations]
        
        cluster_strength = calculation_engine.calculate_cluster_strength(
            cluster_size=len(cluster_observations),
            mean_abw=np.mean(abw_values),
            timestamps=timestamps
        )
        
        confidence, consistency, reinforcement, clarity_trend = \
            calculation_engine.calculate_cluster_confidence(
                intra_cluster_distances=clustering_result['distances'][cluster_id],
                cluster_size=len(cluster_observations),
                clarity_scores=[obs.clarity_score for obs in cluster_observations]
            )
        
        # Select canonical label (UI only)
        canonical_label, _ = calculation_engine.select_canonical_label(
            observations=cluster_observations,
            cluster_centroid=clustering_result['centroids'][cluster_id]
        )
        
        # Create BehaviorCluster
        cluster = BehaviorCluster(
            cluster_id=cluster_id,
            user_id=user_id,
            observations=cluster_observations,  # ALL preserved
            cluster_size=len(cluster_observations),
            canonical_label=canonical_label,
            cluster_strength=cluster_strength,
            cluster_confidence=confidence,
            consistency_score=consistency,
            reinforcement_score=reinforcement,
            clarity_trend=clarity_trend,
            tier=_assign_tier_by_strength(cluster_strength),
            # ... other fields
        )
        
        behavior_clusters.append(cluster)
    
    # Step 7: Generate archetype (optional)
    archetype = await archetype_service.generate_archetype(behavior_clusters)
    
    # Step 8: Create profile
    profile = CoreBehaviorProfile(
        user_id=user_id,
        generated_at=current_timestamp,
        behavior_clusters=behavior_clusters,
        archetype=archetype,
        statistics=statistics
    )
    
    # Step 9: Store in MongoDB
    mongodb.insert_profile(profile)
    
    return profile
```

---

## Database Schema

### MongoDB Collections

#### 1. `behaviors` (BehaviorObservation)
```javascript
{
  "_id": ObjectId,
  "observation_id": "beh_e787b433",
  "user_id": "user_102",
  "behavior_text": "learns by examples",
  "timestamp": 1763764164,
  "prompt_id": "prompt_950a5eb8",
  "credibility": 0.93,
  "clarity_score": 0.88,
  "extraction_confidence": 0.88,
  "decay_rate": 0.012,
  "session_id": "session_4827",
  "bw": 0.898,
  "abw": 0.906
}
```

**Indexes:**
- `observation_id` (unique)
- `user_id`
- `session_id`

#### 2. `prompts` (PromptModel)
```javascript
{
  "_id": ObjectId,
  "prompt_id": "prompt_950a5eb8",
  "user_id": "user_102",
  "prompt_text": "Explain HTTP request lifecycle",
  "timestamp": 1763764100,
  "tokens": 8.5,
  "session_id": "session_4827"
}
```

**Indexes:**
- `prompt_id` (unique)
- `user_id`
- `timestamp`

#### 3. `core_behavior_profiles` (CoreBehaviorProfile)
```javascript
{
  "_id": ObjectId,
  "user_id": "user_102",
  "generated_at": 1766110553,
  "behavior_clusters": [
    {
      "cluster_id": "cluster_2",
      "observations": [/* full BehaviorObservation objects */],
      "cluster_size": 4,
      "canonical_label": "prefers analogies and metaphors",
      "cluster_strength": 0.8421,
      "cluster_confidence": 0.6232,
      "tier": "PRIMARY",
      // ... other fields
    }
  ],
  "archetype": "Visual Learner",
  "statistics": {
    "total_behaviors_analyzed": 10,
    "clusters_formed": 3
  }
}
```

**Indexes:**
- `user_id` (unique)
- `generated_at`

---

### Qdrant Collection: `behavior_embeddings`

**Point Structure:**
```python
{
  "id": "uuid-string",
  "vector": [0.123, -0.456, ...],  # 3072 dimensions (text-embedding-3-large)
  "payload": {
    "behavior_id": "beh_e787b433",    # OLD field name (backward compat)
    "observation_id": "beh_e787b433",  # NEW field name
    "behavior_text": "learns by examples",
    "user_id": "user_102",
    "session_id": "session_4827",
    "credibility": 0.93,
    "clarity_score": 0.88,
    "extraction_confidence": 0.88,
    "timestamp": 1763764164,          # NEW field name
    "created_at": 1763764164,         # OLD field name (backward compat)
    "decay_rate": 0.012,
    "prompt_history_ids": ["prompt_950a5eb8", ...]
  }
}
```

**Why Qdrant is Source of Truth:**
- Has ALL observations with embeddings
- Embeddings are expensive to regenerate
- MongoDB may have partial/stale data due to bulk insert failures

---

## API Endpoints

### POST `/api/v1/analyze-behaviors-from-storage`

**Query Parameters:**
- `user_id`: User identifier (required)

**Response:**
```json
{
  "user_id": "user_102",
  "generated_at": 1766110553,
  "behavior_clusters": [
    {
      "cluster_id": "cluster_2",
      "user_id": "user_102",
      "observations": [
        {
          "observation_id": "beh_e787b433",
          "behavior_text": "prefers analogies and metaphors",
          "credibility": 0.90,
          "clarity_score": 0.88,
          "timestamp": 1763764164,
          "bw": 0.898,
          "abw": 0.906
        },
        // ... 3 more observations
      ],
      "cluster_size": 4,
      "canonical_label": "prefers analogies and metaphors",
      "wording_variations": [
        "prefers analogies and metaphors",
        "uses analogies frequently",
        "likes metaphorical explanations",
        "explains through analogies"
      ],
      "cluster_strength": 0.8421,
      "cluster_confidence": 0.6232,
      "consistency_score": 0.6177,
      "reinforcement_score": 0.6990,
      "clarity_trend": 0.4825,
      "tier": "PRIMARY",
      "first_seen": 1761187755,
      "last_seen": 1765996185,
      "all_timestamps": [1761187755, 1763050370, 1764220583, 1765996185],
      "all_prompt_ids": ["prompt_39ca7051", "prompt_8d4bd5b6", ...]
    },
    // ... more clusters
  ],
  "archetype": "Visual Learner",
  "statistics": {
    "total_behaviors_analyzed": 10,
    "clusters_formed": 3,
    "total_prompts_analyzed": 250,
    "analysis_time_span_days": 59.69
  }
}
```

---

## Configuration

### Settings (src/config.py)

```python
# Formula weights
alpha = 0.35           # Credibility weight
beta = 0.40            # Clarity weight
gamma = 0.25           # Extraction confidence weight

# Clustering parameters
min_cluster_size = 2
min_samples = 1
cluster_selection_epsilon = 0.15

# Tier thresholds
PRIMARY_THRESHOLD = 1.0
SECONDARY_THRESHOLD = 0.7
```

---

## Testing

### Example Test Output (user_102)

```
=== USER user_102 ANALYSIS ===
Total Observations: 10
Clusters Formed: 3

Cluster: cluster_2 | Tier: PRIMARY
  Size: 4 | Strength: 0.8421 | Confidence: 0.6232
  Label: prefers analogies and metaphors
  Observations:
    - prefers analogies and metaphors
    - uses analogies frequently
    - likes metaphorical explanations
    - explains through analogies

Cluster: cluster_0 | Tier: SECONDARY
  Size: 2 | Strength: 0.7783 | Confidence: 0.5124
  Label: theory and concept focused

Cluster: cluster_1 | Tier: NOISE
  Size: 2 | Strength: 0.3958 | Confidence: 0.2456
  Label: avoids technical jargon
```

---

## Key Differences from Old Implementation

| Aspect | Old (Wrong) | New (Cluster-Centric) |
|--------|-------------|----------------------|
| **Primary Entity** | BehaviorModel | BehaviorCluster |
| **Clustering Usage** | Created groups, picked highest ABW, **discarded rest** | Preserves ALL observations |
| **Scoring** | Individual `abw` | `cluster_strength` = log(size) * mean(ABW) * recency |
| **Confidence** | Not calculated | consistency * reinforcement * clarity_trend |
| **Canonical Label** | Used for scoring | **Display ONLY** |
| **Tier Logic** | `abw >= threshold` | `cluster_strength >= threshold` |
| **Size Awareness** | No | Yes (logarithmic boost) |
| **Evidence Tracking** | Single timestamp | All timestamps, all prompts |
| **API Response** | `primary_behaviors[]` | `behavior_clusters[]` |

---

## Migration Notes

### Backward Compatibility

The system handles both old and new data formats:

1. **Qdrant Payloads**: Checks for both `behavior_id` and `observation_id`
2. **Timestamps**: Checks for both `created_at` and `timestamp`
3. **MongoDB**: Old `BehaviorModel` documents still work via fallback logic

### Data Loading

When loading legacy data:
```python
# Old format → New schema mapping
obs = BehaviorObservation(
    observation_id=old_data.get('behavior_id'),
    timestamp=old_data.get('created_at'),
    prompt_id=old_data.get('prompt_history_ids', [None])[0],
    clarity_score=old_data.get('clarity_score', 0.75),
    extraction_confidence=old_data.get('extraction_confidence', 0.80)
)
```

---

## Performance Considerations

### Embedding Storage
- **Dimension**: 3072 (text-embedding-3-large)
- **Storage per observation**: ~12KB
- **1000 observations**: ~12MB in Qdrant

### Clustering
- **Algorithm**: HDBSCAN (O(n log n))
- **Typical time**: <1 second for 1000 observations

### API Response Size
- Each cluster includes ALL observations (full objects)
- 10 observations → ~15KB response
- Consider pagination for large user bases

---

## Next Steps / Future Enhancements

1. **Temporal Evolution**: Track how cluster_strength changes over time
2. **Cross-User Patterns**: Find common clusters across multiple users
3. **Confidence Thresholds**: Filter low-confidence clusters from UI
4. **Embedding Updates**: Re-embed periodically to improve clustering
5. **Archetype Training**: Fine-tune LLM on successful archetype assignments

---

## References

- **CBIE MVP Documentation**: Full calculation logic and parameters
- **CLUSTER_IMPLEMENTATION.md**: Original implementation notes
- **TEST_RESULTS.md**: Test validation results
- **HDBSCAN**: [scikit-learn-contrib/hdbscan](https://github.com/scikit-learn-contrib/hdbscan)
- **Azure OpenAI**: text-embedding-3-large model

---

**Document Version**: 1.0  
**Last Reviewed**: December 19, 2025
