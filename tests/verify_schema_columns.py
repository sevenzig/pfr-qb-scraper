#!/usr/bin/env python3
"""
Verify that qb_splits_advanced table has exactly the expected columns
"""

import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def verify_schema_columns():
    """Verify qb_splits_advanced table columns match expected CSV structure"""
    
    # Expected columns based on user specification
    expected_columns = [
        # Split identifiers
        'split', 'value',
        # Passing stats
        'cmp', 'att', 'inc', 'cmp_pct', 'yds', 'td', 'first_downs', 'int', 'rate', 'sk', 'sk_yds', 'y_a', 'ay_a',
        # Rushing stats  
        'rush_att', 'rush_yds', 'rush_y_a', 'rush_td', 'rush_first_downs'
    ]
    
    # Get database connection
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("DATABASE_URL not found in environment")
        return
    
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        # Get actual columns from database
        cur.execute("""
            SELECT column_name
            FROM information_schema.columns 
            WHERE table_name = 'qb_splits_advanced'
            AND column_name NOT IN ('id', 'pfr_id', 'player_name', 'season', 'scraped_at', 'updated_at')
            ORDER BY ordinal_position
        """)
        
        actual_columns = [row[0] for row in cur.fetchall()]
        
        print("=== Schema Verification ===")
        print(f"Expected columns: {len(expected_columns)}")
        print(f"Actual columns: {len(actual_columns)}")
        
        print(f"\nExpected columns:")
        for col in expected_columns:
            print(f"  - {col}")
        
        print(f"\nActual columns:")
        for col in actual_columns:
            print(f"  - {col}")
        
        # Check for missing columns
        missing = set(expected_columns) - set(actual_columns)
        extra = set(actual_columns) - set(expected_columns)
        
        if missing:
            print(f"\n❌ Missing columns: {list(missing)}")
        else:
            print(f"\n✅ All expected columns present")
            
        if extra:
            print(f"\n⚠️  Extra columns: {list(extra)}")
        else:
            print(f"\n✅ No extra columns")
        
        # Check column order
        print(f"\n=== Column Order Check ===")
        for i, (expected, actual) in enumerate(zip(expected_columns, actual_columns)):
            if expected == actual:
                print(f"  {i+1:2d}. ✅ {expected}")
            else:
                print(f"  {i+1:2d}. ❌ Expected: {expected}, Got: {actual}")
        
        if len(expected_columns) != len(actual_columns):
            print(f"\n⚠️  Column count mismatch: Expected {len(expected_columns)}, Got {len(actual_columns)}")
        
        # Summary
        if not missing and not extra:
            print(f"\n🎉 Schema matches exactly!")
        else:
            print(f"\n⚠️  Schema needs adjustment")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_schema_columns() 