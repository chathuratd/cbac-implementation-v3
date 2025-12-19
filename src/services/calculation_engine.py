"""
Calculation Engine for CBIE System
Implements all formulas from MVP documentation
"""
import math
from typing import List, Dict, Any, Optional
import time
import logging

from src.config import settings
from src.models.schemas import BehaviorModel, TemporalSpan, TierEnum

logger = logging.getLogger(__name__)


class CalculationEngine:
    """Engine for calculating behavior weights and metrics"""
    
    def __init__(self):
        # Formula parameters from settings
        self.alpha = settings.alpha  # 0.35
        self.beta = settings.beta    # 0.40
        self.gamma = settings.gamma  # 0.25
        self.reinforcement_multiplier = settings.reinforcement_multiplier  # 0.01
        self.primary_threshold = settings.primary_threshold  # 1.0
        self.secondary_threshold = settings.secondary_threshold  # 0.7
    
    def calculate_behavior_weight(
        self,
        credibility: float,
        clarity_score: float,
        extraction_confidence: float
    ) -> float:
        """
        Calculate Behavior Weight (BW)
        
        Formula: BW = credibility^α × clarity_score^β × extraction_confidence^γ
        
        Args:
            credibility: Trustworthiness (0-1)
            clarity_score: Explicitness (0-1)
            extraction_confidence: Model confidence (0-1)
            
        Returns:
            float: Behavior Weight
        """
        bw = (
            math.pow(credibility, self.alpha) *
            math.pow(clarity_score, self.beta) *
            math.pow(extraction_confidence, self.gamma)
        )
        
        logger.debug(
            f"BW = {credibility}^{self.alpha} × {clarity_score}^{self.beta} × "
            f"{extraction_confidence}^{self.gamma} = {bw:.6f}"
        )
        
        return bw
    
    def calculate_adjusted_behavior_weight(
        self,
        behavior_weight: float,
        reinforcement_count: int,
        decay_rate: float,
        days_since_last_seen: float
    ) -> float:
        """
        Calculate Adjusted Behavior Weight (ABW)
        
        Formula: ABW = BW × (1 + reinforcement_count × r) × e^(-decay_rate × days_since_last_seen)
        
        Args:
            behavior_weight: Base behavior weight (BW)
            reinforcement_count: Number of reinforcements
            decay_rate: Decay rate for this behavior
            days_since_last_seen: Days since behavior was last observed
            
        Returns:
            float: Adjusted Behavior Weight
        """
        reinforcement_factor = 1 + (reinforcement_count * self.reinforcement_multiplier)
        decay_factor = math.exp(-decay_rate * days_since_last_seen)
        
        abw = behavior_weight * reinforcement_factor * decay_factor
        
        logger.debug(
            f"ABW = {behavior_weight:.6f} × (1 + {reinforcement_count} × {self.reinforcement_multiplier}) × "
            f"e^(-{decay_rate} × {days_since_last_seen}) = {abw:.6f}"
        )
        
        return abw
    
    def calculate_days_since_last_seen(
        self,
        last_seen_timestamp: int,
        current_timestamp: Optional[int] = None
    ) -> float:
        """
        Calculate days since behavior was last seen
        
        Args:
            last_seen_timestamp: Unix timestamp of last observation
            current_timestamp: Current Unix timestamp (defaults to now)
            
        Returns:
            float: Days since last seen
        """
        if current_timestamp is None:
            current_timestamp = int(time.time())
        
        days = (current_timestamp - last_seen_timestamp) / 86400
        return max(0.0, days)  # Ensure non-negative
    
    def calculate_behavior_metrics(
        self,
        behavior: BehaviorModel,
        current_timestamp: Optional[int] = None
    ) -> Dict[str, float]:
        """
        Calculate both BW and ABW for a behavior
        
        Args:
            behavior: BehaviorModel instance
            current_timestamp: Current Unix timestamp (defaults to now). 
                              For historical data, this parameter is ignored and 
                              the behavior's own timeline (created_at to last_seen) is used.
            
        Returns:
            dict: Contains 'bw', 'abw', 'days_active'
        """
        # Calculate BW
        bw = self.calculate_behavior_weight(
            behavior.credibility,
            behavior.clarity_score,
            behavior.extraction_confidence
        )
        
        # Calculate days active (from created_at to last_seen)
        # This represents the behavior's actual activity period
        days_active = (behavior.last_seen - behavior.created_at) / 86400
        days_active = max(0.0, days_active)  # Ensure non-negative
        
        # Calculate ABW using the behavior's activity period
        abw = self.calculate_adjusted_behavior_weight(
            bw,
            behavior.reinforcement_count,
            behavior.decay_rate,
            days_active
        )
        
        return {
            "behavior_id": behavior.behavior_id,
            "bw": bw,
            "abw": abw,
            "days_active": days_active
        }
    
    def calculate_cluster_cbi(self, abw_list: List[float]) -> float:
        """
        Calculate Cluster Core Behavior Index (CBI)
        
        Formula: Cluster_CBI = Σ(ABW_i) / N
        
        Args:
            abw_list: List of Adjusted Behavior Weights in the cluster
            
        Returns:
            float: Cluster CBI (average of ABWs)
        """
        if not abw_list:
            return 0.0
        
        cluster_cbi = sum(abw_list) / len(abw_list)
        
        logger.debug(
            f"Cluster CBI = sum({abw_list}) / {len(abw_list)} = {cluster_cbi:.6f}"
        )
        
        return cluster_cbi
    
    def select_canonical_behavior(
        self,
        behaviors_with_abw: List[Dict[str, Any]]
    ) -> str:
        """
        Select canonical behavior from cluster (highest ABW)
        
        Args:
            behaviors_with_abw: List of dicts with 'behavior_id' and 'abw' keys
            
        Returns:
            str: behavior_id of canonical behavior
        """
        if not behaviors_with_abw:
            raise ValueError("Cannot select canonical from empty cluster")
        
        canonical = max(behaviors_with_abw, key=lambda x: x['abw'])
        
        logger.debug(
            f"Selected canonical behavior: {canonical['behavior_id']} "
            f"with ABW={canonical['abw']:.6f}"
        )
        
        return canonical['behavior_id']
    
    def assign_tier(self, cluster_cbi: float) -> TierEnum:
        """
        Assign tier based on Cluster CBI
        
        Rules:
        - PRIMARY: CBI ≥ 1.0
        - SECONDARY: 0.7 ≤ CBI < 1.0
        - NOISE: CBI < 0.7
        
        Args:
            cluster_cbi: Cluster Core Behavior Index
            
        Returns:
            TierEnum: PRIMARY, SECONDARY, or NOISE
        """
        if cluster_cbi >= self.primary_threshold:
            tier = TierEnum.PRIMARY
        elif cluster_cbi >= self.secondary_threshold:
            tier = TierEnum.SECONDARY
        else:
            tier = TierEnum.NOISE
        
        logger.debug(f"Cluster CBI {cluster_cbi:.6f} assigned to tier: {tier.value}")
        
        return tier
    
    def calculate_temporal_metrics(
        self,
        prompt_timestamps: List[int]
    ) -> TemporalSpan:
        """
        Calculate temporal metrics for a behavior cluster
        
        Args:
            prompt_timestamps: List of Unix timestamps from related prompts
            
        Returns:
            TemporalSpan: Contains first_seen, last_seen, days_active
        """
        if not prompt_timestamps:
            raise ValueError("Cannot calculate temporal metrics from empty list")
        
        first_seen = min(prompt_timestamps)
        last_seen = max(prompt_timestamps)
        days_active = (last_seen - first_seen) / 86400
        
        logger.debug(
            f"Temporal metrics: first={first_seen}, last={last_seen}, "
            f"days_active={days_active:.2f}"
        )
        
        return TemporalSpan(
            first_seen=first_seen,
            last_seen=last_seen,
            days_active=days_active
        )
    
    def calculate_all_metrics_batch(
        self,
        behaviors: List[BehaviorModel],
        current_timestamp: Optional[int] = None
    ) -> Dict[str, Dict[str, float]]:
        """
        Calculate BW and ABW for multiple behaviors
        
        Args:
            behaviors: List of BehaviorModel instances
            current_timestamp: Current Unix timestamp (defaults to now)
            
        Returns:
            dict: Maps behavior_id to metrics dict
        """
        metrics = {}
        
        for behavior in behaviors:
            behavior_metrics = self.calculate_behavior_metrics(
                behavior, 
                current_timestamp
            )
            metrics[behavior.behavior_id] = behavior_metrics
        
        logger.info(f"Calculated metrics for {len(behaviors)} behaviors")
        
        return metrics


# Global calculation engine instance
calculation_engine = CalculationEngine()
