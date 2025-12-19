# CBIE Storage Architecture Documentation

## Overview

The CBIE system uses a **dual-database architecture** optimized for semantic search and metadata management.

---

## Storage Design

### 🗄️ Qdrant Vector Database (Primary Storage for Behaviors)

**Purpose**: Store behavior embeddings for semantic similarity and clustering

**What's Stored**:
- ✅ **Behavior embeddings** (3072-dimensional vectors from text-embedding-3-large)
- ✅ **Complete behavior metadata** (all BehaviorModel fields)
  - behavior_id, behavior_text
  - user_id, session_id
  - credibility, reinforcement_count, decay_rate
  - created_at, last_seen
  - clarity_score, extraction_confidence
  - prompt_history_ids
  - Optional: domain, expertise_level

**Why Qdrant**:
- Optimized for vector similarity search (cosine similarity)
- Required for HDBSCAN clustering on embeddings
- Fast semantic search capabilities
- Efficient storage of high-dimensional vectors
- Single source of truth for all behavior data (vector + metadata)

**Schema**:
```json
{
  "id": "uuid",
  "vector": [0.123, -0.456, ...],  // 3072 dimensions
  "payload": {
    "behavior_id": "beh_3ccbf2b2",
    "behavior_text": "prefers visual learning",
    "user_id": "user_348",
    "session_id": "session_6366",
    "credibility": 0.86,
    "reinforcement_count": 8,
    "decay_rate": 0.023,
    "created_at": 1763722466,
    "last_seen": 1764114775,
    "clarity_score": 0.84,
    "extraction_confidence": 0.95,
    "prompt_history_ids": ["prompt_3412cae1", "prompt_d2850f60", ...]
  }
}
```

---

### 🗄️ MongoDB (Storage for Prompts, Metadata, and Profiles)

**Purpose**: Store structured data, metadata, and analysis results

**Collections**:

#### 1. `prompts` Collection
**What's Stored**:
- ✅ **Prompt text** (user input)
- ✅ **Prompt ID** (unique identifier)
- ✅ **User ID**
- ✅ **Session ID**
- ✅ **Timestamp**
- ✅ **Token count** (optional)

**Why MongoDB**:
- Prompts are metadata (no embedding needed for clustering)
- Used for temporal analysis (first_seen, last_seen, days_active)
- Easy querying by user_id and timestamp
- Document-oriented storage fits prompt structure

**Schema**:
```json
{
  "_id": ObjectId,
  "prompt_id": "prompt_d6bafd26",
  "prompt_text": "Visualize the HTTP request lifecycle",
  "timestamp": 1761637013,
  "tokens": 12.0,
  "user_id": "user_348",
  "session_id": "session_7732"
}
```

#### 2. `behaviors` Collection (Optional Metadata Cache)
**What's Stored**:
- ✅ **Full BehaviorModel** with all metadata
- Credibility, clarity_score, extraction_confidence
- Reinforcement_count, decay_rate
- Created_at, last_seen
- Prompt_history_ids

**Purpose**: Quick access to behavior metadata without Qdrant query

**Note**: The "source of truth" for behaviors is **Qdrant** (with embeddings). MongoDB stores metadata for convenience.

#### 3. `core_behavior_profiles` Collection
**What's Stored**:
- ✅ **Analysis results** (primary/secondary behaviors)
- ✅ **Archetype labels**
- ✅ **Statistics**
- ✅ **Generated timestamp**

#### 4. `clusters` Collection (Optional)
**What's Stored**:
- ✅ **Cluster metadata**
- ✅ **Cluster CBI scores**
- ✅ **Member behavior IDs**

---

## Two Operational Scenarios

### 🔵 Scenario 1: Production (Normal Operation)

**Data Flow**:
```
1. User interaction generates behavior
   ↓
2. Behavior text → Azure OpenAI → Generate embedding
   ↓
3. Store in Qdrant (behavior_id + embedding + text + metadata)
   ↓
4. Optionally store full metadata in MongoDB behaviors collection
   ↓
5. User prompt → Store in MongoDB prompts collection
   ↓
6. When analysis triggered:
   ├─ Fetch behaviors from Qdrant (with embeddings)
   ├─ Fetch prompts from MongoDB
   ├─ Calculate BW/ABW
   ├─ Run HDBSCAN clustering on embeddings
   ├─ Generate profile
   └─ Store profile in MongoDB
```

**API Endpoint**: `POST /api/v1/analyze-behaviors-from-storage?user_id=user_348`

**Advantages**:
- ✅ No redundant embedding generation
- ✅ Fast analysis (embeddings pre-computed)
- ✅ Semantic search enabled (similar behaviors)
- ✅ Production-ready architecture

---

### 🟢 Scenario 2: Import/Testing (Bulk Data Import)

**Data Flow**:
```
1. Receive batch of behaviors and prompts (e.g., test data)
   ↓
2. Store prompts in MongoDB
   ↓
3. Generate embeddings for all behaviors
   ↓
4. Store behaviors in Qdrant (with embeddings)
   ↓
5. Store behavior metadata in MongoDB (optional)
   ↓
6. Run analysis pipeline:
   ├─ Calculate BW/ABW
   ├─ Run HDBSCAN clustering
   ├─ Generate profile
   └─ Store profile in MongoDB
```

