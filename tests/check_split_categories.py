#!/usr/bin/env python3
"""
Check split categories in the database
"""

import sys
import os
sys.path.insert(0, 'src')

from database.db_manager import DatabaseManager

def main():
    """Check split categories in the database"""
    print("Checking split categories in qb_splits table...")
    
    try:
        db_manager = DatabaseManager()
        
        # Check what split categories exist
        result = db_manager.query("SELECT split, COUNT(*) as count FROM qb_splits GROUP BY split ORDER BY count DESC")
        
        print("\nSplit categories found:")
        for row in result:
            print(f"  - {row['split']}: {row['count']} records")
        
        # Check some sample records with "other" split
        result = db_manager.query("SELECT split, value, player_name, season, rush_att, rush_yds, rush_td FROM qb_splits WHERE split = 'other' LIMIT 5")
        
        print(f"\nSample records with 'other' split:")
        for row in result:
            print(f"  - {row['player_name']} ({row['season']}): split='{row['split']}', value='{row['value']}', rush_att={row['rush_att']}, rush_yds={row['rush_yds']}, rush_td={row['rush_td']}")
        
        # Check if there are any non-"other" splits
        result = db_manager.query("SELECT split, COUNT(*) as count FROM qb_splits WHERE split != 'other' GROUP BY split")
        
        if result:
            print(f"\nNon-'other' split categories:")
            for row in result:
                print(f"  - {row['split']}: {row['count']} records")
        else:
            print(f"\nNo non-'other' split categories found")
        
        # Check what values are being used for "other" splits
        result = db_manager.query("SELECT value, COUNT(*) as count FROM qb_splits WHERE split = 'other' GROUP BY value ORDER BY count DESC LIMIT 10")
        
        print(f"\nTop 10 values for 'other' splits:")
        for row in result:
            print(f"  - '{row['value']}': {row['count']} records")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 