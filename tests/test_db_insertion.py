#!/usr/bin/env python3
"""Test database insertion with minimal test case"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from datetime import datetime
from models.qb_models import QBSplitStats, QBSplitsType1
from database.db_manager import DatabaseManager

def test_splits_insertion():
    """Test QB splits insertion with minimal data"""
    
    # Create a minimal QBSplitStats object
    test_split = QBSplitStats(
        pfr_id="test01",
        player_name="Test Player",
        season=2024,
        split="League",
        value="NFL",
        g=17,
        w=10,
        l=7,
        t=0,
        cmp=300,
        att=500,
        inc=200,
        cmp_pct=60.0,
        yds=3500,
        td=25,
        int=10,
        rate=95.0,
        sk=30,
        sk_yds=200,
        y_a=7.0,
        ay_a=7.5,
        a_g=29.4,
        y_g=205.9,
        rush_att=50,
        rush_yds=200,
        rush_y_a=4.0,
        rush_td=2,
        rush_a_g=2.9,
        rush_y_g=11.8,
        total_td=27,
        pts=162,
        fmb=5,
        fl=2,
        ff=0,
        fr=1,
        fr_yds=0,
        fr_td=0,
        scraped_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    print("Created test QBSplitStats object:")
    print(f"  pfr_id: {test_split.pfr_id}")
    print(f"  player_name: {test_split.player_name}")
    print(f"  season: {test_split.season}")
    print(f"  split: {test_split.split}")
    print(f"  value: {test_split.value}")
    print(f"  rush_att: {test_split.rush_att}")
    print(f"  rush_yds: {test_split.rush_yds}")
    print(f"  rush_td: {test_split.rush_td}")
    
    # Test database insertion
    try:
        db = DatabaseManager()
        print("\nTesting database insertion...")
        
        # Test connection
        if db.test_connection():
            print("✓ Database connection successful")
        else:
            print("✗ Database connection failed")
            return
        
        # Test insertion
        result = db.insert_qb_splits([test_split])
        print(f"✓ Inserted {result} QB splits records")
        
        # Clean up test data
        db.execute("DELETE FROM qb_splits_type1 WHERE pfr_id = %s", ("test01",))
        print("✓ Cleaned up test data")
        
    except Exception as e:
        print(f"✗ Error during database test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    test_splits_insertion() 