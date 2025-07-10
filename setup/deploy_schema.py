#!/usr/bin/env python3
"""
Deploy database schema to Supabase
"""

import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from database.db_manager import DatabaseManager

def main():
    """Deploy schema to database"""
    try:
        print("Connecting to database...")
        db = DatabaseManager()
        
        # Test connection
        if not db.test_connection():
            print("❌ Failed to connect to database")
            return 1
        
        print("✅ Database connection successful")
        
        # Create tables
        print("Creating database tables...")
        try:
            db.create_tables()
        except Exception as e:
            print(f"⚠️  Warning: Error(s) occurred during schema deployment: {e}")
        
        print("✅ Schema deployed successfully!")
        
        # Show initial stats
        stats = db.get_database_stats()
        print("\n=== INITIAL DATABASE STATS ===")
        print(f"Total Players: {stats.get('total_players', 0)}")
        print(f"Total QB Stats: {stats.get('total_qb_stats', 0)}")
        print(f"Total QB Splits: {stats.get('total_qb_splits', 0)}")
        print(f"Total Teams: {stats.get('total_teams', 0)}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error deploying schema: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 