# API Documentation - Cluster-Centric Core Behavior Detection

**Version**: 2.0 (Cluster-Centric, User-Facing)  
**Last Updated**: December 27, 2025  
**Status**: Migration in Progress

---

## Table of Contents

1. [Overview](#overview)
2. [User-Facing Architecture](#user-facing-architecture)
3. [Authentication & Authorization](#authentication--authorization)
4. [Current API Status](#current-api-status)
5. [APIs to Remove](#apis-to-remove)
6. [APIs to Add](#apis-to-add)
7. [User Management APIs](#user-management-apis)
8. [Database Persistence](#database-persistence)
9. [Migration Roadmap](#migration-roadmap)

---

## Overview

This document outlines the API migration from the **observation-centric** model to the **cluster-centric** architecture. The new design treats behavior clusters as primary entities, providing more stable and reliable core behavior profiles.

**IMPORTANT**: This is a **user-facing system**. Each user can view and manage their own behavior profile. APIs must enforce user-scoped access and provide user controls for data management.

### Architecture Change

**Old Model (Observation-Centric)**:
- Individual behavior observations were selected as "canonical"
- Profiles had 1:1 mapping between canonical_behaviors and observations
- Updates/deletes on individual observations

**New Model (Cluster-Centric)**:
- Behavior clusters aggregate multiple observations
- Each cluster has canonical_label (synthesized), wording_variations[], evidence
- Observations are immutable by system, but users can delete/hide incorrect behaviors
- User-controlled data with privacy settings

---

## User-Facing Architecture

### Design Principles

1. **User Ownership**: Users own their behavior data and can view/manage it
2. **Privacy First**: Users control what data is stored and visible
3. **Correction Mechanism**: Users can delete incorrect behaviors or report issues
4. **Transparency**: Users see exactly what behaviors are detected
5. **Configurability**: Users have settings to control analysis behavior

### User Roles

**End User**:
- View their own behavior profile
- Delete incorrect behaviors
- Hide specific clusters from their profile
- Export their data
- Configure privacy settings
- Request profile deletion (GDPR compliance)

**System** (automated):
- Analyze user interactions to detect behaviors
- Generate clusters from observations
- Update profiles when new data arrives

**Implementation Note**: User authentication is handled externally. All user-facing endpoints assume an authenticated session and automatically scope data to the current user.

### Data Ownership Model

- Each user has **one profile**: Identified by `user_id`
- Users access **their own data**: Via `/profile/me` endpoints
- Behaviors are **soft-deletable**: Users can mark as incorrect, system excludes from analysis
- Privacy controls: Users can pause analysis, export data, request deletion

---

## Current API Status

### Existing Endpoints

**Note**: Authentication is handled externally. All user-facing endpoints assume an active user session.

| Method | Endpoint | Access | Status | Notes |
|--------|----------|--------|--------|-------|
| **User-Scoped Endpoints** |
| GET | `/api/v1/profile/me` | User | 🆕 **NEW** | User's own profile |
| GET | `/api/v1/profile/me/llm-context` | User | 🆕 **NEW** | User's LLM context |
| GET | `/api/v1/profile/me/summary` | User | 🆕 **NEW** | User's profile summary |
| DELETE | `/api/v1/profile/me/behaviors/{behavior_id}` | User | 🆕 **NEW** | Delete incorrect behavior |
| PUT | `/api/v1/profile/me/clusters/{cluster_id}/hide` | User | 🆕 **NEW** | Hide cluster from profile |
| GET | `/api/v1/profile/me/settings` | User | 🆕 **NEW** | User preferences |
| PUT | `/api/v1/profile/me/settings` | User | 🆕 **NEW** | Update preferences |
| POST | `/api/v1/profile/me/export` | User | 🆕 **NEW** | Export user data |
| DELETE | `/api/v1/profile/me` | User | 🆕 **NEW** | Delete profile (GDPR) |
| **System Endpoints** |
| POST | `/api/v1/analyze-behaviors-from-storage` | System | ⚠️ **DEPRECATED** | Uses old pipeline |
| POST | `/api/v1/analyze-behaviors` | System | ⚠️ **DEPRECATED** | Uses old pipeline |
| POST | `/api/v1/update-behavior` | System | ❌ **REMOVE** | Violates immutability |
| POST | `/api/v1/assign-archetype` | System | ✅ **ACTIVE** | Automated only |
| POST | `/api/v1/analyze-behaviors-cluster-centric` | System | ✅ **ACTIVE** | Automated only |
| **Public Endpoints** |
| GET | `/api/v1/health` | Public | ✅ **ACTIVE** | Health check |

---

## APIs to Remove

### 1. POST `/api/v1/update-behavior`

**Reason for Removal**: Violates immutability principle of observations

**Current Implementation**:
```python
@router.post("/update-behavior")
async def update_behavior(request: UpdateBehaviorRequest):
    """
    Updates individual observation fields:
    - reinforcement_count
    - credibility
    - clarity_score
    - extraction_confidence
    - last_seen
    - decay_rate
    """
```

**Why Remove**:
- Observations in cluster-centric model are **immutable snapshots**
- Behavior evolution is captured through **new observations**, not mutations
- Editing past observations corrupts temporal analysis
- Cluster strength/confidence should recalculate from original data

**Migration Path**:
- Replace with: Add new observations when user behavior changes
- Clusters will naturally adapt through re-clustering
- Historical data remains pristine for auditing

---

### 2. DELETE `/api/v1/behavior/{behavior_id}` (if exists)

**Reason for Removal**: Not found in current codebase, but mentioned in design

**Why Remove**:
- Same immutability principle
- Observations should never be deleted, only excluded from analysis
- Implement soft-delete via `is_active` flag if needed

---

### 3. POST `/api/v1/analyze-behaviors-from-storage` & POST `/api/v1/analyze-behaviors`

**Reason for Removal**: Uses deprecated `analysis_pipeline.py`

**Current Implementation**:
```python
@router.post("/analyze-behaviors-from-storage")
async def analyze_behaviors_from_storage(request: AnalyzeFromStorageRequest):
    # Uses old observation-centric pipeline
    profile = await analysis_pipeline.analyze_behaviors(...)
```

**Why Remove**:
- Calls `src/services/analysis_pipeline.py` which is fully deprecated
- Returns observation-centric profile structure
- Replaced by `/analyze-behaviors-cluster-centric`

**Migration Path**:
- All clients should migrate to POST `/api/v1/analyze-behaviors-cluster-centric`
- Response schema changed: `canonical_behaviors[]` → `behavior_clusters[]`

---

## APIs to Add

**Note**: Authentication is handled externally. User-facing endpoints assume an authenticated session.

### User Profile APIs (User-Scoped)

#### 1. GET `/api/v1/profile/me`

**Purpose**: Get current user's own profile

**Access**: User (session-based)

**Response Schema**: Same as cluster-centric profile structure

**Implementation**:
```python
@router.get("/profile/me")
async def get_my_profile(current_user_id: str = Depends(get_current_user_id)):
    profile_data = mongodb_service.get_profile(current_user_id)
    if not profile_data:
        raise HTTPException(status_code=404, detail="Profile not found")
    return CoreBehaviorProfile(**profile_data)
```

---

#### 2. GET `/api/v1/profile/me/llm-context`

**Purpose**: Optimized endpoint for LLM system prompt injection

**Rationale**:
- Current `/profile/{user_id}` returns **full profile** with embeddings, timestamps, all evidence
- LLMs need **minimal, focused data** to reduce token usage
- Need structured format specifically designed for prompt injection

**Response Schema**:
```json
{
  "user_id": "user_123",
  "archetype": "Pragmatic Analytical Thinker",
  "primary_behaviors": [
    {
      "label": "Analytical Problem-Solving",
      "description": "User consistently approaches problems through logical analysis",
      "confidence": 0.85,
      "observed_count": 12
    }
  ],
  "secondary_behaviors": [
    {
      "label": "Documentation Preference",
      "confidence": 0.65,
      "observed_count": 5
    }
  ],
  "summary": "User exhibits strong analytical tendencies with emphasis on systematic problem-solving. Secondary traits include preference for detailed documentation and iterative refinement."
}
```

**Key Features**:
- No embeddings or timestamps
- Only PRIMARY and SECONDARY tiers
- Includes human-readable summary for LLM consumption
- Token-efficient: ~200-500 tokens vs ~2000+ for full profile

**Implementation**:
```python
@router.get(
    "/profile/{user_id}/llm-context",
    response_model=LLMContextResponse,
    summary="Get LLM-optimized behavior profile",
    description="Returns minimal, token-efficient profile for LLM system prompts"
)
async def get_llm_context(user_id: str):
    """
    Optimized for LLM injection:
    - No embeddings/timestamps
    - Only PRIMARY/SECONDARY behaviors
    - Includes human-readable summary
    """
    profile_data = mongodb_service.get_profile(user_id)
    
    if not profile_data:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Extract and format for LLM
    primary = [
        {
            "label": c["canonical_label"],
            "description": c.get("cluster_name", c["canonical_label"]),
            "confidence": c["confidence"],
            "observed_count": c["cluster_size"]
        }
        for c in profile_data.get("behavior_clusters", [])
        if c.get("tier") == "PRIMARY"
    ]
    
    secondary = [
        {
            "label": c["canonical_label"],
            "confidence": c["confidence"],
            "observed_count": c["cluster_size"]
        }
        for c in profile_data.get("behavior_clusters", [])
        if c.get("tier") == "SECONDARY"
    ]
    
    # Generate summary
    summary = f"User exhibits {len(primary)} primary behavioral patterns..."
    
    return {
        "user_id": user_id,
        "archetype": profile_data.get("archetype", "Unknown"),
        "primary_behaviors": primary,
        "secondary_behaviors": secondary,
        "summary": summary
    }
```

---

### 2. GET `/api/v1/profile/{user_id}/summary`

**Purpose**: Ultra-minimal endpoint for quick lookups (e.g., dashboards)

**Response Schema**:
```json
{
  "user_id": "user_123",
  "archetype": "Pragmatic Analytical Thinker",
  "behavior_count": {
    "primary": 3,
    "secondary": 5,
    "total": 8
  },
  "last_updated": "2024-01-15T10:30:00Z",
  "confidence_avg": 0.72
}
```

**Use Cases**:
- Dashboard widgets
- User list views
- Quick status checks

---

### 3. POST `/api/v1/profile/{user_id}/analyze-and-save`

**Purpose**: Run cluster-centric analysis and persist results to database

**Current Gap**: `analyze-behaviors-cluster-centric` has `store_in_dbs=False` hardcoded for testing

**Request Schema**:
```json
{
  "user_id": "user_123",
  "behaviors": [...],  // BehaviorModel[]
  "prompts": [...],    // PromptModel[]
  "generate_archetype": true,
  "force_reanalysis": false  // Skip if recent profile exists
}
```

**Response Schema**:
```json
{
  "success": true,
  "user_id": "user_123",
  "clusters_detected": 5,
  "primary_count": 2,
  "secondary_count": 3,
  "archetype": "Pragmatic Analytical Thinker",
  "profile_id": "507f1f77bcf86cd799439011"
}
```

**Implementation**:
```python
@router.post(
    "/profile/{user_id}/analyze-and-save",
    response_model=AnalyzeAndSaveResponse,
    summary="Analyze behaviors and persist profile to database"
)
async def analyze_and_save(user_id: str, request: AnalyzeBehaviorsRequest):
    """
    Runs cluster-centric analysis and saves CoreBehaviorProfile to MongoDB
    """
    # Run analysis
    profile = await cluster_analysis_pipeline.analyze_observations(
        user_id=user_id,
        observations=request.behaviors,
        prompts=request.prompts,
        generate_archetype=request.generate_archetype,
        store_in_dbs=True  # SAVE TO DATABASE
    )
    
    # Verify save
    saved_profile = mongodb_service.get_profile(user_id)
    if not saved_profile:
        raise HTTPException(status_code=500, detail="Profile save failed")
    
    return {
        "success": True,
        "user_id": user_id,
        "clusters_detected": len(profile.behavior_clusters),
        "primary_count": sum(1 for c in profile.behavior_clusters if c.tier == "PRIMARY"),
        "secondary_count": sum(1 for c in profile.behavior_clusters if c.tier == "SECONDARY"),
        "archetype": profile.archetype,
        "profile_id": str(saved_profile["_id"])
    }
```

---

## Database Persistence

### Current Implementation

**File**: `src/database/mongodb_service.py` (Lines 175-203)

**Method**: `insert_profile(profile: CoreBehaviorProfile) -> bool`

```python
def insert_profile(self, profile: CoreBehaviorProfile) -> bool:
    """Insert or update a core behavior profile"""
    try:
        self.db.core_behavior_profiles.replace_one(
            {"user_id": profile.user_id},
            profile.model_dump(),
            upsert=True
        )
        return True
    except PyMongoError as e:
        logger.error(f"Error inserting profile: {e}")
        return False
```

### Verification

✅ **VERIFIED**: Database save functionality exists and works with cluster-centric model

**Evidence**:
1. Method accepts `CoreBehaviorProfile` Pydantic model
2. Uses `replace_one` with `upsert=True` for idempotent saves
3. Converts to dict via `model_dump()` for MongoDB compatibility
4. Returns boolean success/failure

**Schema Compatibility**:
```python
# CoreBehaviorProfile (schemas.py)
class CoreBehaviorProfile(BaseModel):
    user_id: str
    behavior_clusters: List[BehaviorCluster]  # Cluster-centric structure
    archetype: Optional[str]
    analysis_metadata: AnalysisMetadata
```

**Collection**: `core_behavior_profiles`

**Indexes** (recommended):
```javascript
db.core_behavior_profiles.createIndex({ "user_id": 1 }, { unique: true })
db.core_behavior_profiles.createIndex({ "analysis_metadata.analysis_timestamp": -1 })
```

### Integration with Cluster Analysis Pipeline

**File**: `src/services/cluster_analysis_pipeline.py`

**Current Usage**:
```python
# Line ~180-190 (approximate)
if store_in_dbs:
    # Save clusters to MongoDB
    for cluster in behavior_clusters:
        # ... save cluster data ...
    
    # Save profile
    mongodb_service.insert_profile(profile)
```

**Status**: ✅ Already integrated in pipeline, but needs testing with `store_in_dbs=True`

---

## Migration Roadmap

### Phase 1: Deprecation Warnings (Current)
- [x] Mark old endpoints with deprecation warnings
- [x] Add deprecation notices to `analysis_pipeline.py`
- [x] Update documentation

### Phase 2: New Endpoint Implementation (Next)
- [ ] Implement GET `/profile/{user_id}/llm-context`
- [ ] Implement GET `/profile/{user_id}/summary`
- [ ] Implement POST `/profile/{user_id}/analyze-and-save`
- [ ] Add Pydantic schemas: `LLMContextResponse`, `AnalyzeAndSaveResponse`
- [ ] Test database save with `store_in_dbs=True`

### Phase 3: Client Migration (2-4 weeks)
- [ ] Update frontend to use `/llm-context` for AI features
- [ ] Migrate all analysis calls to `/analyze-behaviors-cluster-centric`
- [ ] Update dashboards to use `/summary` endpoint
- [ ] Monitor usage metrics for old endpoints

### Phase 4: Removal (After 100% migration)
- [ ] Remove POST `/update-behavior`
- [ ] Remove POST `/analyze-behaviors-from-storage`
- [ ] Remove POST `/analyze-behaviors`
- [ ] Archive `src/services/analysis_pipeline.py`
- [ ] Clean up deprecated methods in `calculation_engine.py`

---

## Testing Checklist

### New Endpoints
- [ ] GET `/profile/{user_id}/llm-context` returns < 500 tokens
- [ ] GET `/profile/{user_id}/summary` returns basic stats
- [ ] POST `/profile/{user_id}/analyze-and-save` persists to MongoDB
- [ ] Verify `insert_profile()` handles cluster-based `CoreBehaviorProfile`
- [ ] Test idempotency: calling save twice doesn't create duplicates

### Database
- [ ] Verify `core_behavior_profiles` collection structure
- [ ] Test profile retrieval after save
- [ ] Verify `behavior_clusters[]` field structure in MongoDB
- [ ] Test profile updates (archetype assignment after initial save)

### Deprecated Endpoints (Remove After Testing)
- [ ] Confirm no production traffic to `/update-behavior`
- [ ] Confirm no production traffic to old analysis endpoints
- [ ] Archive or remove deprecated code

---

## Response Schema Changes

### Old Schema (Observation-Centric)
```json
{
  "user_id": "user_123",
  "canonical_behaviors": [
    {
      "behavior_id": "beh_001",
      "behavior_text": "I need detailed documentation",
      "behavior_weight": 0.85,
      "cbi_score": 0.72,
      "reinforcement_count": 5
    }
  ]
}
```

### New Schema (Cluster-Centric)
```json
{
  "user_id": "user_123",
  "behavior_clusters": [
    {
      "cluster_id": 0,
      "canonical_label": "Documentation Preference",
      "cluster_name": "Strong Documentation and Explanation Needs",
      "tier": "PRIMARY",
      "cluster_strength": 0.85,
      "confidence": 0.72,
      "cluster_size": 8,
      "wording_variations": [
        "I need detailed documentation",
        "I prefer comprehensive guides",
        "I like thorough explanations"
      ],
      "all_prompt_ids": ["p1", "p2", "p5", ...],
      "first_seen": "2024-01-01T10:00:00Z",
      "last_seen": "2024-01-15T18:30:00Z"
    }
  ],
  "archetype": "Detail-Oriented Analyst"
}
```

**Key Differences**:
- `canonical_behaviors[]` → `behavior_clusters[]`
- Single text → `wording_variations[]`
- `behavior_weight` → `cluster_strength`
- `cbi_score` → `confidence`
- Added: `canonical_label`, `cluster_name`, `tier`, temporal data

---

## Configuration

### Threshold Externalization (TODO)

**Current Issue**: Thresholds hardcoded in `calculation_engine.py`

```python
# Line ~250 (approximate)
def assign_tier(cluster_strength: float) -> str:
    if cluster_strength >= 0.80:  # ❌ Hardcoded
        return "PRIMARY"
    elif cluster_strength >= 0.50:  # ❌ Hardcoded
        return "SECONDARY"
    else:
        return "NOISE"
```

**Recommended Fix**: Move to `src/config.py`

```python
# config.py
class Settings(BaseSettings):
    # ... existing settings ...
    
    # Cluster tier thresholds
    CLUSTER_PRIMARY_THRESHOLD: float = 0.80
    CLUSTER_SECONDARY_THRESHOLD: float = 0.50
    
    # Temporal decay
    TEMPORAL_DECAY_RATE: float = 0.05
    
    # LLM token limits
    LLM_CONTEXT_MAX_TOKENS: int = 500
    LLM_CANONICAL_LABEL_MAX_TOKENS: int = 20
```

---

## Error Handling

### Standard Error Responses

**404 Not Found**:
```json
{
  "detail": "No profile found for user user_123"
}
```

**500 Internal Server Error**:
```json
{
  "detail": "Cluster-centric analysis failed: <error_message>"
}
```

**400 Bad Request**:
```json
{
  "detail": "Invalid request: behaviors array is empty"
}
```

---

## Appendix: API Migration Checklist

- [ ] **Phase 1**: Implement 3 new endpoints (llm-context, summary, analyze-and-save)
- [ ] **Phase 2**: Add Pydantic response models
- [ ] **Phase 3**: Test database save with cluster-based profiles
- [ ] **Phase 4**: Externalize thresholds to config.py
- [ ] **Phase 5**: Update frontend clients to new endpoints
- [ ] **Phase 6**: Remove deprecated endpoints (update-behavior, old analysis endpoints)
- [ ] **Phase 7**: Archive analysis_pipeline.py and deprecated calculation methods
- [ ] **Phase 8**: Update PROJECT_STATUS.md with completion status