**API Endpoint**: `POST /api/v1/analyze-behaviors` (with request body)

**Use Cases**:
- ✅ Testing with sample data
- ✅ Bulk import from external systems
- ✅ Initial data setup
- ✅ Migration from other systems

---

## Implementation Details

### Behavior Storage Workflow

#### Normal Production Flow:
```python
# 1. New behavior detected
behavior_text = "prefers visual learning"

# 2. Generate embedding
embedding = embedding_service.generate_embedding(behavior_text)

# 3. Store in Qdrant (primary storage)
qdrant_service.insert_embeddings(
    embeddings=[embedding],
    behavior_ids=["beh_123"],
    behavior_texts=[behavior_text],
    user_id="user_348",
    timestamps=[timestamp]
)

# 4. Optionally store metadata in MongoDB
mongodb_service.insert_behavior(behavior_model)

# 5. Later: Fetch for analysis
behaviors = qdrant_service.get_embeddings_by_user("user_348")
# Returns: embeddings + metadata, ready for clustering
```

#### Analysis from Storage:
```python
# Production scenario
profile = await analysis_pipeline.analyze_behaviors_from_storage(
    user_id="user_348"
)
# Fetches from Qdrant + MongoDB, runs analysis
```

---

## Why This Architecture?

### ✅ Separation of Concerns
- **Qdrant**: Optimized for vector operations
- **MongoDB**: Optimized for structured data and metadata

### ✅ Performance
- Embeddings pre-computed and stored
- No redundant API calls to OpenAI
- Fast clustering with Qdrant's optimized vector storage

### ✅ Scalability
- Qdrant handles millions of vectors efficiently
- MongoDB handles high-volume prompt storage
- Independent scaling of vector and document storage

### ✅ Semantic Capabilities
- Semantic search on behaviors (find similar behaviors)
- Clustering based on meaning, not just keywords
- Future: Recommend similar users based on behavior vectors

### ✅ Cost Efficiency
- Embeddings generated once, reused many times
- Reduced OpenAI API costs
- Efficient storage of metadata

---

## Migration from Single-DB Systems

If migrating from a system where everything was in MongoDB:

### Step 1: Add Qdrant
```bash
docker run -d -p 6333:6333 qdrant/qdrant:latest
```

### Step 2: Generate and Store Embeddings
```python
# For existing behaviors in MongoDB
behaviors = mongodb_service.get_all_behaviors()

for behavior in behaviors:
    # Generate embedding
    embedding = embedding_service.generate_embedding(behavior.behavior_text)
    
    # Store in Qdrant
    qdrant_service.insert_embeddings(
        embeddings=[embedding],
        behavior_ids=[behavior.behavior_id],
        behavior_texts=[behavior.behavior_text],
        user_id=behavior.user_id,
        timestamps=[behavior.last_seen]
    )
```

### Step 3: Update Application
- Use `analyze_behaviors_from_storage()` for production
- Keep `analyze_behaviors()` for imports

---

## Best Practices

### ✅ DO:
- Store behaviors in Qdrant with embeddings
- Store prompts in MongoDB
- Keep behavior metadata in MongoDB for quick access (optional)
- Use `analyze_behaviors_from_storage()` in production
- Generate embeddings once per behavior

### ❌ DON'T:
- Store embeddings in MongoDB (inefficient for vector ops)
- Store prompts in Qdrant (they don't need embeddings)
- Regenerate embeddings on every analysis
- Query Qdrant for non-vector operations

---

## Monitoring & Maintenance

### Qdrant Monitoring:
```python
# Check collection size
collection_info = qdrant_service.client.get_collection(
    collection_name="behavior_embeddings"
)
print(f"Vector count: {collection_info.points_count}")
```

### MongoDB Monitoring:
```python
# Check prompt count
prompt_count = mongodb_service.db.prompts.count_documents({"user_id": "user_348"})
print(f"Prompts: {prompt_count}")
```

### Cleanup:
```python
# Delete user data from both databases
qdrant_service.delete_embeddings_by_user("user_348")
mongodb_service.db.prompts.delete_many({"user_id": "user_348"})
mongodb_service.db.behaviors.delete_many({"user_id": "user_348"})
```

---

## Testing Both Scenarios

Use the provided test script:
```bash
python test_api_updated.py
```

This will:
1. Test import scenario (store new data)
2. Test production scenario (fetch from storage)
3. Verify both databases are used correctly

---

## Summary

| Component | Storage | Purpose | Primary Use |
|-----------|---------|---------|-------------|
| **Behaviors** | Qdrant | Embeddings + clustering | Semantic analysis |
| **Prompts** | MongoDB | Temporal analysis | First/last seen, days active |
| **Behavior Metadata** | MongoDB (optional) | Quick access | Credibility, clarity, etc. |
| **Profiles** | MongoDB | Analysis results | Store output |
| **Clusters** | MongoDB (optional) | Cluster metadata | Debugging/analysis |

**Production Endpoint**: `/analyze-behaviors-from-storage` ⭐

**Import Endpoint**: `/analyze-behaviors` (for testing/bulk import)
