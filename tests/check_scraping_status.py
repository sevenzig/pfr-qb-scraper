#!/usr/bin/env python3
"""
Check scraping status and show current data
"""

import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from database.db_manager import DatabaseManager

def main():
    """Check scraping status"""
    try:
        db = DatabaseManager()
        
        # Get database stats
        stats = db.get_database_stats()
        
        print("=== DATABASE STATUS ===")
        print(f"Total Players: {stats.get('total_players', 0)}")
        print(f"Total QB Stats: {stats.get('total_qb_stats', 0)}")
        print(f"Total QB Splits: {stats.get('total_qb_splits', 0)}")
        print(f"Total Teams: {stats.get('total_teams', 0)}")
        
        # Get recent scraping logs
        logs = db.query("""
            SELECT session_id, season, start_time, end_time, 
                   total_players, total_passing_stats, total_splits,
                   processing_time_seconds, successful_requests, failed_requests
            FROM scraping_logs 
            ORDER BY start_time DESC 
            LIMIT 5
        """)
        
        if logs:
            print("\n=== RECENT SCRAPING SESSIONS ===")
            for log in logs:
                print(f"Session: {log['session_id']}")
                print(f"Season: {log['season']}")
                print(f"Started: {log['start_time']}")
                print(f"Players: {log['total_players']}")
                print(f"Stats: {log['total_passing_stats']}")
                print(f"Splits: {log['total_splits']}")
                print(f"Processing Time: {log['processing_time_seconds']:.2f}s")
                print(f"Requests: {log['successful_requests']} success, {log['failed_requests']} failed")
                print("---")
        
        # Get sample QB data
        qbs = db.query("""
            SELECT pfr_id, player_name, season, team, g, gs, cmp, att, yds, td, int, rate
            FROM qb_passing_stats 
            WHERE season = 2024 
            ORDER BY yds DESC 
            LIMIT 10
        """)
        
        if qbs:
            print("\n=== TOP 10 QBs BY YARDS (2024) ===")
            for qb in qbs:
                print(f"{qb['player_name']} ({qb['team']}): {qb['yds']} yards, {qb['td']} TDs, {qb['int']} INTs")
        
    except Exception as e:
        print(f"Error checking status: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 