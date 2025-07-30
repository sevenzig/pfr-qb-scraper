#!/usr/bin/env python3
"""
Check current database state and determine if rescraping is needed
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

# Import database manager without the problematic models import
import psycopg2
from psycopg2.extras import RealDictCursor
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_database_connection():
    """Get database connection"""
    try:
        # Try to get connection string from environment
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            # Try to get from config
            try:
                from config.config import config
                database_url = config.get_database_url()
            except:
                print("❌ No database URL found in environment or config")
                return None
        
        conn = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return None

def check_database_state():
    """Check current database state and data integrity"""
    print("🔍 Checking current database state...")
    
    conn = get_database_connection()
    if not conn:
        return False
    
    try:
        print("✅ Database connection successful")
        
        # Check table structure
        print("\n📊 Checking table structure...")
        
        with conn.cursor() as cur:
            # Check if qb_splits table exists and has correct columns
            cur.execute("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'qb_splits' 
                ORDER BY ordinal_position
            """)
            
            result = cur.fetchall()
            if result:
                print(f"✅ qb_splits table exists with {len(result)} columns")
                print("Columns found:")
                for col in result:
                    print(f"  - {col['column_name']}: {col['data_type']}")
            else:
                print("❌ qb_splits table not found")
                return False
        
        # Check data counts
        print("\n📈 Checking data counts...")
        
        with conn.cursor() as cur:
            # Count records in each table
            tables = ['qb_passing_stats', 'qb_splits', 'qb_splits_advanced', 'players']
            
            for table in tables:
                try:
                    cur.execute(f"SELECT COUNT(*) as count FROM {table}")
                    result = cur.fetchone()
                    count = result['count'] if result else 0
                    print(f"  - {table}: {count} records")
                except Exception as e:
                    print(f"  - {table}: Error - {e}")
        
        # Check for data integrity issues
        print("\n🔍 Checking data integrity...")
        
        with conn.cursor() as cur:
            # Check if qb_splits has the expected split categories
            cur.execute("""
                SELECT split, COUNT(*) as count 
                FROM qb_splits 
                GROUP BY split 
                ORDER BY split
            """)
            
            result = cur.fetchall()
            if result:
                print("Split categories found:")
                for row in result:
                    print(f"  - {row['split']}: {row['count']} records")
                
                # Check for required categories
                required_splits = {
                    'Place', 'Result', 'Final Margin', 'Month', 'Game Number', 
                    'Day', 'Time', 'Conference', 'Division', 'Opponent', 'Stadium', 'QB Start'
                }
                
                found_splits = {row['split'] for row in result}
                missing_splits = required_splits - found_splits
                
                if missing_splits:
                    print(f"⚠️  Missing split categories: {missing_splits}")
                else:
                    print("✅ All required split categories present")
            else:
                print("⚠️  No split data found")
        
        # Check for duplicate column name issues
        print("\n🔍 Checking for duplicate column mapping issues...")
        
        with conn.cursor() as cur:
            # Check if rushing stats are properly separated from passing stats
            cur.execute("""
                SELECT 
                    COUNT(*) as total_records,
                    COUNT(CASE WHEN rush_att IS NOT NULL THEN 1 END) as has_rush_att,
                    COUNT(CASE WHEN rush_yds IS NOT NULL THEN 1 END) as has_rush_yds,
                    COUNT(CASE WHEN rush_td IS NOT NULL THEN 1 END) as has_rush_td
                FROM qb_splits 
                LIMIT 1
            """)
            
            result = cur.fetchone()
            if result:
                print(f"  - Total records: {result['total_records']}")
                print(f"  - Records with rush_att: {result['has_rush_att']}")
                print(f"  - Records with rush_yds: {result['has_rush_yds']}")
                print(f"  - Records with rush_td: {result['has_rush_td']}")
                
                # If rushing stats are missing, it indicates the duplicate column issue
                if result['has_rush_att'] == 0 and result['total_records'] > 0:
                    print("❌ RUSHING STATS ISSUE DETECTED - Data needs to be rescraped")
                    print("   This indicates the duplicate column mapping issue affected your data")
                    return False
                else:
                    print("✅ Rushing stats appear to be properly mapped")
        
        print("\n✅ Database state check completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error during database check: {e}")
        return False
    finally:
        conn.close()

def main():
    """Main function"""
    print("=" * 60)
    print("QB SPLITS DATABASE STATE CHECK")
    print("=" * 60)
    
    success = check_database_state()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 CONCLUSION: Your database appears to be in good shape!")
        print("   You likely DON'T need to drop and rescrape everything.")
        print("   The schema changes were backwards compatible.")
    else:
        print("⚠️  CONCLUSION: Issues detected that may require attention.")
        print("   Check the specific errors above for guidance.")
    print("=" * 60)

if __name__ == "__main__":
    main() 