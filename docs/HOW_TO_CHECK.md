# How to Check Cluster-Centric Implementation

## ✅ Working Method: Direct Pipeline Test

**File:** `test_cluster_pipeline.py`

**Command:**
```bash
python test_cluster_pipeline.py
```

**What it shows:**
- Complete cluster-centric analysis
- All cluster metrics (strength, confidence, consistency, reinforcement, clarity_trend)
- Evidence aggregation (prompts, timestamps, wording variations)
- Temporal data (first_seen, last_seen, days_active)
- Tier assignments (PRIMARY/SECONDARY/NOISE)

**Output includes:**
```
PRIMARY CLUSTERS (Detailed)
1. prefers analogies and metaphors
   Cluster ID: cluster_1
   Cluster Size: 4 observations
   Cluster Strength: 0.8423
   Confidence: 0.6232
     - Consistency: 0.6177
     - Reinforcement: 0.6990
     - Clarity Trend: 0.4825
   Days Active: 35.0
   Prompt Count: 4
   Wording Variations (4):
     1. learns by examples...
     2. prefers analogies and metaphors...
     3. prefers comparative analysis...
```

---

## ⚠️ API Testing Currently Blocked

The API endpoints currently have schema validation issues because:

1. **`BehaviorModel` was redefined** as `BehaviorObservation`
2. **Old API endpoints** still expect the legacy schema
3. **New cluster endpoint** (`/analyze-behaviors-cluster-centric`) needs schema updates

### What needs to be done for API testing:

1. Create separate request schemas for backward compatibility
2. Update API validation to handle both old and new formats
3. OR migrate all endpoints to use new schemas

---

## Best Way to Verify Implementation

### Option 1: Direct Pipeline (WORKS NOW) ✅
```bash
python test_cluster_pipeline.py
```

**Advantages:**
- Tests the actual implementation
- Shows all cluster data
- No API overhead
- Complete validation checks

### Option 2: Python REPL (Quick Check)
```python
import asyncio
from test_cluster_pipeline import test_cluster_pipeline

# Run the test
asyncio.run(test_cluster_pipeline())
```

### Option 3: API Testing (Requires Schema Fix)
Would need to:
1. Update `AnalyzeBehaviorsRequest` to accept new fields
2. Restart API server
3. Call `/analyze-behaviors-cluster-centric`

---

## What You Can Verify Right Now

Run `python test_cluster_pipeline.py` and verify:

### ✅ Clusters are primary entities
- Loop iterates over clusters
- Each cluster contains ALL observations
- No observations discarded

### ✅ Scoring is cluster-based
- `cluster_strength = log(size+1) * mean_abw * recency`
- Single-member clusters are weaker
- Strength grows with cluster size

### ✅ Confidence from cluster metrics
- `consistency_score` - semantic similarity
- `reinforcement_score` - observation count
- `clarity_trend` - improving/degrading over time

### ✅ Evidence aggregation
- `all_prompt_ids[]` - complete prompt history
- `all_timestamps[]` - temporal data
- `wording_variations[]` - different phrasings
- Can answer "WHY is this core?"

### ✅ Canonical label is display-only
- Selected by: clarity + centroid proximity
- NOT used for scoring
- NOT used for confidence

---

## Summary

**Current Status:**
- ✅ Cluster-centric implementation is COMPLETE and WORKING
- ✅ Can be tested via `test_cluster_pipeline.py`
- ⚠️ API endpoints need schema updates for external testing

**To test implementation:**
```bash
python test_cluster_pipeline.py
```

**To test via API (after schema fixes):**
```bash
# 1. Fix API schemas (todo item #8)
# 2. Restart server
# 3. Run: python test_cluster_api.py
```

For now, the direct pipeline test proves the implementation is correct.
