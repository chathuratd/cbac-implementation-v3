# **CBIE MVP Documentation – Full Calculation Logic and Parameter Justification**

---

## **1. Overview**

The Core Behavior Identification Engine (CBIE) MVP extracts **core behaviors** from user behavior inputs and prompt history. It computes scores that quantify the **strength, clarity, and reliability** of each behavior, clusters similar behaviors, and assigns canonical behaviors for core behavior profiling.

The formulas and parameters are specifically **designed for this MVP**, balancing interpretability and simplicity for research purposes.

---

## **2. Input Data**

### **2.1 Behavior Object**

```json
{
  "behavior_id": "beh_3ccbf2b2",
  "behavior_text": "prefers visual learning",
  "credibility": 0.95,
  "clarity_score": 0.76,
  "extraction_confidence": 0.77,
  "reinforcement_count": 17,
  "decay_rate": 0.012,
  "created_at": 1765741962,
  "last_seen": 1765741962,
  "prompt_history_ids": ["prompt_1", "prompt_2"]
}
```

* **credibility**: Trustworthiness of behavior (0–1), computed based on reinforcement, recency, and prompt clarity.
* **clarity_score**: Measures explicitness in the prompt (0–1).
* **extraction_confidence**: Confidence of NLP extraction (0–1), short-term validation.
* **reinforcement_count**: Number of times behavior was expressed.
* **decay_rate**: How quickly older behaviors lose relevance.
* **timestamps**: creation & last seen, used for recency/decay calculations.
* **prompt_history_ids**: Links to source prompts.

---

### **2.2 Prompt Object**

```json
{
  "prompt_id": "prompt_1",
  "prompt_text": "Visualize the HTTP request lifecycle",
  "timestamp": 1761637013
}
```

* Used to calculate recency, reinforcement, and semantic similarity.

---

## **3. Score Calculations**

### **3.1 Behavior Weight (BW)**

**Formula:**

[
BW = credibility^{\alpha} \cdot clarity^{\beta} \cdot extraction_confidence^{\gamma}
]

* **Purpose:** Combines trustworthiness, clarity, and short-term confidence into a single score.

**Parameters and Justification:**

| Parameter                        | Default | Why Chosen                                                                                         | Formula Source      |
| -------------------------------- | ------- | -------------------------------------------------------------------------------------------------- | ------------------- |
| α (credibility weight)           | 0.35    | Ensures reliability contributes significantly, but not dominant. Selected to balance with clarity. | Custom for this MVP |
| β (clarity weight)               | 0.40    | Slightly higher because clarity reflects direct evidence of behavior.                              | Custom for this MVP |
| γ (extraction confidence weight) | 0.25    | Lower weight since extraction confidence is temporary and may be deprecated.                       | Custom for this MVP |

**Example Calculation:**

For `credibility=0.95, clarity=0.76, extraction_confidence=0.77`:

[
BW = 0.95^{0.35} \cdot 0.76^{0.40} \cdot 0.77^{0.25} \approx 0.858
]

---

### **3.2 Adjusted Behavior Weight (ABW)**

**Formula:**

[
ABW = BW \cdot (1 + reinforcement_count \cdot r) \cdot e^{-decay_rate \cdot days_since_last_seen}
]

* **Purpose:** Incorporates reinforcement and recency into the behavior weight.

**Parameters and Justification:**

| Parameter                    | Default            | Why Chosen                                                                           | Formula Source           |
| ---------------------------- | ------------------ | ------------------------------------------------------------------------------------ | ------------------------ |
| r (reinforcement multiplier) | 0.01               | Small increase per reinforcement; prevents overpowering the other factors.           | Custom for MVP           |
| decay_rate                   | per behavior input | Reflects natural decrease in relevance over time; ensures recent behaviors dominate. | Custom for MVP           |
| days_since_last_seen         | computed           | `(current_timestamp - last_seen)/86400`                                              | Standard time conversion |

**Example Calculation:**

