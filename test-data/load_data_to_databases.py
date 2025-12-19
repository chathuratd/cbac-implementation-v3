"""
Script to load prompts and behaviors from JSON files into databases
- Prompts are saved to MongoDB
- Behaviors are vectorized and saved to Qdrant
"""
import json
import logging
import sys
import os
from pathlib import Path
from typing import List, Dict

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Change working directory to parent to find .env file
os.chdir(parent_dir)

from src.database.mongodb_service import MongoDBService
from src.database.qdrant_service import QdrantService
from src.services.embedding_service import EmbeddingService
from src.models.schemas import BehaviorObservation, PromptModel

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_json_file(filepath: str) -> List[Dict]:
    """Load data from JSON file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"Loaded {len(data)} records from {filepath}")
        return data
    except Exception as e:
        logger.error(f"Error loading {filepath}: {e}")
        return []


def save_prompts_to_mongodb(prompts_data: List[Dict], mongo_service: MongoDBService) -> bool:
    """Save prompts to MongoDB"""
    try:
        # Convert to PromptModel objects
        prompts = [PromptModel(**prompt_data) for prompt_data in prompts_data]
        
        # Bulk insert
        success = mongo_service.insert_prompts_bulk(prompts)
        
        if success:
            logger.info(f"Successfully saved {len(prompts)} prompts to MongoDB")
        else:
            logger.error("Failed to save prompts to MongoDB")
        
        return success
    except Exception as e:
        logger.error(f"Error saving prompts: {e}")
        return False


def save_behaviors_to_qdrant(
    behaviors_data: List[Dict], 
    qdrant_service: QdrantService, 
    embedding_service: EmbeddingService
) -> bool:
    """Vectorize behaviors and save complete data to Qdrant"""
    try:
        # Extract behavior texts for vectorization
        behavior_texts = [b['behavior_text'] for b in behaviors_data]
        
        logger.info(f"Generating embeddings for {len(behavior_texts)} behaviors...")
        
        # Generate embeddings
        embeddings = embedding_service.generate_embeddings_batch(behavior_texts)
        
        if not embeddings:
            logger.error("Failed to generate embeddings")
            return False
        
        logger.info(f"Generated {len(embeddings)} embeddings")
        
        # Save complete behavior data with embeddings to Qdrant
        success = qdrant_service.insert_behaviors_with_embeddings(
            embeddings=embeddings,
            behaviors=behaviors_data
        )
        
        if success:
            logger.info(f"Successfully saved {len(embeddings)} complete behaviors to Qdrant")
        else:
            logger.error("Failed to save behaviors to Qdrant")
        
        return success
    except Exception as e:
        logger.error(f"Error saving behaviors: {e}")
        return False


def main():
    """Main execution function"""
    # Define directory path
    base_dir = Path(__file__).parent / "behavior_dataset"
    
    # Check if directory exists
    if not base_dir.exists():
        logger.error(f"Directory not found: {base_dir}")
        return False
    
    # Find all prompts and behaviors files
    prompts_files = sorted(base_dir.glob("prompts_user_*.json"))
    behaviors_files = sorted(base_dir.glob("behaviors_user_*.json"))
    
    if not prompts_files:
        logger.error(f"No prompts_user_*.json files found in {base_dir}")
        return False
    
    if not behaviors_files:
        logger.error(f"No behaviors_user_*.json files found in {base_dir}")
        return False
    
    logger.info(f"Found {len(prompts_files)} prompt files and {len(behaviors_files)} behavior files")
    
    # Load data from all JSON files
    logger.info("\nLoading data from JSON files...")
    all_prompts_data = []
    all_behaviors_data = []
    
    for prompts_file in prompts_files:
        logger.info(f"Loading {prompts_file.name}...")
        prompts_data = load_json_file(str(prompts_file))
        if prompts_data:
            all_prompts_data.extend(prompts_data)
    
    for behaviors_file in behaviors_files:
        logger.info(f"Loading {behaviors_file.name}...")
        behaviors_data = load_json_file(str(behaviors_file))
        if behaviors_data:
            all_behaviors_data.extend(behaviors_data)
    
    if not all_prompts_data or not all_behaviors_data:
        logger.error("Failed to load data from files")
        return False
    
    logger.info(f"\nTotal loaded: {len(all_prompts_data)} prompts, {len(all_behaviors_data)} behaviors")
    
    # Initialize services
    logger.info("Initializing database services...")
    mongo_service = MongoDBService()
    qdrant_service = QdrantService()
    embedding_service = EmbeddingService()
    
    try:
        # Connect to services
        logger.info("Connecting to databases...")
        mongo_service.connect()
        qdrant_service.connect()
        embedding_service.connect()
        
        # Save prompts to MongoDB
        logger.info("\n" + "="*50)
        logger.info("Saving prompts to MongoDB...")
        logger.info("="*50)
        prompts_success = save_prompts_to_mongodb(all_prompts_data, mongo_service)
        
        # Save behaviors to Qdrant (with vectorization)
        logger.info("\n" + "="*50)
        logger.info("Vectorizing and saving behaviors to Qdrant...")
        logger.info("="*50)
        behaviors_success = save_behaviors_to_qdrant(
            all_behaviors_data, 
            qdrant_service, 
            embedding_service
        )
        
        # Save behaviors to MongoDB (for complete metadata access)
        logger.info("\n" + "="*50)
        logger.info("Saving behaviors to MongoDB...")
        logger.info("="*50)
        try:
            # Convert old format to new BehaviorObservation format
            behavior_observations = []
            for b in all_behaviors_data:
                # Map old fields to new fields
                obs = BehaviorObservation(
                    observation_id=b.get('behavior_id'),  # Use behavior_id as observation_id
                    user_id=b.get('user_id'),
                    behavior_text=b.get('behavior_text'),
                    timestamp=b.get('created_at'),  # Use created_at as timestamp
                    prompt_id=b.get('prompt_history_ids', [None])[0] if b.get('prompt_history_ids') else None,  # Use first prompt
                    session_id=b.get('session_id'),
                    credibility=b.get('credibility'),
                    clarity_score=b.get('clarity_score', 0.75),  # Default value for old data
                    extraction_confidence=b.get('extraction_confidence', 0.80),  # Default value for old data
                    decay_rate=b.get('decay_rate')
                )
                behavior_observations.append(obs)
            
            mongo_service.insert_behaviors_bulk(behavior_observations)
            behaviors_mongo_success = True
            logger.info(f"✓ Successfully saved {len(behavior_observations)} behaviors to MongoDB")
        except Exception as e:
            logger.error(f"Failed to save behaviors to MongoDB: {e}")
            behaviors_mongo_success = False
        
        # Summary
        logger.info("\n" + "="*50)
        logger.info("SUMMARY")
        logger.info("="*50)
        logger.info(f"Prompts saved to MongoDB: {'✓' if prompts_success else '✗'} ({len(all_prompts_data)} records)")
        logger.info(f"Behaviors saved to Qdrant: {'✓' if behaviors_success else '✗'} ({len(all_behaviors_data)} records)")
        logger.info(f"Behaviors saved to MongoDB: {'✓' if behaviors_mongo_success else '✗'} ({len(all_behaviors_data)} records)")
        
        if prompts_success and behaviors_success and behaviors_mongo_success:
            logger.info("\n✓ All data loaded successfully!")
            return True
        else:
            logger.warning("\n⚠ Some operations failed. Check logs above.")
            return False
        
    except Exception as e:
        logger.error(f"Error during execution: {e}")
        return False
    
    finally:
        # Disconnect services
        logger.info("\nDisconnecting from databases...")
        mongo_service.disconnect()
        qdrant_service.disconnect()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
