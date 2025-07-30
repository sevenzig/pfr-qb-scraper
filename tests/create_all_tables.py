#!/usr/bin/env python3
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

try:
    # Create players table
    players_sql = """
    CREATE TABLE IF NOT EXISTS players (
        pfr_id VARCHAR(20) PRIMARY KEY,
        player_name VARCHAR(100) NOT NULL,
        first_name VARCHAR(50),
        last_name VARCHAR(50),
        position VARCHAR(5) DEFAULT 'QB',
        height_inches INTEGER,
        weight_lbs INTEGER,
        birth_date DATE,
        age INTEGER,
        college VARCHAR(100),
        draft_year INTEGER,
        draft_round INTEGER,
        draft_pick INTEGER,
        pfr_url VARCHAR(255) NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    cur.execute(players_sql)
    print("✅ Created players table")
    
    # Create teams table
    teams_sql = """
    CREATE TABLE IF NOT EXISTS teams (
        team_code VARCHAR(3) PRIMARY KEY,
        team_name VARCHAR(100) NOT NULL,
        city VARCHAR(50) NOT NULL,
        conference VARCHAR(3) CHECK (conference IN ('AFC', 'NFC')),
        division VARCHAR(10) CHECK (division IN ('North', 'South', 'East', 'West')),
        founded_year INTEGER,
        stadium_name VARCHAR(100),
        stadium_capacity INTEGER,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    cur.execute(teams_sql)
    print("✅ Created teams table")
    
    # Create qb_splits table
    qb_splits_sql = """
    CREATE TABLE IF NOT EXISTS qb_splits (
        id BIGSERIAL PRIMARY KEY,
        pfr_id VARCHAR(20) NOT NULL,
        player_name VARCHAR(100) NOT NULL,
        season INTEGER NOT NULL CHECK (season >= 1920 AND season <= 2030),
        split VARCHAR(50),
        value VARCHAR(100),
        g INTEGER,
        w INTEGER,
        l INTEGER,
        t INTEGER,
        cmp INTEGER,
        att INTEGER,
        inc INTEGER,
        cmp_pct DECIMAL(5,2),
        yds INTEGER,
        td INTEGER,
        int INTEGER,
        rate DECIMAL(5,2),
        sk INTEGER,
        sk_yds INTEGER,
        y_a DECIMAL(5,2),
        ay_a DECIMAL(5,2),
        a_g DECIMAL(5,2),
        y_g DECIMAL(6,2),
        rush_att INTEGER,
        rush_yds INTEGER,
        rush_y_a DECIMAL(5,2),
        rush_td INTEGER,
        rush_a_g DECIMAL(5,2),
        rush_y_g DECIMAL(6,2),
        total_td INTEGER,
        pts INTEGER,
        fmb INTEGER,
        fl INTEGER,
        ff INTEGER,
        fr INTEGER,
        fr_yds INTEGER,
        fr_td INTEGER,
        scraped_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT fk_qb_splits_player FOREIGN KEY (pfr_id) REFERENCES players(pfr_id) ON DELETE CASCADE,
        CONSTRAINT unique_player_season_split UNIQUE(pfr_id, season, split, value)
    );
    """
    
    cur.execute(qb_splits_sql)
    print("✅ Created qb_splits table")
    
    # Commit changes
    conn.commit()
    print("✅ All tables created successfully")
    
    # Check what tables exist now
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name")
    tables = cur.fetchall()
    print("\nExisting tables:")
    for table in tables:
        print(f"  {table[0]}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    conn.rollback()

conn.close() 