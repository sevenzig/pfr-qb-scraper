#!/usr/bin/env python3
"""Check the teams table schema"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from database.db_manager import DatabaseManager

def main():
    db = DatabaseManager()
    
    try:
        print("=== Teams Table Schema ===")
        result = db.query("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'teams' 
            ORDER BY ordinal_position
        """)
        
        if result:
            for col in result:
                nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                print(f"  {col['column_name']} - {col['data_type']} ({nullable})")
        else:
            print("No columns found or table doesn't exist")
        
        print("\n=== Current Teams Data ===")
        teams = db.query("SELECT * FROM teams LIMIT 3")
        if teams:
            print("Sample data:")
            for team in teams:
                print(f"  {team}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main() 