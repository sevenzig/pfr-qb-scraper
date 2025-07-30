#!/usr/bin/env python3
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

# Check quarterbacks table structure
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'quarterbacks' ORDER BY ordinal_position")
columns = cur.fetchall()
print("quarterbacks table columns:")
for col in columns:
    print(f"  {col[0]}")

# Check if there are any constraints
cur.execute("SELECT constraint_name, constraint_type FROM information_schema.table_constraints WHERE table_name = 'quarterbacks'")
constraints = cur.fetchall()
print("\nquarterbacks table constraints:")
for constraint in constraints:
    print(f"  {constraint[0]}: {constraint[1]}")

conn.close() 