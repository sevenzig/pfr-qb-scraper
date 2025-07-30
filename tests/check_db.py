#!/usr/bin/env python3
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

# Check what tables exist
cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
tables = cur.fetchall()
print("Existing tables:")
for table in tables:
    print(f"  {table[0]}")

# Check if qb_passing_stats exists and has the inc column
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'qb_passing_stats'")
columns = cur.fetchall()
print("\nqb_passing_stats columns:")
for col in columns:
    print(f"  {col[0]}")

conn.close() 