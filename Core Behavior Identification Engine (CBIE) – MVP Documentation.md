# **Core Behavior Identification Engine (CBIE) – MVP Documentation (Expanded with Calculations and Parameters)**

---

## **1. Overview**

CBIE is an MVP system designed to identify a user’s **core behaviors** from behavior inputs and prompt history. The system calculates behavior strengths, clusters similar behaviors, assigns canonical behaviors to clusters, and labels them as **PRIMARY**, **SECONDARY**, or **NOISE**. Optionally, it can generate a behavioral **archetype** using an LLM.

This version focuses on **research feasibility** rather than production complexity.

---

## **2. Input Data**

### **2.1 Behavior Object**

Each behavior includes:

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
  "prompt_history_ids": ["prompt_1", "prompt_2", "..."]
}
```

* **credibility**: trustworthiness (0–1)
* **clarity_score**: explicitness of behavior (0–1)
* **extraction_confidence**: model confidence (0–1)
* **reinforcement_count**: number of times behavior was expressed
* **decay_rate**: decay over time
* **timestamps**: creation and last seen
* **prompt_history_ids**: list of related prompt IDs

### **2.2 Prompt Object**

```json
{
  "prompt_id": "prompt_1",
  "prompt_text": "Visualize the HTTP request lifecycle",
  "timestamp": 1761637013
}
```

* **prompt_text**: user input
* **timestamp**: when prompt was created

---

## **3. Score Calculations**

### **3.1 Behavior Weight**

**Formula:**

[
\text{Behavior Weight} = \text{credibility}^{\alpha} \times \text{clarity score}^{\beta} \times \text{extraction confidence}^{\gamma}
]

**Parameters:**

| Parameter                        | Default Value | Justification                                                                             |
| -------------------------------- | ------------- | ----------------------------------------------------------------------------------------- |
| α (credibility weight)           | 0.35          | Ensures trustworthiness impacts the score moderately; avoids overweighting single factor. |
| β (clarity weight)               | 0.40          | Clarity is slightly more important, as ambiguous behaviors reduce reliability.            |
| γ (extraction confidence weight) | 0.25          | Extraction confidence is short-term validation; lower weight in MVP.                      |

**Purpose:** Combines reliability, clarity, and model confidence into a single measure of behavior strength.

---

### **3.2 Adjusted Behavior Weight**

**Formula:**

[
\text{Adjusted Weight} = \text{Behavior Weight} \times \left(1 + \text{reinforcement count} \times 0.01\right) \times e^{-\text{decay rate} \times \text{days since last seen}}
]

**Parameters:**

| Parameter                | Default Value      | Justification                                                                          |
| ------------------------ | ------------------ | -------------------------------------------------------------------------------------- |
| Reinforcement multiplier | 0.01               | Small increment per reinforcement ensures repeated behaviors get slightly more weight. |
| Decay rate               | per behavior input | Reduces influence of old behaviors; prevents outdated behaviors from dominating.       |
| days since last seen     | computed           | Keeps recency relevant; calculated as `(current_time - last_seen)/86400`.              |

**Purpose:** Adjusts behavior weight for recency and reinforcement, reflecting actual user tendencies.

---

### **3.3 Cluster CBI (Core Behavior Index)**

**Formula:**

[
\text{Cluster CBI} = \frac{\sum \text{Adjusted Weight of behaviors in cluster}}{\text{number of behaviors in cluster}}
]

* **Input:** Adjusted Behavior Weights of behaviors in a cluster
* **Purpose:** Quantifies cluster strength; used for tier assignment.

---

### **3.4 Canonical Behavior Selection**

* **Logic:** Behavior in cluster with the **highest Adjusted Weight** is selected as canonical.
* **Purpose:** Represents the core of the cluster.

---

### **3.5 Tier Classification**

| Tier      | Condition                                             | Parameters                |
| --------- | ----------------------------------------------------- | ------------------------- |
| PRIMARY   | Cluster CBI ≥ primary_threshold                       | primary_threshold = 1.0   |
| SECONDARY | secondary_threshold ≤ Cluster CBI < primary_threshold | secondary_threshold = 0.7 |
| NOISE     | Cluster CBI < secondary_threshold                     |                           |

**Justification:**

* Thresholds chosen for clear separation of high vs. medium vs. low relevance behaviors.
* Interpretable and adjustable for research studies.

---

### **3.6 Temporal Metrics**

* **First Seen:** earliest prompt timestamp in canonical cluster
* **Last Seen:** latest prompt timestamp
* **Days Active:** `(last_seen - first_seen)/86400`

**Purpose:** Provides evidence of sustained behavior over time.

---

## **4. Clustering Logic**

* **Algorithm:** HDBSCAN
* **Distance Metric:** cosine similarity between embeddings
* **Parameters:**

| Parameter        | Default Value | Justification                                                 |
| ---------------- | ------------- | ------------------------------------------------------------- |
| min_cluster_size | 2             | Ensures clusters contain at least 2 behaviors; reduces noise. |
| min_samples      | 1             | Small sample threshold allows MVP flexibility.                |
| metric           | cosine        | Embedding-based semantic similarity is standard for text.     |
| epsilon          | 0.15          | Allows close behaviors to form clusters.                      |

* **Embedding model:** text-embedding-3-large (OpenAI)
* **Purpose:** Groups semantically similar behaviors into clusters for canonical selection.

---

## **5. Archetype Labeling (Optional LLM)**

* **Prompt Template for LLM:**

```
"Given the following user behaviors: [list canonical behavior_text], classify the user into a behavioral archetype. Return a single descriptive label."
```

* **Purpose:** Adds semantic generalization for research analysis.
* **Output:** Archetype label (e.g., “Visual Learner”, “Detail-Oriented”).

---

## **6. Core Behavior Profile Output**

Example:

```json
{
  "user_id": "user_348",
  "generated_at": 1766000000,
  "primary_behaviors": [
    {
      "behavior_id": "beh_3ccbf2b2",
      "behavior_text": "prefers visual learning",
      "cluster_id": "cluster_1",
      "cbi_original": 0.88,
      "cluster_cbi": 1.05,
      "tier": "PRIMARY",
      "temporal_span": {"first_seen": 1765741962, "last_seen": 1765840000, "days_active": 10}
    }
  ],
  "secondary_behaviors": [...],
  "archetype": "Visual Learner",
  "statistics": {
    "total_behaviors_analyzed": 5,
    "clusters_formed": 3,
    "total_prompts_analyzed": 50,
    "analysis_time_span_days": 60
  }
}
```

---

## **7. MVP APIs**

### **7.1 /analyze-behaviors** (POST)

* **Input:** list of behaviors and prompt data
* **Output:** Core Behavior Profile JSON
* **Purpose:** Main API to run the MVP pipeline

### **7.2 /get-user-profile/{user_id}** (GET)

* **Purpose:** Retrieve a user’s existing Core Behavior Profile
* **Output:** JSON

### **7.3 /list-core-behaviors/{user_id}** (GET)

* **Purpose:** Return canonical core behaviors for downstream context usage
* **Output:** List of canonical behaviors and IDs

### **7.4 /update-behavior** (POST)

* **Purpose:** Update reinforcement, credibility, or timestamps of a behavior
* **Input:** behavior_id + updated fields
* **Output:** Confirmation / updated behavior

### **7.5 /assign-archetype** (POST)

* **Purpose:** Assign behavioral archetype label via LLM
* **Input:** List of canonical behaviors
* **Output:** Archetype label

---

## **8. Justification of MVP Choices**

| Component                   | Justification                                                                               |
| --------------------------- | ------------------------------------------------------------------------------------------- |
| **Behavior Weight formula** | Combines trustworthiness, clarity, and confidence; ensures multiple factors are considered. |
| **Adjusted Weight**         | Accounts for reinforcement & decay to prioritize recent and repeated behaviors.             |
| **Cluster CBI**             | Aggregates behavior strength within clusters; simple average keeps MVP interpretable.       |
| **Tier Classification**     | Threshold-based; clearly separates high, medium, low relevance.                             |
| **Embedding + HDBSCAN**     | Lightweight semantic clustering; minimal configuration, easy for MVP.                       |
| **LLM Archetype**           | Adds semantic generalization without complicated rules; optional for MVP.                   |
| **APIs**                    | Minimal, extendable, and modular for research use.                                          |

