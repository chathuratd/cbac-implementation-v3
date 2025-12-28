# Confidence Calculation - Deep Dive

## Overview

This document explains how the **confidence score** is calculated for behavior clusters in the CBIE (Core Behavior Identification Engine) system. Confidence represents how certain we are that a detected pattern is a real, meaningful behavior rather than random noise.

---

## 📊 The Formula

```python
confidence = (hdbscan_probability * 0.6) + (silhouette_score * 0.4)
```

**Two components:**
- **HDBSCAN Probability** (60% weight) - Intra-cluster quality
- **Silhouette Score** (40% weight) - Inter-cluster separation

---

## 🔍 Component 1: HDBSCAN Probability (60% weight)

### What It Measures
**"How strongly does each behavior belong to its assigned cluster?"**

### Where These Values Come From

**Source:** HDBSCAN algorithm's internal calculations

```python
# In clustering_service.py
clusterer = hdbscan.HDBSCAN(
    min_cluster_size=2,
    min_samples=1,
    metric='cosine',
    cluster_selection_method='eom'
)

labels = clusterer.fit_predict(embeddings)
probabilities = clusterer.probabilities_  # ← The source of values like 0.95, 0.88, 0.92
```

### How HDBSCAN Calculates These

HDBSCAN builds a density-based hierarchy and assigns each point a probability based on:

1. **Distance to cluster core** - How close is this behavior to the cluster's dense center?
2. **Local density** - How dense is the cluster at this point's location?
3. **Persistence** - How stable is this assignment across different density thresholds?

### Visual Example

```
Cluster in Vector Space:

      Cluster Core
          ⭐
        🔵 🔵  ← Very close to core
      🔵  🔵 🔵   → Probability: 0.92-0.95
        🔵 🔵

         🔵     ← Further from core
                 → Probability: 0.85-0.88

            🔵  ← On the edge
                 → Probability: 0.65-0.75
```

### Real Example

```python
Behaviors in Cluster A:
1. "Prefers step-by-step explanations"     → Probability: 0.95 (very central)
2. "Requests sequential guidance"          → Probability: 0.88 (slightly off-center)
3. "Seeks structured breakdown"            → Probability: 0.92 (very central)

Average HDBSCAN Probability = (0.95 + 0.88 + 0.92) / 3 = 0.916 = 91.6%
```

### Interpretation

- **0.90-1.00**: Behavior is definitely part of this cluster (near core)
- **0.70-0.90**: Behavior probably belongs here (moderate distance)
- **0.50-0.70**: Behavior might belong here (on periphery)
- **<0.50**: Behavior is questionable (outlier)

### Why This Matters

HDBSCAN probability tells us about **internal cohesion** - are the behaviors in this cluster actually similar to each other? High probabilities mean the cluster is **tight and coherent**.

---

## 🎯 Component 2: Silhouette Score (40% weight)

### What It Measures
**"How well-separated is this cluster from other clusters?"**

### Where This Value Comes From

**Source:** Scikit-learn's silhouette_score function

```python
from sklearn.metrics import silhouette_score

silhouette = silhouette_score(
    embeddings,      # All behavior embeddings
    labels,          # Cluster assignments from HDBSCAN
    metric='cosine'  # Use cosine distance
)
# Returns: value between -1 and +1
```

### How Silhouette Score Works

For each behavior in a cluster:

```python
a = average_distance_to_same_cluster_members
b = average_distance_to_nearest_other_cluster

silhouette_per_behavior = (b - a) / max(a, b)

# Average across all behaviors in all clusters
overall_silhouette = mean(all_silhouettes)
```

### Mathematical Meaning

```
Silhouette ranges from -1 to +1:

+1.0: Perfect separation
      Cluster A       |         Cluster B
      🔵 🔵          |            🟢 🟢
     🔵 🔵 🔵        |          🟢 🟢 🟢
      🔵 🔵          |            🟢 🟢
      (far apart, well-defined)

 0.0: Overlapping clusters
      Cluster A overlaps Cluster B
         🔵 🔵 🟢
        🔵 🟢 🟢
         🔵 🟢
      (ambiguous boundaries)

-1.0: Wrong clustering
      Behaviors closer to other cluster than their own
         🔵 → really belongs in 🟢 cluster
```

