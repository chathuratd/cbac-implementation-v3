"""
Pydantic schemas for CBIE data models
Based on CBIE MVP Documentation specifications
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class TierEnum(str, Enum):
    """Behavior tier classification"""
    PRIMARY = "PRIMARY"
    SECONDARY = "SECONDARY"
    NOISE = "NOISE"


class BehaviorModel(BaseModel):
    """Individual behavior object with metadata"""
    behavior_id: str
    behavior_text: str
    credibility: float = Field(ge=0.0, le=1.0)
    clarity_score: float = Field(ge=0.0, le=1.0)
    extraction_confidence: float = Field(ge=0.0, le=1.0)
    reinforcement_count: int = Field(ge=0)
    decay_rate: float = Field(ge=0.0)
    created_at: int  # Unix timestamp
    last_seen: int   # Unix timestamp
    prompt_history_ids: List[str]
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "behavior_id": "beh_3ccbf2b2",
                "behavior_text": "prefers visual learning",
                "credibility": 0.95,
                "clarity_score": 0.76,
                "extraction_confidence": 0.77,
                "reinforcement_count": 17,
                "decay_rate": 0.012,
                "created_at": 1765741962,
                "last_seen": 1765741962,
                "prompt_history_ids": ["prompt_1", "prompt_2"],
                "user_id": "user_348",
                "session_id": "session_7732"
            }
        }


class PromptModel(BaseModel):
    """User prompt object"""
    prompt_id: str
    prompt_text: str
    timestamp: int  # Unix timestamp
    tokens: Optional[float] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "prompt_id": "prompt_1",
                "prompt_text": "Visualize the HTTP request lifecycle",
                "timestamp": 1761637013,
                "tokens": 12.0,
                "user_id": "user_348",
                "session_id": "session_7732"
            }
        }


class TemporalSpan(BaseModel):
    """Temporal metrics for a behavior"""
    first_seen: int
    last_seen: int
    days_active: float


class CanonicalBehavior(BaseModel):
    """Canonical behavior representing a cluster"""
    behavior_id: str
    behavior_text: str
    cluster_id: str
    cbi_original: float  # Individual ABW
    cluster_cbi: float   # Cluster average
    tier: TierEnum
    temporal_span: TemporalSpan


class ProfileStatistics(BaseModel):
    """Statistics for core behavior profile"""
    total_behaviors_analyzed: int
    clusters_formed: int
    total_prompts_analyzed: int
    analysis_time_span_days: float


class CoreBehaviorProfile(BaseModel):
    """Complete user core behavior profile"""
    user_id: str
    generated_at: int  # Unix timestamp
    primary_behaviors: List[CanonicalBehavior] = []
    secondary_behaviors: List[CanonicalBehavior] = []
    archetype: Optional[str] = None
    statistics: ProfileStatistics
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_348",
                "generated_at": 1766000000,
                "primary_behaviors": [],
                "secondary_behaviors": [],
                "archetype": "Visual Learner",
                "statistics": {
                    "total_behaviors_analyzed": 5,
                    "clusters_formed": 3,
                    "total_prompts_analyzed": 50,
                    "analysis_time_span_days": 60
                }
            }
        }


class ClusterModel(BaseModel):
    """Cluster metadata"""
    cluster_id: str
    user_id: str
    behavior_ids: List[str]
    canonical_behavior_id: str
    cluster_cbi: float
    tier: TierEnum
    created_at: int


# API Request/Response Models

class AnalyzeBehaviorsRequest(BaseModel):
    """Request body for /analyze-behaviors endpoint"""
    user_id: str
    behaviors: List[BehaviorModel]
    prompts: List[PromptModel]


class AnalyzeBehaviorsResponse(CoreBehaviorProfile):
    """Response for /analyze-behaviors endpoint"""
    pass


class UpdateBehaviorRequest(BaseModel):
    """Request body for /update-behavior endpoint"""
    behavior_id: str
    updates: Dict[str, Any]


class AssignArchetypeRequest(BaseModel):
    """Request body for /assign-archetype endpoint"""
    user_id: str
    canonical_behaviors: List[str]  # List of behavior texts


class AssignArchetypeResponse(BaseModel):
    """Response for /assign-archetype endpoint"""
    user_id: str
    archetype: str


class ListCoreBehaviorsResponse(BaseModel):
    """Response for /list-core-behaviors endpoint"""
    user_id: str
    canonical_behaviors: List[Dict[str, str]]
