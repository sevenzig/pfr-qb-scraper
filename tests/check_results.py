#!/usr/bin/env python3
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

# Check what tables exist
cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name LIKE '%split%'")
tables = cur.fetchall()
print("Splits tables:")
for table in tables:
    print(f"  {table[0]}")

# Check Joe Burrow passing stats
cur.execute("SELECT COUNT(*) FROM qb_passing_stats WHERE player_name LIKE '%Burrow%'")
count = cur.fetchone()[0]
print(f"\nJoe Burrow passing stats: {count} records")

if count > 0:
    # Show the data
    cur.execute("SELECT player_name, season, team, cmp, att, inc, yds, td FROM qb_passing_stats WHERE player_name LIKE '%Burrow%'")
    rows = cur.fetchall()
    for row in rows:
        print(f"  {row[0]} ({row[1]}): {row[2]} - {row[3]}/{row[4]} for {row[6]} yards, {row[7]} TDs (inc: {row[5]})")
        
        # Calculate inc if it's None
        if row[5] is None and row[3] is not None and row[4] is not None:
            inc = row[4] - row[3]  # att - cmp
            print(f"    Calculated inc: {inc}")

# Check Joe Burrow splits in the correct table
if tables:
    splits_table = tables[0][0]  # Use the first splits table
    cur.execute(f"SELECT COUNT(*) FROM {splits_table} WHERE player_name LIKE '%Burrow%'")
    count = cur.fetchone()[0]
    print(f"\nJoe Burrow splits ({splits_table}): {count} records")

conn.close() 