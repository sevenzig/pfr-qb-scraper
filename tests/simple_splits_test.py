#!/usr/bin/env python3
"""
Simple test to check what fields are actually in the qb_splits_advanced table
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_splits_advanced_fields():
    """Check what fields are present in qb_splits_advanced table"""
    
    # Get database connection
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("DATABASE_URL not found in environment")
        return
    
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        # Check table structure
        print("=== Checking qb_splits_advanced table structure ===")
        cur.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'qb_splits_advanced'
            ORDER BY ordinal_position
        """)
        
        columns = cur.fetchall()
        print(f"Found {len(columns)} columns in qb_splits_advanced:")
        for col in columns:
            print(f"  {col[0]} ({col[1]}, nullable: {col[2]})")
        
        # Check if specific fields exist
        column_names = [col[0] for col in columns]
        print(f"\n=== Field Check ===")
        print(f"cmp_pct in columns: {'cmp_pct' in column_names}")
        print(f"first_downs in columns: {'first_downs' in column_names}")
        print(f"inc in columns: {'inc' in column_names}")
        
        # Check sample data
        print(f"\n=== Sample Data Check ===")
        cur.execute("""
            SELECT pfr_id, player_name, season, split, value, 
                   cmp_pct, first_downs, inc, cmp, att
            FROM qb_splits_advanced 
            LIMIT 5
        """)
        
        rows = cur.fetchall()
        print(f"Found {len(rows)} sample rows:")
        for row in rows:
            print(f"  {row[0]} ({row[1]}) - {row[2]} - {row[3]}={row[4]}")
            print(f"    cmp_pct: {row[5]}, first_downs: {row[6]}, inc: {row[7]}")
            print(f"    cmp: {row[8]}, att: {row[9]}")
        
        # Count null values
        print(f"\n=== Null Value Analysis ===")
        cur.execute("""
            SELECT 
                COUNT(*) as total_rows,
                COUNT(cmp_pct) as cmp_pct_not_null,
                COUNT(first_downs) as first_downs_not_null,
                COUNT(inc) as inc_not_null
            FROM qb_splits_advanced
        """)
        
        stats = cur.fetchone()
        print(f"Total rows: {stats[0]}")
        print(f"Rows with cmp_pct: {stats[1]} ({stats[1]/stats[0]*100:.1f}%)")
        print(f"Rows with first_downs: {stats[2]} ({stats[2]/stats[0]*100:.1f}%)")
        print(f"Rows with inc: {stats[3]} ({stats[3]/stats[0]*100:.1f}%)")
        
        # Check for any non-null values
        cur.execute("""
            SELECT COUNT(*) 
            FROM qb_splits_advanced 
            WHERE cmp_pct IS NOT NULL OR first_downs IS NOT NULL
        """)
        
        any_data = cur.fetchone()[0]
        print(f"\nRows with ANY of cmp_pct or first_downs: {any_data}")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_splits_advanced_fields() 