#!/usr/bin/env python3
"""
Clear QB Data Script

This script clears existing QB data from the database so you can start fresh
with the fixed scraper that now extracts real data instead of zeros.

Usage:
    python scripts/clear_qb_data.py --confirm
"""

import argparse
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from database.db_manager import DatabaseManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clear_qb_data(confirm: bool = False):
    """Clear all QB-related data from the database"""
    
    if not confirm:
        print("❌ This will DELETE ALL existing QB data!")
        print("   Use --confirm flag if you're sure you want to proceed.")
        print("   Example: python scripts/clear_qb_data.py --confirm")
        return False
    
    print("🗑️  Clearing existing QB data from database...")
    
    try:
        db_manager = DatabaseManager()
        
        with db_manager.get_connection() as conn:
            with db_manager.get_cursor(conn) as cur:
                
                # Clear in order to respect foreign keys
                tables_to_clear = [
                    'qb_splits_type2',
                    'qb_splits_type1', 
                    'qb_passing_stats',
                    'players'
                ]
                
                for table in tables_to_clear:
                    cur.execute(f"DELETE FROM {table}")
                    affected = cur.rowcount
                    print(f"  ✅ Cleared {table}: {affected} records deleted")
                
                # Also clear scraping logs
                cur.execute("DELETE FROM scraping_log")
                affected = cur.rowcount
                print(f"  ✅ Cleared scraping_log: {affected} records deleted")
        
        print("🎉 Database cleared successfully!")
        print("   You can now run the scraper to get fresh data:")
        print("   python scripts/robust_qb_scraper.py --all")
        return True
        
    except Exception as e:
        logger.error(f"Error clearing database: {e}")
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Clear QB data from database')
    parser.add_argument('--confirm', action='store_true', 
                       help='Confirm that you want to delete all QB data')
    
    args = parser.parse_args()
    
    success = clear_qb_data(args.confirm)
    
    if success:
        print("\n🚀 Next steps:")
        print("1. Run: python scripts/robust_qb_scraper.py --all")
        print("2. Wait for scraping to complete (~15-30 minutes)")
        print("3. Enjoy your real QB data! 🏈")

if __name__ == "__main__":
    main() 