### Normalization to 0-1 Scale

```python
silhouette_normalized = (silhouette + 1) / 2

Examples:
silhouette = +1.0 → normalized = (1.0 + 1) / 2 = 1.0 (perfect)
silhouette = +0.6 → normalized = (0.6 + 1) / 2 = 0.8 (good)
silhouette =  0.0 → normalized = (0.0 + 1) / 2 = 0.5 (mediocre)
silhouette = -0.4 → normalized = (-0.4 + 1) / 2 = 0.3 (poor)
```

**Why normalize?** Makes it easier to combine with HDBSCAN probabilities (both 0-1 range).

### Interpretation

- **0.8-1.0**: Clusters are very well-separated
- **0.6-0.8**: Good separation, clear boundaries
- **0.4-0.6**: Moderate separation, some overlap
- **<0.4**: Poor separation, clusters may not be distinct

### Why This Matters

Silhouette score tells us about **inter-cluster quality** - are the clusters actually different from each other? High silhouette means clusters represent **distinct patterns**, not arbitrary divisions.

---

## 🤔 Why Both Metrics? (Not Redundant!)

### The Key Question: Aren't They Measuring the Same Thing?

**No!** They measure different aspects of cluster quality.

| Metric | Question | Focus |
|--------|----------|-------|
| **HDBSCAN Probability** | "Are behaviors cohesive **within** their cluster?" | **Intra-cluster** quality |
| **Silhouette Score** | "Is the cluster **distinct from** other clusters?" | **Inter-cluster** separation |

### Why We Need Both: Real Scenarios

#### Scenario 1: High HDBSCAN, Low Silhouette
```
Problem: Tight clusters that are too similar to each other

    Cluster A              Cluster B
      🔵🔵                   🔵🔵
     🔵🔵🔵                 🔵🔵🔵
      🔵🔵                   🔵🔵
        (very close to each other!)

HDBSCAN Probability: 0.95 (tight cluster)
Silhouette Score: 0.2 (clusters overlap)

Combined Confidence: (0.95 * 0.6) + (0.2 * 0.4) = 0.57 + 0.08 = 0.65

Interpretation: 
✅ Behaviors within cluster are similar
❌ But cluster is not distinct from others
→ Moderate confidence (maybe should be one cluster?)
```

#### Scenario 2: Low HDBSCAN, High Silhouette
```
Problem: Distinct but loose clusters

    Cluster A              Cluster B
   🔵      🔵                   
  🔵  🔵    🔵                 🟢 🟢
 🔵    🔵  🔵                🟢 🟢 🟢
   (spread out)          (far away)

HDBSCAN Probability: 0.65 (scattered within cluster)
Silhouette Score: 0.9 (very distinct from other cluster)

Combined Confidence: (0.65 * 0.6) + (0.9 * 0.4) = 0.39 + 0.36 = 0.75

Interpretation:
⚠️ Behaviors within cluster are somewhat scattered
✅ But cluster is clearly different from others
→ Good confidence (real pattern, but loose grouping)
```

#### Scenario 3: High Both (Ideal!)
```
Perfect: Tight AND distinct

    Cluster A              Cluster B
      🔵🔵                       
     🔵🔵🔵                    🟢 🟢
      🔵🔵                   🟢 🟢 🟢
    (tight!)        (far away!)

HDBSCAN Probability: 0.92 (very cohesive)
Silhouette Score: 0.85 (well-separated)

Combined Confidence: (0.92 * 0.6) + (0.85 * 0.4) = 0.552 + 0.34 = 0.892

Interpretation:
✅ Behaviors are tightly grouped
✅ Cluster is distinct from others
→ High confidence! This is a real, reliable pattern.
```

