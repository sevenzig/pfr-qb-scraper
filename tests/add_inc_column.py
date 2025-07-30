#!/usr/bin/env python3
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

try:
    # Add the inc column
    cur.execute("ALTER TABLE qb_passing_stats ADD COLUMN inc INTEGER")
    print("✅ Added inc column to qb_passing_stats table")
    
    # Commit the change
    conn.commit()
    print("✅ Changes committed successfully")
    
except Exception as e:
    print(f"❌ Error: {e}")
    conn.rollback()

conn.close() 