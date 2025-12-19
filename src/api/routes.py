"""
FastAPI routes for CBIE System
Implements 5 API endpoints as specified in MVP documentation
"""
from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Any
import logging

from src.models.schemas import (
    AnalyzeBehaviorsRequest,
    AnalyzeBehaviorsResponse,
    CoreBehaviorProfile,
    UpdateBehaviorRequest,
    AssignArchetypeRequest,
    AssignArchetypeResponse,
    ListCoreBehaviorsResponse,
    BehaviorObservation
)
from src.services.analysis_pipeline import analysis_pipeline
from src.services.cluster_analysis_pipeline import cluster_analysis_pipeline
from src.database.mongodb_service import mongodb_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/analyze-behaviors-from-storage",
    response_model=AnalyzeBehaviorsResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze behaviors from existing storage (NORMAL SCENARIO)",
    description="Fetch behaviors from Qdrant (with embeddings) and prompts from MongoDB, "
                "then run analysis pipeline. This is the typical production workflow."
)
async def analyze_behaviors_from_storage(user_id: str):
    """
    Analyze user behaviors from existing storage (PRODUCTION SCENARIO)
    
    In normal operation:
    - Behaviors are stored in Qdrant vector database (with embeddings)
    - Prompts are stored in MongoDB
    
    This endpoint:
    1. Fetches behaviors from Qdrant (already embedded)
    2. Fetches prompts from MongoDB
    3. Calculates behavior weights (BW, ABW)
    4. Performs clustering using existing embeddings
    5. Assigns tiers (PRIMARY/SECONDARY/NOISE)
    6. Calculates temporal metrics
    7. Generates archetype (optional)
    8. Stores and returns profile
    """
    try:
        logger.info(f"Received analysis request from storage for user {user_id}")
        
        # Run cluster-centric analysis pipeline from storage
        profile = await cluster_analysis_pipeline.analyze_behaviors_from_storage(
            user_id=user_id,
            generate_archetype=True
        )
        
        return profile
        
    except ValueError as e:
        logger.error(f"User data not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in analyze_behaviors_from_storage: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


@router.post(
    "/analyze-behaviors",
    response_model=AnalyzeBehaviorsResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze new behaviors and store in databases",
    description="Import new behaviors and prompts, generate embeddings, store everything, "
                "then run analysis. Use this for test data or bulk imports."
)
async def analyze_behaviors(request: AnalyzeBehaviorsRequest):
    """
    Analyze user behaviors with new data (TEST/IMPORT SCENARIO)
    
    This endpoint is used for:
    - Testing with sample data
    - Bulk importing new behaviors
    - Initial data setup
    
    It will:
    1. Store prompts in MongoDB
    2. Generate embeddings for behaviors
    3. Store behaviors with embeddings in Qdrant
    4. Store behavior metadata in MongoDB
    5. Calculate behavior weights (BW, ABW)
    6. Perform clustering (HDBSCAN)
    7. Assign tiers (PRIMARY/SECONDARY/NOISE)
    8. Calculate temporal metrics
    9. Generate archetype (optional)
    10. Store and return profile
    """
    try:
        logger.info(
            f"Received analyze request with new data for user {request.user_id}: "
            f"{len(request.behaviors)} behaviors, {len(request.prompts)} prompts"
        )
        
        # Run analysis pipeline with storage
        profile = await analysis_pipeline.analyze_behaviors(
            user_id=request.user_id,
            behaviors=request.behaviors,
            prompts=request.prompts,
            generate_archetype=True,
            store_in_dbs=True
        )
        
        return profile
        
    except Exception as e:
        logger.error(f"Error in analyze_behaviors: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


@router.get(
    "/get-user-profile/{user_id}",
    response_model=CoreBehaviorProfile,
    status_code=status.HTTP_200_OK,
    summary="Retrieve user's core behavior profile",
    description="Get existing core behavior profile for a specific user"
)
async def get_user_profile(user_id: str):
    """
    Retrieve a user's existing core behavior profile from database
    """
    try:
        logger.info(f"Fetching profile for user {user_id}")
        
        profile_data = mongodb_service.get_profile(user_id)
        
        if not profile_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No profile found for user {user_id}"
            )
        
        # Convert to Pydantic model
        profile = CoreBehaviorProfile(**profile_data)
        
        return profile
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve profile: {str(e)}"
        )


@router.get(
    "/list-core-behaviors/{user_id}",
    response_model=ListCoreBehaviorsResponse,
    status_code=status.HTTP_200_OK,
    summary="List canonical core behaviors for a user",
    description="Return canonical behaviors for downstream context usage"
)
async def list_core_behaviors(user_id: str):
    """
    Get list of canonical core behaviors (primary and secondary) for a user
    """
    try:
        logger.info(f"Listing core behaviors for user {user_id}")
        
        profile_data = mongodb_service.get_profile(user_id)
        
        if not profile_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No profile found for user {user_id}"
            )
        
        # Extract canonical behaviors
        canonical_behaviors = []
        
        for behavior in profile_data.get("primary_behaviors", []):
            canonical_behaviors.append({
                "behavior_id": behavior["behavior_id"],
                "behavior_text": behavior["behavior_text"],
                "tier": "PRIMARY"
            })
        
        for behavior in profile_data.get("secondary_behaviors", []):
            canonical_behaviors.append({
                "behavior_id": behavior["behavior_id"],
                "behavior_text": behavior["behavior_text"],
                "tier": "SECONDARY"
            })
        
        return ListCoreBehaviorsResponse(
            user_id=user_id,
            canonical_behaviors=canonical_behaviors
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing behaviors: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list behaviors: {str(e)}"
        )