#### Scenario 4: Low Both (Noise)
```
Problem: Poor clustering

    Random scatter
   🔵  🟢  🔵
  🟢  🔵  🟢  🔵
   🔵  🟢  🔵

HDBSCAN Probability: 0.45 (loose grouping)
Silhouette Score: 0.1 (heavy overlap)

Combined Confidence: (0.45 * 0.6) + (0.1 * 0.4) = 0.27 + 0.04 = 0.31

Interpretation:
❌ Behaviors are scattered
❌ Clusters overlap heavily
→ Low confidence (likely noise, not a real pattern)
```

---

## ⚖️ Why 60% / 40% Weights?

```python
confidence = (hdbscan_probability * 0.6) + (silhouette_score * 0.4)
```

### Rationale

1. **HDBSCAN gets 60%** because:
   - It's the primary clustering algorithm doing the heavy lifting
   - It provides granular, per-behavior probabilities
   - Internal cohesion is more important than external separation
   - Measures the "quality" of cluster membership directly

2. **Silhouette gets 40%** because:
   - It's a sanity check to ensure clusters are meaningfully different
   - Prevents false positives from overlapping clusters
   - One global score for the entire clustering solution
   - Important but secondary to internal cohesion

### Could These Be Different?

**Yes!** These weights are configurable and could be adjusted based on:

```python
# Current (default)
hdbscan_weight = 0.6
silhouette_weight = 0.4

# Could be dynamic based on data:
if cluster_size < 5:
    # Trust HDBSCAN more with small clusters
    hdbscan_weight = 0.7
    silhouette_weight = 0.3
    
elif num_clusters > 10:
    # Emphasize separation when many clusters
    hdbscan_weight = 0.5
    silhouette_weight = 0.5
```

**Why 60/40 was chosen:**
- Based on empirical testing and common practice in clustering validation
- Balances internal quality (more important) with external distinctness
- Provides reasonable confidence scores in most scenarios
- Could be tuned further with A/B testing on real user data

---

## 📈 Real Example from Test Data

### User: user_665390

```python
Total behaviors: 15
Total observations: 62
Clusters found: 2

Cluster 1: "Detailed Sequential Guidance"
├─ Behaviors in cluster: 8
├─ Strength: 8/15 = 0.533 = 53.3%
│
├─ HDBSCAN Probabilities:
│   [0.45, 0.42, 0.48, 0.44, 0.46, 0.43, 0.47, 0.45]
│   Average: 0.45
│
├─ Silhouette Score: 0.48
│   Normalized: (0.48 + 1) / 2 = 0.74
│
├─ Confidence Calculation:
│   (0.45 * 0.6) + (0.74 * 0.4)
│   = 0.27 + 0.296
│   = 0.566 = 56.6%
│
├─ Tier Assignment:
│   strength 53.3% ≥ 40% ✓
│   confidence 56.6% < 60% ✗
│   → NOISE (confidence below SECONDARY threshold)
│
└─ Interpretation:
    - Moderate frequency (appears in 53% of behaviors)
    - Behaviors are somewhat scattered (HDBSCAN: 0.45)
    - Cluster is reasonably distinct (Silhouette: 0.74)
    - Overall: Real pattern but needs more data for higher confidence

Cluster 2: "Visual Learning Preference"
├─ Behaviors in cluster: 7
├─ Strength: 7/15 = 0.467 = 46.7%
│
├─ HDBSCAN Probabilities:
│   [0.50, 0.48, 0.52, 0.49, 0.51, 0.50, 0.48]
│   Average: 0.497
│
├─ Silhouette Score: 0.44
│   Normalized: (0.44 + 1) / 2 = 0.72
│
├─ Confidence Calculation:
│   (0.497 * 0.6) + (0.72 * 0.4)
│   = 0.298 + 0.288
│   = 0.586 = 58.6%
│
├─ Tier Assignment:
│   strength 46.7% ≥ 40% ✓
│   confidence 58.6% < 60% ✗
│   → NOISE (confidence just below SECONDARY threshold)
│
└─ Interpretation:
    - Common behavior (appears in 47% of behaviors)
    - More cohesive than Cluster 1 (HDBSCAN: 0.50)
    - Good separation (Silhouette: 0.72)
    - Overall: Almost SECONDARY tier, needs slightly more data
```

