"""
Archetype Service for CBIE System
Generates behavioral archetype labels using Azure OpenAI LLM
"""
from typing import List, Optional
import logging
from openai import AzureOpenAI

from src.config import settings

logger = logging.getLogger(__name__)


class ArchetypeService:
    """Service for generating behavioral archetypes using LLM"""
    
    def __init__(self):
        self.client: Optional[AzureOpenAI] = None
        # Using a GPT model for completion - adjust deployment name as needed
        self.model = "gpt-4"  # Or your Azure deployment name
        
    def connect(self):
        """Initialize Azure OpenAI client"""
        try:
            self.client = AzureOpenAI(
                api_key=settings.openai_api_key,
                api_version=settings.openai_api_version,
                azure_endpoint=settings.openai_api_base
            )
            logger.info(f"Connected to Azure OpenAI for archetype generation")
        except Exception as e:
            logger.error(f"Failed to connect to Azure OpenAI: {e}")
            raise
    
    def generate_archetype(
        self,
        canonical_behaviors: List[str],
        user_id: Optional[str] = None
    ) -> str:
        """
        Generate behavioral archetype label from canonical behaviors
        
        Args:
            canonical_behaviors: List of behavior text strings
            user_id: Optional user ID for logging
            
        Returns:
            str: Archetype label (e.g., "Visual Learner")
        """
        try:
            if not canonical_behaviors:
                logger.warning("No behaviors provided for archetype generation")
                return "Unknown"
            
            # Create prompt
            prompt = self._create_archetype_prompt(canonical_behaviors)
            
            # Call Azure OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert in behavioral psychology and user profiling. "
                                   "Your task is to analyze user behaviors and assign a concise, "
                                   "descriptive archetype label."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=50
            )
            
            archetype = response.choices[0].message.content.strip()
            
            # Clean up the response (remove quotes, extra punctuation)
            archetype = archetype.strip('"\'.,')
            
            logger.info(
                f"Generated archetype for user {user_id}: '{archetype}' "
                f"from {len(canonical_behaviors)} behaviors"
            )
            
            return archetype
            
        except Exception as e:
            logger.error(f"Error generating archetype: {e}")
            return "Unknown"
    
    def _create_archetype_prompt(self, behaviors: List[str]) -> str:
        """
        Create prompt for LLM archetype generation
        
        Args:
            behaviors: List of behavior text strings
            
        Returns:
            str: Formatted prompt
        """
        behaviors_text = "\n".join([f"- {behavior}" for behavior in behaviors])
        
        prompt = f"""Given the following user behaviors:

{behaviors_text}

Classify the user into a single, concise behavioral archetype. 
The archetype should be a descriptive label (2-4 words) that captures the essence of these behaviors.

Examples of good archetypes: "Visual Learner", "Detail-Oriented Analyst", "Quick Reference Seeker", "Hands-On Experimenter"

Return ONLY the archetype label, nothing else."""
        
        return prompt
    
    def generate_archetype_with_context(
        self,
        canonical_behaviors: List[str],
        user_statistics: dict,
        user_id: Optional[str] = None
    ) -> str:
        """
        Generate archetype with additional context about user statistics
        
        Args:
            canonical_behaviors: List of behavior text strings
            user_statistics: Dict with statistics (total_behaviors, days_active, etc.)
            user_id: Optional user ID for logging
            
        Returns:
            str: Archetype label
        """
        try:
            if not canonical_behaviors:
                return "Unknown"
            
            # Enhanced prompt with statistics
            behaviors_text = "\n".join([f"- {behavior}" for behavior in canonical_behaviors])
            
            stats_text = ""
            if user_statistics:
                stats_text = f"\n\nUser activity context:\n"
                if "total_behaviors_analyzed" in user_statistics:
                    stats_text += f"- Total behaviors: {user_statistics['total_behaviors_analyzed']}\n"
                if "analysis_time_span_days" in user_statistics:
                    stats_text += f"- Active for: {user_statistics['analysis_time_span_days']:.0f} days\n"
                if "total_prompts_analyzed" in user_statistics:
                    stats_text += f"- Total interactions: {user_statistics['total_prompts_analyzed']}\n"
            
            prompt = f"""Given the following user behaviors:

{behaviors_text}
{stats_text}

Classify the user into a single, concise behavioral archetype that captures their learning or interaction style.

Return ONLY the archetype label (2-4 words), nothing else."""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert in behavioral psychology and user profiling."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=50
            )
            
            archetype = response.choices[0].message.content.strip().strip('"\'.,')
            
            logger.info(f"Generated contextual archetype for user {user_id}: '{archetype}'")
            
            return archetype
            
        except Exception as e:
            logger.error(f"Error generating contextual archetype: {e}")
            return "Unknown"


# Global archetype service instance
archetype_service = ArchetypeService()
