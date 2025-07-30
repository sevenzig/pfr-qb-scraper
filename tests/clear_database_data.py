#!/usr/bin/env python3
"""
Clear all data from database tables while preserving table structure
"""

import sys
import os
import logging
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database.db_manager import DatabaseManager

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def clear_database_data(confirm: bool = False) -> bool:
    """
    Clear all data from database tables while preserving table structure
    
    Args:
        confirm: Whether to confirm the operation (safety check)
        
    Returns:
        True if successful, False otherwise
    """
    if not confirm:
        print("⚠️  WARNING: This will delete ALL data from the database!")
        print("Tables will be preserved, but all records will be removed.")
        print("This operation cannot be undone.")
        print()
        response = input("Type 'YES' to confirm: ")
        if response != 'YES':
            print("Operation cancelled.")
            return False
    
    try:
        logger.info("Connecting to database...")
        db_manager = DatabaseManager()
        
        # Test connection
        if not db_manager.test_connection():
            logger.error("Failed to connect to database")
            return False
        
        logger.info("✅ Database connection successful")
        
        # Tables to clear (in order to respect foreign key constraints)
        tables_to_clear = [
            'scraping_logs',
            'qb_splits_advanced', 
            'qb_splits',
            'qb_passing_stats',
            'players'
        ]
        
        total_deleted = 0
        
        for table in tables_to_clear:
            try:
                logger.info(f"Clearing table: {table}")
                
                # Get count before deletion
                count_result = db_manager.query(f"SELECT COUNT(*) as count FROM {table}")
                count_before = count_result[0]['count'] if count_result else 0
                
                # Delete all records
                deleted_count = db_manager.execute(f"DELETE FROM {table}")
                
                logger.info(f"✅ Deleted {deleted_count} records from {table} (was {count_before})")
                total_deleted += deleted_count
                
            except Exception as e:
                logger.error(f"❌ Error clearing table {table}: {e}")
                # Continue with other tables
                continue
        
        # Show final stats
        logger.info(f"✅ Database clearing completed!")
        logger.info(f"Total records deleted: {total_deleted}")
        
        # Show current table counts
        logger.info("Current table counts:")
        for table in tables_to_clear:
            try:
                count_result = db_manager.query(f"SELECT COUNT(*) as count FROM {table}")
                count = count_result[0]['count'] if count_result else 0
                logger.info(f"  {table}: {count} records")
            except Exception as e:
                logger.warning(f"  {table}: Error getting count - {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error clearing database: {e}")
        return False
    finally:
        if 'db_manager' in locals():
            db_manager.close()

def main():
    """Main function"""
    print("🗑️  Database Data Clearing Tool")
    print("=" * 40)
    
    # Check if --confirm flag is provided
    confirm = '--confirm' in sys.argv
    
    success = clear_database_data(confirm=confirm)
    
    if success:
        print("\n✅ Database cleared successfully!")
        print("You can now run fresh scraping operations.")
    else:
        print("\n❌ Database clearing failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 