Behavior `BW=0.858`, `reinforcement_count=17`, `decay_rate=0.012`, `days_since_last_seen=3`:

[
ABW = 0.858 \cdot (1 + 17 \cdot 0.01) \cdot e^{-0.012 \cdot 3}
= 0.858 \cdot 1.17 \cdot 0.964 \approx 0.967
]

**Justification:**

* Reinforcement increment is subtle to prevent rare behaviors from exploding the score.
* Decay ensures old behaviors fade naturally.

---

### **3.3 Cluster Core Behavior Index (CBI)**

**Formula:**

[
CBI = \frac{\sum ABW_i}{N}
]

* **Purpose:** Aggregates Adjusted Weights for a cluster.
* **Inputs:** ABWs of behaviors in a cluster, `N = number of behaviors`.

**Example:** 3 behaviors in cluster with `ABWs=[0.967,0.945,0.873]`:

[
CBI = \frac{0.967+0.945+0.873}{3} \approx 0.928
]

**Justification:** Simple average ensures interpretability and maintains MVP simplicity.

---

### **3.4 Canonical Behavior Selection**

* **Logic:** Behavior with **highest ABW** in cluster is canonical.
* **Input:** ABW values in cluster
* **Purpose:** Represents the strongest behavior in the cluster.

---

### **3.5 Tier Assignment**

| Tier      | Condition       | Parameter                 | Justification                                                                                    |
| --------- | --------------- | ------------------------- | ------------------------------------------------------------------------------------------------ |
| PRIMARY   | CBI ≥ 1.0       | primary_threshold = 1.0   | High confidence behaviors are considered core. Threshold chosen to capture top cluster strength. |
| SECONDARY | 0.7 ≤ CBI < 1.0 | secondary_threshold = 0.7 | Medium relevance behaviors. Provides buffer zone between PRIMARY and NOISE.                      |
| NOISE     | CBI < 0.7       | –                         | Low influence behaviors ignored.                                                                 |

* **Formula Source:** Custom thresholds for MVP; easily adjustable for research experiments.

---

### **3.6 Temporal Metrics**

* **First Seen:** earliest `prompt.timestamp`
* **Last Seen:** latest `prompt.timestamp`
* **Days Active:** `(last_seen - first_seen)/86400`

**Justification:** Tracks persistence and stability of core behaviors.

---

## **4. Clustering Logic**

* **Algorithm:** HDBSCAN
* **Distance Metric:** Cosine similarity of embeddings
* **Embedding Model:** `text-embedding-3-large` (OpenAI)

**Parameters:**

| Parameter                 | Default | Justification                                            |
| ------------------------- | ------- | -------------------------------------------------------- |
| min_cluster_size          | 2       | Ensure clusters have ≥2 behaviors to avoid noise.        |
| min_samples               | 1       | Minimum support to form cluster; allows MVP flexibility. |
| cluster_selection_epsilon | 0.15    | Tight enough to group semantically close behaviors.      |

**Formula Source:** HDBSCAN is a standard clustering algorithm; parameters tuned for research MVP.

---

## **5. LLM Archetype Assignment**

* **Prompt Template:**

```
"Given the following canonical behaviors: [list behaviors], assign a single descriptive archetype label for the user."
```

* **Output:** Archetype label (optional in MVP)
* **Justification:** Simplifies semantic summarization without complicating pipeline.

---

## **6. APIs for MVP**

| API                            | Method | Purpose                                                  |
| ------------------------------ | ------ | -------------------------------------------------------- |
| /analyze-behaviors             | POST   | Input behaviors & prompts → output Core Behavior Profile |
| /get-user-profile/{user_id}    | GET    | Retrieve stored core behavior profile                    |
| /list-core-behaviors/{user_id} | GET    | Retrieve canonical behaviors only                        |
| /update-behavior               | POST   | Update reinforcement, credibility, or timestamps         |
| /assign-archetype              | POST   | Use LLM to assign archetype label                        |

