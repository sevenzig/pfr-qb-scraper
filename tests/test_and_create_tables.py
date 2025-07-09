#!/usr/bin/env python3
"""
Test database connection and create tables if needed
"""

import sys
sys.path.append('src')

from config.config import config
from database.db_manager import DatabaseManager

def main():
    """Test database connection and create tables"""
    print("Testing database connection...")
    
    # Initialize database manager
    db_manager = DatabaseManager(config.get_database_url())
    
    # Test connection
    if db_manager.test_connection():
        print("✅ Database connection successful!")
    else:
        print("❌ Database connection failed!")
        return
    
    # Create tables
    print("Creating database tables...")
    try:
        db_manager.create_tables()
        print("✅ Database tables created successfully!")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return
    
    # Test a simple query
    print("Testing database query...")
    try:
        with db_manager.get_connection() as conn:
            with db_manager.get_cursor(conn) as cur:
                cur.execute("SELECT COUNT(*) FROM qb_stats")
                result = cur.fetchone()
                print(f"✅ Query successful! QB stats count: {result[0] if result else 0}")
    except Exception as e:
        print(f"❌ Query failed: {e}")

if __name__ == "__main__":
    main() 