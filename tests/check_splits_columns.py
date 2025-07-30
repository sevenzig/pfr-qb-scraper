#!/usr/bin/env python3
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

# Check qb_splits_advanced columns
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'qb_splits_advanced' ORDER BY ordinal_position")
columns = cur.fetchall()
print("qb_splits_advanced columns:")
for col in columns:
    print(f"  {col[0]}")

# Check quarterbacks table
cur.execute("SELECT COUNT(*) FROM quarterbacks")
count = cur.fetchone()[0]
print(f"\nquarterbacks table: {count} records")

# Check if qb_splits table exists
cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'qb_splits'")
tables = cur.fetchall()
if tables:
    print("qb_splits table: EXISTS")
    cur.execute("SELECT COUNT(*) FROM qb_splits")
    count = cur.fetchone()[0]
    print(f"qb_splits records: {count}")
else:
    print("qb_splits table: MISSING")

conn.close() 