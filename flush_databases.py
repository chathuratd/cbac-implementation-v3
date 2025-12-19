"""
Flush MongoDB and Qdrant databases
Clears all data for a fresh start
"""
import sys
sys.path.append('.')

from src.database.mongodb_service import mongodb_service
from src.database.qdrant_service import qdrant_service


def flush_databases():
    """Clear all data from MongoDB and Qdrant"""
    
    print("="*70)
    print("  FLUSHING DATABASES")
    print("="*70)
    
    # Connect to databases
    print("\n1. Connecting to databases...")
    mongodb_service.connect()
    qdrant_service.connect()
    print("   Connected ✓")
    
    # Flush MongoDB
    print("\n2. Flushing MongoDB...")
    try:
        db = mongodb_service.db
        
        # Get all collections
        collections = db.list_collection_names()
        print(f"   Found {len(collections)} collections")
        
        # Drop each collection
        for collection_name in collections:
            count = db[collection_name].count_documents({})
            db[collection_name].delete_many({})
            print(f"   Deleted {count} documents from '{collection_name}'")
        
        print("   MongoDB flushed ✓")
    except Exception as e:
        print(f"   Error flushing MongoDB: {e}")
    
    # Flush Qdrant
    print("\n3. Flushing Qdrant...")
    try:
        collection_name = qdrant_service.collection_name
        
        # Get collection info
        collection_info = qdrant_service.client.get_collection(collection_name)
        point_count = collection_info.points_count
        
        print(f"   Found {point_count} points in collection '{collection_name}'")
        
        # Delete the collection and recreate it
        qdrant_service.client.delete_collection(collection_name)
        print(f"   Deleted collection '{collection_name}'")
        
        # Recreate collection
        qdrant_service._ensure_collection()
        print(f"   Recreated collection '{collection_name}'")
        
        print("   Qdrant flushed ✓")
    except Exception as e:
        print(f"   Error flushing Qdrant: {e}")
    
    # Disconnect
    print("\n4. Disconnecting...")
    mongodb_service.disconnect()
    qdrant_service.disconnect()
    print("   Disconnected ✓")
    
    print("\n" + "="*70)
    print("  DATABASES FLUSHED SUCCESSFULLY")
    print("="*70)


if __name__ == "__main__":
    response = input("\n⚠️  This will DELETE ALL DATA from MongoDB and Qdrant.\nAre you sure? (yes/no): ")
    
    if response.lower() == 'yes':
        flush_databases()
    else:
        print("\n❌ Operation cancelled")
