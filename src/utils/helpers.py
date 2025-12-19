"""Utility helper functions for CBIE system"""
import hashlib
import uuid
from typing import Optional
from datetime import datetime


def generate_behavior_id(prefix: str = "beh") -> str:
    """
    Generate a unique behavior ID
    
    Args:
        prefix: Prefix for the ID (default: "beh")
        
    Returns:
        str: Unique ID like "beh_3ccbf2b2"
    """
    unique_part = uuid.uuid4().hex[:8]
    return f"{prefix}_{unique_part}"


def generate_prompt_id(prefix: str = "prompt") -> str:
    """
    Generate a unique prompt ID
    
    Args:
        prefix: Prefix for the ID (default: "prompt")
        
    Returns:
        str: Unique ID like "prompt_d6bafd26"
    """
    unique_part = uuid.uuid4().hex[:8]
    return f"{prefix}_{unique_part}"


def generate_cluster_id(cluster_index: int) -> str:
    """
    Generate cluster ID from index
    
    Args:
        cluster_index: Cluster number from HDBSCAN
        
    Returns:
        str: Cluster ID like "cluster_0"
    """
    return f"cluster_{cluster_index}"


def unix_timestamp_to_datetime(timestamp: int) -> datetime:
    """
    Convert Unix timestamp to datetime object
    
    Args:
        timestamp: Unix timestamp (seconds)
        
    Returns:
        datetime: Datetime object
    """
    return datetime.fromtimestamp(timestamp)


def datetime_to_unix_timestamp(dt: datetime) -> int:
    """
    Convert datetime to Unix timestamp
    
    Args:
        dt: Datetime object
        
    Returns:
        int: Unix timestamp (seconds)
    """
    return int(dt.timestamp())


def hash_text(text: str) -> str:
    """
    Generate hash of text for deduplication
    
    Args:
        text: Input text
        
    Returns:
        str: SHA256 hash
    """
    return hashlib.sha256(text.encode()).hexdigest()


def validate_score(score: float, name: str = "score") -> bool:
    """
    Validate that a score is between 0 and 1
    
    Args:
        score: Score value
        name: Name of the score for error messages
        
    Returns:
        bool: True if valid
        
    Raises:
        ValueError: If score is out of range
    """
    if not 0.0 <= score <= 1.0:
        raise ValueError(f"{name} must be between 0 and 1, got {score}")
    return True


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to maximum length
    
    Args:
        text: Input text
        max_length: Maximum length
        
    Returns:
        str: Truncated text with "..." if truncated
    """
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def format_days(days: float) -> str:
    """
    Format days as human-readable string
    
    Args:
        days: Number of days
        
    Returns:
        str: Formatted string like "2.5 days" or "1 day"
    """
    if days == 1:
        return "1 day"
    elif days < 1:
        hours = days * 24
        return f"{hours:.1f} hours"
    else:
        return f"{days:.1f} days"
