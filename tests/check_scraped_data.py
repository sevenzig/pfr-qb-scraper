#!/usr/bin/env python3
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

# Print all columns for Joe Burrow's 2024 passing stats
cur.execute("""
    SELECT *
    FROM qb_passing_stats 
    WHERE player_name LIKE '%Burrow%' AND season=2024
    LIMIT 1
""")
row = cur.fetchone()
if row:
    print("Joe Burrow 2024 passing stats (all columns):")
    for idx, col in enumerate(cur.description):
        print(f"  {col.name}: {row[idx]}")
else:
    print("No passing stats found for Joe Burrow 2024.")

# Print all columns for three rows from qb_splits
cur.execute("""
    SELECT *
    FROM qb_splits 
    WHERE player_name LIKE '%Burrow%' AND season=2024
    LIMIT 3
""")
rows = cur.fetchall()
print(f"\nJoe Burrow qb_splits (showing {len(rows)} records, all columns):")
if rows:
    for row in rows:
        for idx, col in enumerate(cur.description):
            print(f"  {col.name}: {row[idx]}")
        print("---")
else:
    print("No qb_splits found for Joe Burrow 2024.")

# Print all columns for three rows from qb_splits_advanced
cur.execute("""
    SELECT *
    FROM qb_splits_advanced 
    WHERE player_name LIKE '%Burrow%' AND season=2024
    LIMIT 3
""")
rows = cur.fetchall()
print(f"\nJoe Burrow qb_splits_advanced (showing {len(rows)} records, all columns):")
if rows:
    for row in rows:
        for idx, col in enumerate(cur.description):
            print(f"  {col.name}: {row[idx]}")
        print("---")
else:
    print("No qb_splits_advanced found for Joe Burrow 2024.")

conn.close() 