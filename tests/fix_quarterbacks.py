#!/usr/bin/env python3
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

try:
    # Check quarterbacks table structure
    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'quarterbacks' ORDER BY ordinal_position")
    columns = cur.fetchall()
    print("quarterbacks table columns:")
    for col in columns:
        print(f"  {col[0]}")
    
    # Populate quarterbacks table with correct column names
    populate_qb_sql = """
    INSERT INTO quarterbacks (name, team, year, games_started, wins, losses, passing_yards, passing_tds, interceptions, sacks, rushing_yards, rushing_tds, passer_rating, any_per_attempt, completion_percentage, sack_percentage, game_winning_drives)
    SELECT DISTINCT 
        player_name as name,
        team,
        season as year,
        gs as games_started,
        CASE 
            WHEN qb_rec LIKE '%-%' THEN CAST(SPLIT_PART(qb_rec, '-', 1) AS INTEGER)
            ELSE 0
        END as wins,
        CASE 
            WHEN qb_rec LIKE '%-%-%' THEN CAST(SPLIT_PART(qb_rec, '-', 2) AS INTEGER)
            ELSE 0
        END as losses,
        yds as passing_yards,
        td as passing_tds,
        int as interceptions,
        sk as sacks,
        0 as rushing_yards,  -- Not available in passing stats
        0 as rushing_tds,    -- Not available in passing stats
        CAST(rate AS DECIMAL(5,2)) as passer_rating,
        CAST(ay_a AS DECIMAL(5,2)) as any_per_attempt,
        CAST(cmp_pct AS DECIMAL(5,2)) as completion_percentage,
        CAST(sk_pct AS DECIMAL(5,2)) as sack_percentage,
        gwd as game_winning_drives
    FROM qb_passing_stats
    WHERE pos = 'QB'
    ON CONFLICT DO NOTHING
    """
    
    cur.execute(populate_qb_sql)
    print("✅ Populated quarterbacks table")
    
    # Commit changes
    conn.commit()
    print("✅ All changes committed successfully")
    
except Exception as e:
    print(f"❌ Error: {e}")
    conn.rollback()

conn.close() 