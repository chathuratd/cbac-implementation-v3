"""
Test calculation engine formulas with examples from documentation
"""
import pytest
import math
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.services.calculation_engine import CalculationEngine
from src.models.schemas import BehaviorModel, TierEnum


def test_behavior_weight_calculation():
    """Test BW formula with documented example"""
    engine = CalculationEngine()
    
    # Example from documentation:
    # credibility=0.95, clarity=0.76, extraction_confidence=0.77
    # Expected: BW ≈ 0.858
    
    bw = engine.calculate_behavior_weight(
        credibility=0.95,
        clarity_score=0.76,
        extraction_confidence=0.77
    )
    
    assert abs(bw - 0.858) < 0.001, f"Expected BW ≈ 0.858, got {bw}"


def test_adjusted_behavior_weight_calculation():
    """Test ABW formula with documented example"""
    engine = CalculationEngine()
    
    # Example from documentation:
    # BW=0.858, reinforcement_count=17, decay_rate=0.012, days_since_last_seen=3
    # Expected: ABW ≈ 0.967
    
    abw = engine.calculate_adjusted_behavior_weight(
        behavior_weight=0.858,
        reinforcement_count=17,
        decay_rate=0.012,
        days_since_last_seen=3
    )
    
    assert abs(abw - 0.967) < 0.001, f"Expected ABW ≈ 0.967, got {abw}"


def test_cluster_cbi_calculation():
    """Test Cluster CBI formula"""
    engine = CalculationEngine()
    
    # Example: 3 behaviors with ABWs = [0.967, 0.945, 0.873]
    # Expected: CBI ≈ 0.928
    
    abw_list = [0.967, 0.945, 0.873]
    cbi = engine.calculate_cluster_cbi(abw_list)
    
    expected = sum(abw_list) / len(abw_list)
    assert abs(cbi - 0.928) < 0.001, f"Expected CBI ≈ 0.928, got {cbi}"
    assert abs(cbi - expected) < 0.0001


def test_tier_assignment():
    """Test tier classification thresholds"""
    engine = CalculationEngine()
    
    # PRIMARY: CBI ≥ 1.0
    assert engine.assign_tier(1.5) == TierEnum.PRIMARY
    assert engine.assign_tier(1.0) == TierEnum.PRIMARY
    
    # SECONDARY: 0.7 ≤ CBI < 1.0
    assert engine.assign_tier(0.9) == TierEnum.SECONDARY
    assert engine.assign_tier(0.7) == TierEnum.SECONDARY
    
    # NOISE: CBI < 0.7
    assert engine.assign_tier(0.5) == TierEnum.NOISE
    assert engine.assign_tier(0.0) == TierEnum.NOISE


def test_canonical_behavior_selection():
    """Test canonical behavior selection (highest ABW)"""
    engine = CalculationEngine()
    
    behaviors_with_abw = [
        {"behavior_id": "beh_1", "abw": 0.8},
        {"behavior_id": "beh_2", "abw": 0.95},
        {"behavior_id": "beh_3", "abw": 0.7}
    ]
    
    canonical_id = engine.select_canonical_behavior(behaviors_with_abw)
    
    assert canonical_id == "beh_2"


def test_days_since_last_seen():
    """Test days calculation"""
    engine = CalculationEngine()
    
    current = 1766000000
    last_seen = current - (3 * 86400)  # 3 days ago
    
    days = engine.calculate_days_since_last_seen(last_seen, current)
    
    assert abs(days - 3.0) < 0.001


def test_complete_behavior_metrics():
    """Test complete metrics calculation for a behavior"""
    engine = CalculationEngine()
    
    behavior = BehaviorModel(
        behavior_id="beh_test",
        behavior_text="test behavior",
        credibility=0.95,
        clarity_score=0.76,
        extraction_confidence=0.77,
        reinforcement_count=17,
        decay_rate=0.012,
        created_at=1765741962,
        last_seen=1765741962,
        prompt_history_ids=["p1", "p2"]
    )
    
    current_timestamp = behavior.last_seen + (3 * 86400)  # 3 days later
    
    metrics = engine.calculate_behavior_metrics(behavior, current_timestamp)
    
    assert "bw" in metrics
    assert "abw" in metrics
    assert "days_since_last_seen" in metrics
    
    # Verify BW calculation
    assert abs(metrics["bw"] - 0.858) < 0.001
    
    # Verify days
    assert abs(metrics["days_since_last_seen"] - 3.0) < 0.001


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