@router.post(
    "/update-behavior",
    response_model=BehaviorObservation,
    status_code=status.HTTP_200_OK,
    summary="Update behavior metadata",
    description="Update reinforcement, credibility, or timestamps of a behavior"
)
async def update_behavior(request: UpdateBehaviorRequest):
    """
    Update behavior document with new values
    
    Allowed updates:
    - reinforcement_count
    - credibility
    - clarity_score
    - extraction_confidence
    - last_seen
    - decay_rate
    """
    try:
        logger.info(f"Updating behavior {request.behavior_id}: {request.updates}")
        
        # Validate behavior exists
        behavior_data = mongodb_service.get_behavior(request.behavior_id)
        if not behavior_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Behavior {request.behavior_id} not found"
            )
        
        # Update behavior
        success = await analysis_pipeline.update_behavior_metrics(
            request.behavior_id,
            request.updates
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update behavior"
            )
        
        # Fetch updated behavior
        updated_data = mongodb_service.get_behavior(request.behavior_id)
        updated_behavior = BehaviorObservation(**updated_data)
        
        return updated_behavior
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating behavior: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Update failed: {str(e)}"
        )


@router.post(
    "/assign-archetype",
    response_model=AssignArchetypeResponse,
    status_code=status.HTTP_200_OK,
    summary="Assign behavioral archetype label",
    description="Use LLM to generate and assign archetype label to user profile"
)
async def assign_archetype(request: AssignArchetypeRequest):
    """
    Generate behavioral archetype label using LLM
    
    Can provide canonical behaviors explicitly, or will fetch from existing profile
    """
    try:
        logger.info(
            f"Assigning archetype for user {request.user_id} "
            f"with {len(request.canonical_behaviors)} behaviors"
        )
        
        # Generate and assign archetype
        archetype = await analysis_pipeline.assign_archetype_to_profile(
            user_id=request.user_id,
            canonical_behaviors=request.canonical_behaviors if request.canonical_behaviors else None
        )
        
        if not archetype:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate archetype"
            )
        
        return AssignArchetypeResponse(
            user_id=request.user_id,
            archetype=archetype
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error assigning archetype: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Archetype assignment failed: {str(e)}"
        )


@router.post(
    "/analyze-behaviors-cluster-centric",
    response_model=CoreBehaviorProfile,
    status_code=status.HTTP_200_OK,
    summary="[NEW] Analyze behaviors using cluster-centric pipeline",
    description="Test the NEW cluster-centric implementation where clusters are primary entities. "
                "Returns behavior_clusters[] with full aggregated evidence."
)
async def analyze_behaviors_cluster_centric(request: AnalyzeBehaviorsRequest):
    """
    NEW CLUSTER-CENTRIC analysis pipeline
    
    Key differences from old pipeline:
    - Clusters are PRIMARY entities (not individual behaviors)
    - ALL observations in clusters are preserved
    - Scoring based on cluster_strength (log-scaled with recency)
    - Confidence from cluster consistency, not single observation
    - Returns behavior_clusters[] with full evidence aggregation
    
    Response includes:
    - behavior_clusters[] - list of BehaviorCluster objects
    - Each cluster contains:
      * canonical_label (UI only)
      * cluster_strength (log(size) * mean_abw * recency)
      * confidence (consistency * reinforcement * clarity_trend)
      * observed_count (cluster_size)
      * wording_variations[] (all phrasings)
      * all_prompt_ids[] (evidence)
      * all_timestamps[] (temporal data)
      * first_seen, last_seen, days_active
      * tier (PRIMARY/SECONDARY/NOISE)
    """
    try:
        from src.services.cluster_analysis_pipeline import cluster_analysis_pipeline
        from src.models.schemas import BehaviorObservation, PromptModel
        import time
        
        logger.info(
            f"[CLUSTER-CENTRIC] Analyzing {len(request.behaviors)} observations "
            f"and {len(request.prompts)} prompts for user {request.user_id}"
        )
        
        # Convert BehaviorModel to BehaviorObservation
        observations = []
        for b in request.behaviors:
            obs = BehaviorObservation(
                observation_id=b.behavior_id,
                behavior_text=b.behavior_text,
                credibility=b.credibility,
                clarity_score=b.clarity_score,
                extraction_confidence=b.extraction_confidence,
                timestamp=b.created_at,
                prompt_id=b.prompt_history_ids[0] if b.prompt_history_ids else 'unknown',
                decay_rate=b.decay_rate,
                user_id=b.user_id,
                session_id=b.session_id
            )
            observations.append(obs)
        
        # Run cluster-centric analysis
        profile = await cluster_analysis_pipeline.analyze_observations(
            user_id=request.user_id,
            observations=observations,
            prompts=request.prompts,
            generate_archetype=True,
            store_in_dbs=False  # Don't store yet - this is for testing
        )
        
        logger.info(
            f"[CLUSTER-CENTRIC] Analysis complete: {len(profile.behavior_clusters)} clusters formed"
        )
        
        return profile
        
    except Exception as e:
        logger.error(f"Error in cluster-centric analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cluster-centric analysis failed: {str(e)}"
        )


# Health check endpoint
@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Check if API is running"
)
async def health_check():
    """Simple health check endpoint"""
    return {"status": "healthy", "service": "CBIE MVP"}
