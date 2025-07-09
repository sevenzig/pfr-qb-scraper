#!/usr/bin/env python3
"""
Update QB stats tables to use new PFR team codes

This script updates any QB stats records that reference the old team codes
to use the new PFR-compatible team codes.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from database.db_manager import DatabaseManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Update QB stats tables with new team codes"""
    db = DatabaseManager()
    
    try:
        logger.info("Updating QB stats tables to use new PFR team codes...")
        
        # Team code mappings (old -> new)
        team_updates = [
            ('SF', 'SFO'),
            ('GB', 'GNB'), 
            ('KC', 'KAN'),
            ('LV', 'LVR'),
            ('NE', 'NWE'),
            ('NO', 'NOR'),
            ('TAM', 'TB')  # PFR might use TAM but our DB has TB
        ]
        
        # Update qb_passing_stats (only table with team column)
        logger.info("Updating qb_passing_stats...")
        total_updated = 0
        
        for old_code, new_code in team_updates:
            rows_affected = db.execute(
                "UPDATE qb_passing_stats SET team = %s WHERE team = %s",
                (new_code, old_code)
            )
            if rows_affected > 0:
                logger.info(f"  Updated {rows_affected} records: {old_code} -> {new_code}")
                total_updated += rows_affected
        
        logger.info(f"Total qb_passing_stats updated: {total_updated}")
        
        # Note: QB splits tables don't have team columns - they're linked via pfr_id
        logger.info("QB splits tables don't have team columns - no updates needed")
        
        # Check for any remaining foreign key issues
        logger.info("Checking for remaining foreign key issues...")
        
        orphaned_qb_stats = db.query("""
            SELECT DISTINCT p.team, COUNT(*) as count
            FROM qb_passing_stats p
            LEFT JOIN teams t ON p.team = t.team_code
            WHERE t.team_code IS NULL
            GROUP BY p.team
            ORDER BY p.team
        """)
        
        if orphaned_qb_stats:
            logger.warning("Found QB stats with invalid team codes:")
            for record in orphaned_qb_stats:
                logger.warning(f"  Team code '{record['team']}': {record['count']} records")
        else:
            logger.info("✅ No foreign key constraint issues found in qb_passing_stats")
        
        logger.info("QB stats team code update completed!")
        
    except Exception as e:
        logger.error(f"Error updating QB stats: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main() 