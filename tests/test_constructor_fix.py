#!/usr/bin/env python3
"""
Simple test to verify QBSplitsType2 constructor works without errors.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.models.qb_models import QBSplitsType2
from datetime import datetime

def test_qbsplits_type2_constructor():
    """Test that QBSplitsType2 can be instantiated with the correct field names"""
    print("=== Testing QBSplitsType2 Constructor ===")
    
    try:
        # Test instantiation with all required fields
        qb_splits = QBSplitsType2(
            pfr_id="test123",
            player_name="Test Player",
            season=2024,
            split="Down",
            value="1st",
            cmp=150,
            att=250,
            inc=100,
            cmp_pct=60.0,
            yds=1800,
            td=12,
            first_downs=80,
            int=5,
            rate=92.0,
            sk=15,
            sk_yds=100,
            y_a=7.2,
            ay_a=7.8,
            rush_att=25,
            rush_yds=100,
            rush_y_a=4.0,
            rush_td=1,
            rush_first_downs=8,
            scraped_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        print("✅ QBSplitsType2 instantiation successful!")
        print(f"   Rush Att: {qb_splits.rush_att}")
        print(f"   Rush Yds: {qb_splits.rush_yds}")
        print(f"   Rush Y/A: {qb_splits.rush_y_a}")
        print(f"   Rush TD: {qb_splits.rush_td}")
        print(f"   Rush First Downs: {qb_splits.rush_first_downs}")
        
        return True
        
    except Exception as e:
        print(f"❌ QBSplitsType2 instantiation failed: {e}")
        return False

def test_old_field_names_fail():
    """Test that old field names are no longer accepted"""
    print("\n=== Testing Old Field Names Rejection ===")
    
    # Test that old field names are not accepted
    old_field_names = ['att_rush', 'yds_rush', 'y_a_rush', 'td_rush', 'one_d_rush']
    
    for field_name in old_field_names:
        try:
            # Try to create with old field name
            kwargs = {
                'pfr_id': "test123",
                'player_name': "Test Player", 
                'season': 2024,
                field_name: 100  # This should fail
            }
            qb_splits = QBSplitsType2(**kwargs)
            print(f"❌ Unexpected success with old field name: {field_name}")
            return False
        except TypeError as e:
            if "unexpected keyword argument" in str(e):
                print(f"✅ Correctly rejected old field name: {field_name}")
            else:
                print(f"❌ Unexpected error with {field_name}: {e}")
                return False
        except Exception as e:
            print(f"❌ Unexpected error with {field_name}: {e}")
            return False
    
    return True

if __name__ == "__main__":
    print("🧪 Testing QBSplitsType2 Constructor Fixes")
    
    success = True
    
    # Test that new field names work
    if not test_qbsplits_type2_constructor():
        success = False
    
    # Test that old field names are rejected
    if not test_old_field_names_fail():
        success = False
    
    if success:
        print("\n🎉 All constructor tests passed! Field mapping fixes are working.")
    else:
        print("\n❌ Some constructor tests failed.")
    
    print("\n=== Constructor Test Complete ===") 