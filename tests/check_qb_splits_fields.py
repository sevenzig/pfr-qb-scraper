#!/usr/bin/env python3
"""
Check the qb_splits table for missing fields, specifically the "other=1-4" split
"""

import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_qb_splits_fields():
    """Check qb_splits table for missing fields"""
    
    # Get database connection
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("DATABASE_URL not found in environment")
        return
    
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        # Check table structure
        print("=== Checking qb_splits table structure ===")
        cur.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'qb_splits'
            ORDER BY ordinal_position
        """)
        
        columns = cur.fetchall()
        print(f"Found {len(columns)} columns in qb_splits:")
        for col in columns:
            print(f"  {col[0]} ({col[1]}, nullable: {col[2]})")
        
        # Check if specific fields exist
        column_names = [col[0] for col in columns]
        print(f"\n=== Field Check ===")
        print(f"cmp_pct in columns: {'cmp_pct' in column_names}")
        print(f"first_downs in columns: {'first_downs' in column_names}")
        print(f"inc in columns: {'inc' in column_names}")
        
        # Check sample data for "other=1-4" split
        print(f"\n=== Sample Data for 'other=1-4' split ===")
        cur.execute("""
            SELECT pfr_id, player_name, season, split, value, 
                   cmp_pct, first_downs, inc, cmp, att
            FROM qb_splits 
            WHERE split = 'other' AND value = '1-4'
            ORDER BY player_name
            LIMIT 10
        """)
        
        rows = cur.fetchall()
        print(f"Found {len(rows)} 'other=1-4' rows (showing first 10):")
        for row in rows:
            print(f"  {row[0]} ({row[1]}) - {row[2]} - {row[3]}={row[4]}")
            print(f"    cmp_pct: {row[5]}, first_downs: {row[6]}, inc: {row[7]}")
            print(f"    cmp: {row[8]}, att: {row[9]}")
        
        # Count null values for "other=1-4" split
        print(f"\n=== Null Value Analysis for 'other=1-4' ===")
        cur.execute("""
            SELECT 
                COUNT(*) as total_rows,
                COUNT(cmp_pct) as cmp_pct_not_null,
                COUNT(first_downs) as first_downs_not_null,
                COUNT(inc) as inc_not_null
            FROM qb_splits
            WHERE split = 'other' AND value = '1-4'
        """)
        
        stats = cur.fetchone()
        print(f"Total 'other=1-4' rows: {stats[0]}")
        print(f"Rows with cmp_pct: {stats[1]} ({stats[1]/stats[0]*100:.1f}%)")
        print(f"Rows with first_downs: {stats[2]} ({stats[2]/stats[0]*100:.1f}%)")
        print(f"Rows with inc: {stats[3]} ({stats[3]/stats[0]*100:.1f}%)")
        
        # Compare with other splits
        print(f"\n=== Comparison with other split values ===")
        cur.execute("""
            SELECT 
                split,
                value,
                COUNT(*) as total_rows,
                COUNT(cmp_pct) as cmp_pct_count,
                COUNT(first_downs) as first_downs_count,
                COUNT(inc) as inc_count
            FROM qb_splits 
            WHERE split = 'other'
            GROUP BY split, value
            ORDER BY value
        """)
        
        split_stats = cur.fetchall()
        for row in split_stats:
            split, value, total, cmp_pct, first_downs, inc = row
            print(f"  {split}={value}: {total} rows")
            print(f"    cmp_pct: {cmp_pct}/{total} ({cmp_pct/total*100:.1f}%)")
            print(f"    first_downs: {first_downs}/{total} ({first_downs/total*100:.1f}%)")
            print(f"    inc: {inc}/{total} ({inc/total*100:.1f}%)")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_qb_splits_fields() 