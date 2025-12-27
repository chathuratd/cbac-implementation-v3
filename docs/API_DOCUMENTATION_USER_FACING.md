# API Documentation - Cluster-Centric Core Behavior Detection (User-Facing)

**Version**: 2.0 (Cluster-Centric, User-Facing)  
**Last Updated**: December 27, 2025  
**Status**: Migration in Progress

---

## Table of Contents

1. [Overview](#overview)
2. [User-Facing Architecture](#user-facing-architecture)
3. [Current API Status](#current-api-status)
4. [APIs to Remove](#apis-to-remove)
5. [APIs to Add](#apis-to-add)
6. [User Management APIs](#user-management-apis)
7. [Database Persistence](#database-persistence)
8. [Migration Roadmap](#migration-roadmap)

---

## Overview

This document outlines the API migration from the **observation-centric** model to the **cluster-centric** architecture. The new design treats behavior clusters as primary entities, providing more stable and reliable core behavior profiles.

**IMPORTANT**: This is a **user-facing system**. Each user can view and manage their own behavior profile. APIs must enforce user-scoped access and provide user controls for data management.

### Architecture Change

**Old Model (Observation-Centric)**:
- Individual behavior observations were selected as "canonical"
- Profiles had 1:1 mapping between canonical_behaviors and observations
- Updates/deletes on individual observations (admin only)

**New Model (Cluster-Centric, User-Facing)**:
- Behavior clusters aggregate multiple observations
- Each cluster has canonical_label (synthesized), wording_variations[], evidence
- Observations are immutable by system, but **users can delete/hide incorrect behaviors**
- User-controlled data with privacy settings
- Each user manages their own profile

---

## User-Facing Architecture

### Design Principles

1. **User Ownership**: Users own their behavior data and can view/manage it
2. **Privacy First**: Users control what data is stored and visible
3. **Correction Mechanism**: Users can delete incorrect behaviors or report issues
4. **Transparency**: Users see exactly what behaviors are detected
5. **Configurability**: Users have settings to control analysis behavior

### User Roles

**End User** (Primary Role):
- View their own behavior profile
- Delete incorrect individual behaviors
- Hide specific clusters from their profile
- Report incorrectly detected behaviors
- Export their data (JSON/PDF)
- Configure privacy settings
- Pause behavior detection
- Request complete profile deletion (GDPR compliance)

**System** (Automated):
- Analyze user interactions to detect behaviors
- Generate clusters from observations
- Update profiles when new data arrives
- Respect user's deletion/hide preferences

### Data Ownership Model

- Each user has **one profile**: Identified by `user_id`
- Users access **their own data**: Via `/profile/me` endpoints
- Behaviors are **soft-deletable**: Users can mark as incorrect, system excludes from analysis
- Clusters are **hideable**: Users can hide entire clusters from their profile view
- Privacy controls: Users can pause analysis, export data, request deletion
- All user actions are logged for audit purposes

### Access Pattern

**User-Scoped Endpoints**: All user-facing endpoints use `/profile/me` pattern
- System automatically determines user context
- No explicit user_id required in URLs
- User can only access their own data

**Implementation Note**: Authentication/authorization is handled externally or via session management. APIs assume user context is already established.

---

## Current API Status

### Existing Endpoints

| Method | Endpoint | Access | Status | Notes |
|--------|----------|--------|--------|-------|
| **User Profile (Self-Access)** |
| GET | `/api/v1/profile/me` | User | 🆕 **NEW** | User's complete profile |
| GET | `/api/v1/profile/me/llm-context` | User | 🆕 **NEW** | LLM-optimized context |
| GET | `/api/v1/profile/me/summary` | User | 🆕 **NEW** | Profile summary |
| **User Behavior Management** |
| DELETE | `/api/v1/profile/me/behaviors/{behavior_id}` | User | 🆕 **NEW** | Delete incorrect behavior |
| POST | `/api/v1/profile/me/behaviors/{behavior_id}/report` | User | 🆕 **NEW** | Report incorrect detection |
| PUT | `/api/v1/profile/me/clusters/{cluster_id}/hide` | User | 🆕 **NEW** | Hide cluster from view |
| PUT | `/api/v1/profile/me/clusters/{cluster_id}/unhide` | User | 🆕 **NEW** | Unhide cluster |
| **User Settings & Privacy** |
| GET | `/api/v1/profile/me/settings` | User | 🆕 **NEW** | User preferences |
| PUT | `/api/v1/profile/me/settings` | User | 🆕 **NEW** | Update preferences |
| POST | `/api/v1/profile/me/export` | User | 🆕 **NEW** | Export user data (GDPR) |
| DELETE | `/api/v1/profile/me` | User | 🆕 **NEW** | Delete profile (GDPR) |
| PUT | `/api/v1/profile/me/pause` | User | 🆕 **NEW** | Pause behavior detection |
| PUT | `/api/v1/profile/me/resume` | User | 🆕 **NEW** | Resume behavior detection |
| **Admin Endpoints (Support)** |
| GET | `/api/v1/profile/{user_id}` | Admin | ✅ **ACTIVE** | Admin view any profile |
| GET | `/api/v1/user/{user_id}/core-behaviors` | Admin | ✅ **ACTIVE** | Admin view behaviors |
| **System Endpoints (Internal)** |
| POST | `/api/v1/analyze-behaviors-cluster-centric` | System | ✅ **ACTIVE** | Background analysis |
| POST | `/api/v1/assign-archetype` | System | ✅ **ACTIVE** | Automated archetype |
| **Deprecated Endpoints** |
| POST | `/api/v1/analyze-behaviors-from-storage` | System | ⚠️ **DEPRECATED** | Use cluster-centric |
| POST | `/api/v1/analyze-behaviors` | System | ⚠️ **DEPRECATED** | Use cluster-centric |
| POST | `/api/v1/update-behavior` | Admin | ❌ **REMOVE** | Violates immutability |
| **Public Endpoints** |
| GET | `/api/v1/health` | Public | ✅ **ACTIVE** | Health check |

---

## APIs to Remove

### 1. POST `/api/v1/update-behavior`

**Reason for Removal**: Violates immutability principle

**Why Remove**:
- Observations should be immutable snapshots
- User corrections handled via soft-delete (`DELETE /profile/me/behaviors/{id}`)
- Historical data must remain pristine
- Editing corrupts temporal analysis

**Migration Path**:
- Users delete incorrect behaviors via `/profile/me/behaviors/{behavior_id}` DELETE
- System creates new observations when behavior changes
- Clusters naturally adapt through re-clustering

---

### 2. POST `/api/v1/analyze-behaviors-from-storage` & POST `/api/v1/analyze-behaviors`

**Reason for Removal**: Uses deprecated observation-centric pipeline

**Migration Path**:
- Background system uses `/analyze-behaviors-cluster-centric`
- Users trigger re-analysis via UI (calls internal analysis API)

---

## APIs to Add

### User Profile APIs (Self-Access)

#### 1. GET `/api/v1/profile/me`

**Purpose**: Get authenticated user's complete behavior profile

**Access**: Authenticated User

**Headers**: `Authorization: Bearer <token>`

**Response Schema**:
```json
{
  "user_id": "user_123",
  "behavior_clusters": [
    {
      "cluster_id": 0,
      "canonical_label": "Analytical Problem-Solving",
      "cluster_name": "Systematic Analysis and Logical Reasoning",
      "tier": "PRIMARY",
      "cluster_strength": 0.85,
      "confidence": 0.72,
      "cluster_size": 12,
      "wording_variations": [...],
      "is_hidden": false,  // User-controlled visibility
      "first_seen": "2024-12-01T10:00:00Z",
      "last_seen": "2024-12-27T15:30:00Z",
      "days_active": 27
    }
  ],
  "archetype": "Pragmatic Analytical Thinker",
  "analysis_metadata": {
    "analysis_timestamp": "2024-12-27T10:00:00Z",
    "observation_count": 45,
    "cluster_count": 8,
    "active_clusters": 6  // Excludes hidden clusters
  },
  "user_settings": {
    "analysis_paused": false,
    "show_hidden_clusters": false
  }
}
```

**Implementation**:
```python
@router.get("/profile/me", response_model=CoreBehaviorProfile)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    profile_data = mongodb_service.get_profile(current_user.id)
    if not profile_data:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Apply user's visibility settings (hide clusters marked as hidden)
    profile_data["behavior_clusters"] = [
        c for c in profile_data.get("behavior_clusters", [])
        if not c.get("is_hidden", False)
    ]
    
    return CoreBehaviorProfile(**profile_data)
```

---

#### 5. GET `/api/v1/profile/me/llm-context`

**Purpose**: Get token-efficient profile for LLM system prompts

**Access**: Authenticated User

**Headers**: `Authorization: Bearer <token>`

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
  "summary": "User exhibits strong analytical tendencies with emphasis on systematic problem-solving. Secondary traits include preference for detailed documentation."
}
```

**Token Efficiency**: ~200-500 tokens (vs ~2000+ for full profile)

---

#### 6. GET `/api/v1/profile/me/summary`

**Purpose**: Get minimal profile summary for dashboard widgets

**Access**: Authenticated User

**Headers**: `Authorization: Bearer <token>`

**Response Schema**:
```json
{
  "user_id": "user_123",
  "archetype": "Pragmatic Analytical Thinker",
  "behavior_count": {
    "primary": 3,
    "secondary": 5,
    "total": 8,
    "hidden": 2  // User-hidden clusters
  },
  "last_updated": "2024-12-27T10:30:00Z",
  "confidence_avg": 0.72,
  "analysis_status": "active"  // or "paused"
}
```

---

## User Management APIs

### Behavior Deletion & Correction

#### 4. DELETE `/api/v1/profile/me/behaviors/{behavior_id}`

**Purpose**: Delete an incorrect behavior observation (soft-delete)

**Access**: User (session-based)

**Path Parameters**:
- `behavior_id`: ID of the behavior to delete

**Response Schema**:
```json
{
  "success": true,
  "message": "Behavior deleted successfully",
  "behavior_id": "beh_456",
  "action": "Profile will be recalculated automatically"
}
```

**Implementation**:
```python
@router.delete("/profile/me/behaviors/{behavior_id}")
async def delete_my_behavior(
    behavior_id: str,
    current_user: User = Depends(get_current_user)
):
    # Verify behavior belongs to user
    behavior = mongodb_service.get_behavior(behavior_id)
    if not behavior or behavior.get("user_id") != current_user.id:
        raise HTTPException(status_code=404, detail="Behavior not found")
    
    # Soft-delete: mark as user_deleted
    mongodb_service.update_behavior(behavior_id, {
        "is_active": False,
        "deleted_by_user": True,
        "deleted_at": datetime.utcnow()
    })
    
    # Trigger background re-analysis (exclude deleted behaviors)
    background_tasks.add_task(reanalyze_profile, current_user.id)
    
    return {
        "success": True,
        "message": "Behavior deleted successfully",
        "behavior_id": behavior_id,
        "action": "Profile will be recalculated automatically"
    }
```

**User Workflow**:
1. User views their profile
2. Sees incorrect behavior in wording_variations
3. Clicks "Delete" on that behavior
4. System soft-deletes (sets `is_active=False`)
5. Background job re-clusters remaining behaviors
6. Updated profile reflects deletion

---

#### 5. POST `/api/v1/profile/me/behaviors/{behavior_id}/report`

**Purpose**: Report an incorrectly detected behavior (for system improvement)

**Access**: User (session-based)

**Request Schema**:
```json
{
  "reason": "incorrect_detection",  // or "not_my_behavior", "offensive", "other"
  "comment": "This doesn't represent my behavior accurately"
}
```

**Response Schema**:
```json
{
  "success": true,
  "message": "Report submitted. Thank you for feedback!",
  "ticket_id": "report_789"
}
```

**Use Case**: User flags behavior as wrong, but doesn't delete (system learns from feedback)

---

### Cluster Visibility Control

#### 6. PUT `/api/v1/profile/me/clusters/{cluster_id}/hide`

**Purpose**: Hide an entire cluster from profile view

**Access**: User (session-based)

**Path Parameters**:
- `cluster_id`: ID of the cluster to hide

**Response Schema**:
```json
{
  "success": true,
  "message": "Cluster hidden from profile",
  "cluster_id": 2,
  "note": "You can unhide this cluster anytime from settings"
}
```

**Implementation**:
```python
@router.put("/profile/me/clusters/{cluster_id}/hide")
async def hide_cluster(
    cluster_id: int,
    current_user: User = Depends(get_current_user)
):
    # Update cluster visibility in profile
    result = mongodb_service.update_cluster_visibility(
        user_id=current_user.id,
        cluster_id=cluster_id,
        is_hidden=True
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="Cluster not found")
    
    return {
        "success": True,
        "message": "Cluster hidden from profile",
        "cluster_id": cluster_id,
        "note": "You can unhide this cluster anytime from settings"
    }
```

**User Workflow**:
1. User views PRIMARY/SECONDARY clusters
2. Finds cluster that's not relevant/private
3. Clicks "Hide this behavior"
4. Cluster disappears from profile view
5. Can unhide later from settings

---

#### 7. PUT `/api/v1/profile/me/clusters/{cluster_id}/unhide`

**Purpose**: Unhide a previously hidden cluster

**Access**: User (session-based)

**Response Schema**:
```json
{
  "success": true,
  "message": "Cluster is now visible",
  "cluster_id": 2
}
```

---

### User Settings & Privacy

#### 8. GET `/api/v1/profile/me/settings`

**Purpose**: Get user's behavior detection preferences

**Access**: User (session-based)

**Response Schema**:
```json
{
  "user_id": "user_123",
  "analysis_paused": false,
  "auto_analysis": true,
  "data_retention_days": 365,
  "show_hidden_clusters": false,
  "allow_archetype_generation": true,
  "privacy_level": "balanced",  // "minimal", "balanced", "detailed"
  "export_format": "json",  // "json", "pdf"
  "notification_preferences": {
    "new_cluster_detected": true,
    "archetype_updated": false
  }
}
```

---

#### 9. PUT `/api/v1/profile/me/settings`

**Purpose**: Update user preferences

**Access**: User (session-based)

**Request Schema**:
```json
{
  "auto_analysis": false,
  "privacy_level": "minimal",
  "notification_preferences": {
    "new_cluster_detected": false
  }
}
```

**Response Schema**:
```json
{
  "success": true,
  "message": "Settings updated successfully",
  "updated_fields": ["auto_analysis", "privacy_level", "notification_preferences"]
}
```

---

#### 10. POST `/api/v1/profile/me/export`

**Purpose**: Export user's complete behavior data (GDPR compliance)

**Access**: User (session-based)

**Request Schema**:
```json
{
  "format": "json",  // or "pdf", "csv"
  "include_raw_observations": true,
  "include_clusters": true,
  "include_settings": true
}
```

**Response**:
- **Content-Type**: `application/json` or `application/pdf`
- **Content-Disposition**: `attachment; filename="user_123_profile_2024-12-27.json"`

**Export Includes**:
- Complete behavior profile
- All observations (including deleted)
- Cluster history
- User settings
- Analysis metadata
- Audit log of user actions

---

#### 11. DELETE `/api/v1/profile/me`

**Purpose**: Permanently delete user profile (GDPR right to be forgotten)

**Access**: User (session-based)

**Request Schema**:
```json
{
  "confirm": true,
  "reason": "privacy_concerns"  // optional feedback
}
```

**Response Schema**:
```json
{
  "success": true,
  "message": "Profile deletion scheduled",
  "deletion_id": "del_789",
  "will_complete_by": "2024-12-28T10:00:00Z",
  "note": "Your data will be permanently deleted within 24 hours"
}
```

**Implementation**:
- Queues deletion job (30-day grace period)
- Sends confirmation email
- User can cancel within grace period
- After grace period: Permanent deletion

---

#### 12. PUT `/api/v1/profile/me/pause`

**Purpose**: Temporarily pause behavior detection

**Access**: User (session-based)

**Response Schema**:
```json
{
  "success": true,
  "message": "Behavior detection paused",
  "paused_at": "2024-12-27T10:00:00Z",
  "note": "No new behaviors will be detected until you resume"
}
```

**Use Case**: User wants to stop tracking temporarily

---

#### 13. PUT `/api/v1/profile/me/resume`

**Purpose**: Resume behavior detection after pause

**Access**: User (session-based)

**Response Schema**:
```json
{
  "success": true,
  "message": "Behavior detection resumed",
  "resumed_at": "2024-12-27T11:00:00Z"
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

### New Methods Needed

#### Behavior Soft-Delete
```python
def soft_delete_behavior(self, user_id: str, behavior_id: str) -> bool:
    """Mark behavior as deleted by user"""
    try:
        result = self.db.behaviors.update_one(
            {"observation_id": behavior_id, "user_id": user_id},
            {
                "$set": {
                    "is_active": False,
                    "deleted_by_user": True,
                    "deleted_at": datetime.utcnow()
                }
            }
        )
        return result.modified_count > 0
    except PyMongoError as e:
        logger.error(f"Error deleting behavior: {e}")
        return False
```

#### Cluster Visibility Control
```python
def update_cluster_visibility(
    self, 
    user_id: str, 
    cluster_id: int, 
    is_hidden: bool
) -> bool:
    """Update cluster visibility in profile"""
    try:
        result = self.db.core_behavior_profiles.update_one(
            {
                "user_id": user_id,
                "behavior_clusters.cluster_id": cluster_id
            },
            {
                "$set": {
                    "behavior_clusters.$.is_hidden": is_hidden,
                    "behavior_clusters.$.hidden_at": datetime.utcnow() if is_hidden else None
                }
            }
        )
        return result.modified_count > 0
    except PyMongoError as e:
        logger.error(f"Error updating cluster visibility: {e}")
        return False
```

#### User Settings
```python
def get_user_settings(self, user_id: str) -> Optional[Dict]:
    """Get user preferences"""
    try:
        return self.db.user_settings.find_one({"user_id": user_id})
    except PyMongoError as e:
        logger.error(f"Error fetching settings: {e}")
        return None

def update_user_settings(self, user_id: str, settings: Dict) -> bool:
    """Update user preferences"""
    try:
        self.db.user_settings.update_one(
            {"user_id": user_id},
            {"$set": settings},
            upsert=True
        )
        return True
    except PyMongoError as e:
        logger.error(f"Error updating settings: {e}")
        return False
```

### Schema Updates

#### Behavior Schema (Add User Control Fields)
```python
class BehaviorObservation(BaseModel):
    observation_id: str
    behavior_text: str
    # ... existing fields ...
    
    # User control fields
    is_active: bool = True  # False when user deletes
    deleted_by_user: bool = False
    deleted_at: Optional[datetime] = None
    reported_by_user: bool = False
    report_reason: Optional[str] = None
```

#### Cluster Schema (Add Visibility Field)
```python
class BehaviorCluster(BaseModel):
    cluster_id: int
    canonical_label: str
    # ... existing fields ...
    
    # User visibility control
    is_hidden: bool = False
    hidden_at: Optional[datetime] = None
```

#### User Settings Schema
```python
class UserSettings(BaseModel):
    user_id: str
    analysis_paused: bool = False
    auto_analysis: bool = True
    data_retention_days: int = 365
    show_hidden_clusters: bool = False
    allow_archetype_generation: bool = True
    privacy_level: str = "balanced"  # "minimal", "balanced", "detailed"
    export_format: str = "json"
    notification_preferences: Dict = {
        "new_cluster_detected": True,
        "archetype_updated": False
    }
    created_at: datetime
    updated_at: datetime
```

### Database Indexes (Updated)

```javascript
// Existing indexes
db.core_behavior_profiles.createIndex({ "user_id": 1 }, { unique: true })
db.core_behavior_profiles.createIndex({ "analysis_metadata.analysis_timestamp": -1 })

// New indexes for user management
db.behaviors.createIndex({ "user_id": 1, "is_active": 1 })
db.behaviors.createIndex({ "user_id": 1, "deleted_by_user": 1 })
db.user_settings.createIndex({ "user_id": 1 }, { unique: true })
db.audit_log.createIndex({ "user_id": 1, "action_timestamp": -1 })

// For soft-delete queries
db.behaviors.createIndex({ "user_id": 1, "is_active": 1, "timestamp": -1 })
```

---

## Migration Roadmap

### Phase 1: User Profile Endpoints (Weeks 1-2)
- [ ] Create `/profile/me` user-scoped endpoints
- [ ] Implement session-based user context resolution
- [ ] Test user data isolation
- [ ] Add rate limiting per session

### Phase 2: User Management Features (Weeks 3-4)
- [ ] Implement behavior deletion (soft-delete)
- [ ] Add cluster hide/unhide functionality
- [ ] Create behavior reporting endpoint
- [ ] Build user settings management
- [ ] Test user action workflows

### Phase 3: Privacy & Data Export (Weeks 5-6)
- [ ] Implement data export (JSON/PDF)
- [ ] Add profile deletion (GDPR)
- [ ] Create pause/resume functionality
- [ ] Build audit logging system
- [ ] Test GDPR compliance

### Phase 4: Frontend Integration (Weeks 7-8)
- [ ] Update frontend to use `/profile/me` endpoints
- [ ] Add behavior deletion UI
- [ ] Create settings screen
- [ ] Implement authentication flow
- [ ] Test end-to-end user workflows

### Phase 5: Deprecation Cleanup (Weeks 9-10)
- [ ] Remove admin-only endpoints (except support access)
- [ ] Archive deprecated pipeline code
- [ ] Clean up database schemas
- [ ] Update documentation

---

## API Migration Checklist

### Phase 1: User-Scoped Endpoints
- [ ] Implement GET `/profile/me`
- [ ] Implement GET `/profile/me/llm-context`
- [ ] Implement GET `/profile/me/summary`
- [ ] Test user data isolation

### Phase 3: User Management
- [ ] Implement DELETE `/profile/me/behaviors/{id}`
- [ ] Implement POST `/profile/me/behaviors/{id}/report`
- [ ] Implement PUT `/profile/me/clusters/{id}/hide`
- [ ] Implement PUT `/profile/me/clusters/{id}/unhide`
- [ ] Test deletion triggers re-analysis

### Phase 4: Settings & Privacy
- [ ] Implement GET/PUT `/profile/me/settings`
- [ ] Implement POST `/profile/me/export`
- [ ] Implement DELETE `/profile/me`
- [ ] Implement PUT `/profile/me/pause`
- [ ] Implement PUT `/profile/me/resume`
- [ ] Test GDPR compliance

### Phase 5: Database Updates
- [ ] Add `is_active`, `deleted_by_user` fields to behaviors
- [ ] Add `is_hidden` field to clusters
- [ ] Create `user_settings` collection
- [ ] Create `audit_log` collection
- [ ] Add necessary indexes

---

## Error Handling (User-Facing)

### User-Friendly Error Messages

| Error Code | API Response | User-Friendly Message |
|------------|--------------|----------------------|
| 401 | "Invalid credentials" | "Email or password is incorrect" |
| 403 | "Access denied" | "You don't have permission to view this" |
| 404 | "Behavior not found" | "This behavior no longer exists" |
| 409 | "Username already exists" | "This email is already registered" |
| 429 | "Rate limit exceeded" | "Too many requests. Please try again in a minute" |
| 500 | "Internal server error" | "Something went wrong. We're working on it!" |

### Validation Errors

```json
{
  "detail": {
    "field": "password",
    "error": "Password must be at least 8 characters"
  }
}
```

**User Message**: "Password must be at least 8 characters"

---

## Security & Compliance

### GDPR Compliance

1. **Right to Access**: Users can view all their data via `/profile/me`
2. **Right to Rectification**: Users can delete incorrect behaviors
3. **Right to Erasure**: Users can delete entire profile via DELETE `/profile/me`
4. **Right to Data Portability**: Users can export data via `/profile/me/export`
5. **Right to Object**: Users can pause detection via `/profile/me/pause`

### Data Retention

- Active profiles: Retained indefinitely
- Deleted behaviors: Soft-deleted, retained for 30 days then purged
- Audit logs: Retained for 2 years
- Deleted profiles: 30-day grace period, then permanent deletion

### Privacy Levels

**Minimal**:
- Store only PRIMARY behaviors
- No wording variations
- Auto-delete after 90 days

**Balanced** (default):
- Store PRIMARY and SECONDARY
- Limited wording variations (top 5)
- Retain for 365 days

**Detailed**:
- Store all behaviors
- All wording variations
- Indefinite retention (user choice)

---

## Appendix: Complete Endpoint List

### Public Endpoints
- GET `/api/v1/health`

### User Endpoints (Session-Based)
**Profile**:
- GET `/api/v1/profile/me`
- GET `/api/v1/profile/me/llm-context`
- GET `/api/v1/profile/me/summary`

**Behavior Management**:
- DELETE `/api/v1/profile/me/behaviors/{behavior_id}`
- POST `/api/v1/profile/me/behaviors/{behavior_id}/report`

**Cluster Control**:
- PUT `/api/v1/profile/me/clusters/{cluster_id}/hide`
- PUT `/api/v1/profile/me/clusters/{cluster_id}/unhide`

**Settings**:
- GET `/api/v1/profile/me/settings`
- PUT `/api/v1/profile/me/settings`

**Privacy**:
- POST `/api/v1/profile/me/export`
- DELETE `/api/v1/profile/me`
- PUT `/api/v1/profile/me/pause`
- PUT `/api/v1/profile/me/resume`

### Admin Endpoints (Admin Access)
- GET `/api/v1/profile/{user_id}`
- GET `/api/v1/user/{user_id}/core-behaviors`

### System Endpoints (Internal Only)
- POST `/api/v1/analyze-behaviors-cluster-centric`
- POST `/api/v1/assign-archetype`

---

**End of API Documentation**