### Key Insights from This Example

1. **Both clusters are NOISE tier** despite reasonable strength (46-53%)
   - Why? Confidence scores (56-58%) are just below the 60% threshold
   - This is intentional - system is conservative about labeling behaviors

2. **HDBSCAN probabilities are moderate** (0.45-0.50)
   - Behaviors within clusters are somewhat scattered
   - Not super tight groupings yet
   - Need more data points to establish clearer patterns

3. **Silhouette scores are decent** (0.72-0.74 normalized)
   - Clusters are reasonably well-separated
   - Not overlapping significantly
   - Distinct enough to be considered different patterns

4. **The 60/40 weighting works as intended**
   - HDBSCAN's moderate scores pull confidence down (appropriate)
   - Silhouette's good scores pull confidence up (balancing)
   - Result: Conservative confidence that requires more data for promotion

---

## 🎓 Key Takeaways

### 1. Two Complementary Metrics

- **HDBSCAN Probability**: Internal cluster quality (cohesion)
- **Silhouette Score**: External cluster quality (separation)
- **Together**: Comprehensive assessment of pattern reliability

### 2. Not Redundant

- They measure **different aspects** of clustering quality
- Both can be high, both can be low, or they can disagree
- Disagreement provides valuable diagnostic information

### 3. Source of Values

- **HDBSCAN**: Computed by HDBSCAN algorithm based on density and distance
- **Silhouette**: Computed by sklearn based on inter/intra cluster distances
- **Both**: Mathematical calculations, not arbitrary choices

### 4. Why 60/40 Split

- Prioritizes internal cohesion (more fundamental)
- Still validates external separation (catches overlaps)
- Empirically tested balance
- Configurable for different use cases

### 5. Confidence Interpretation

```
90-100%: Excellent - Very reliable pattern
75-90%:  Good - Solid pattern, minor scatter
60-75%:  Fair - Real pattern, some uncertainty
40-60%:  Questionable - Weak pattern, needs more data
<40%:    Poor - Likely noise, not reliable
```

---

## 🔧 Implementation Reference

**File:** `src/services/clustering_service.py`

```python
def _calculate_confidence(
    self,
    cluster_label: int,
    labels: np.ndarray,
    embeddings: np.ndarray,
    probabilities: Optional[np.ndarray] = None
) -> float:
    """
    Calculate confidence score for a cluster
    
    Combines:
    - HDBSCAN membership probability (60% weight)
    - Silhouette score (40% weight)
    """
    cluster_mask = labels == cluster_label
    cluster_embeddings = embeddings[cluster_mask]
    
    if len(cluster_embeddings) < 2:
        return 0.5
    
    # Component 1: HDBSCAN probability
    if probabilities is not None:
        cluster_probs = probabilities[cluster_mask]
        hdbscan_confidence = np.mean(cluster_probs)
    else:
        hdbscan_confidence = 0.7
    
    # Component 2: Silhouette score
    try:
        silhouette = silhouette_score(embeddings, labels, metric='cosine')
        silhouette_normalized = (silhouette + 1) / 2
    except:
        silhouette_normalized = 0.5
    
    # Weighted combination
    confidence = (hdbscan_confidence * 0.6) + (silhouette_normalized * 0.4)
    
    return confidence
```

---

## 📚 Further Reading

- [HDBSCAN Documentation](https://hdbscan.readthedocs.io/)
- [Silhouette Score (sklearn)](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.silhouette_score.html)
- [Cluster Validation Techniques](https://en.wikipedia.org/wiki/Cluster_analysis#Internal_evaluation)
- CBIE Implementation: `src/services/clustering_service.py`

---

**Document Version:** 1.0  
**Last Updated:** December 28, 2025  
**Author:** CBIE Development Team
