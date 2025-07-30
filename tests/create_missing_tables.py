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
        pfr_id VARCHAR(20) PRIMARY KEY,  -- PFR unique ID (e.g., 'burrjo01' for Joe Burrow)
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
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        
        CONSTRAINT valid_height CHECK (height_inches IS NULL OR (height_inches > 60 AND height_inches < 84)),
        CONSTRAINT valid_weight CHECK (weight_lbs IS NULL OR (weight_lbs > 150 AND weight_lbs < 350)),
        CONSTRAINT valid_age CHECK (age IS NULL OR (age > 15 AND age < 50)),
        CONSTRAINT valid_draft_year CHECK (draft_year IS NULL OR (draft_year >= 1936 AND draft_year <= 2030)),
        CONSTRAINT valid_draft_round CHECK (draft_round IS NULL OR (draft_round >= 1 AND draft_round <= 10)),
        CONSTRAINT valid_draft_pick CHECK (draft_pick IS NULL OR (draft_pick >= 1 AND draft_pick <= 300))
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
        
        -- Split identifiers
        split VARCHAR(50),  -- Split type (e.g., "League", "Place", "Result")
        value VARCHAR(100),  -- Split value (e.g., "NFL", "Home", "Win")
        
        -- Raw CSV columns (matching advanced_stats_1.csv exactly by position)
        -- Columns 3-6: Game Stats
        g INTEGER,           -- Games (Col 3)
        w INTEGER,           -- Wins (Col 4)
        l INTEGER,           -- Losses (Col 5)
        t INTEGER,           -- Ties (Col 6)
        
        -- Columns 7-20: Passing Stats
        cmp INTEGER,         -- Completions (Col 7)
        att INTEGER,         -- Passing Attempts (Col 8)
        inc INTEGER,         -- Incompletions (Col 9)
        cmp_pct DECIMAL(5,2), -- Completion % (Col 10)
        yds INTEGER,         -- Passing Yards (Col 11)
        td INTEGER,          -- Passing TDs (Col 12)
        int INTEGER,         -- Interceptions (Col 13)
        rate DECIMAL(5,2),   -- Passer Rating (Col 14)
        sk INTEGER,          -- Sacks (Col 15)
        sk_yds INTEGER,      -- Sack Yards (Col 16)
        y_a DECIMAL(5,2),    -- Passing Y/A (Col 17)
        ay_a DECIMAL(5,2),   -- AY/A (Col 18)
        a_g DECIMAL(5,2),    -- Passing A/G (Col 19)
        y_g DECIMAL(6,2),    -- Passing Y/G (Col 20)
        
        -- Columns 21-26: Rushing Stats
        rush_att INTEGER,    -- Rush Attempts (Col 21)
        rush_yds INTEGER,    -- Rush Yards (Col 22)
        rush_y_a DECIMAL(5,2), -- Rush Y/A (Col 23)
        rush_td INTEGER,     -- Rush TDs (Col 24)
        rush_a_g DECIMAL(5,2), -- Rush A/G (Col 25)
        rush_y_g DECIMAL(6,2), -- Rush Y/G (Col 26)
        
        -- Columns 27-28: Total Stats
        total_td INTEGER,    -- Total TDs (Col 27)
        pts INTEGER,         -- Points (Col 28)
        
        -- Columns 29-34: Fumble Stats
        fmb INTEGER,         -- Fumbles (Col 29)
        fl INTEGER,          -- Fumbles Lost (Col 30)
        ff INTEGER,          -- Fumbles Forced (Col 31)
        fr INTEGER,          -- Fumbles Recovered (Col 32)
        fr_yds INTEGER,      -- Fumble Recovery Yards (Col 33)
        fr_td INTEGER,       -- Fumble Recovery TDs (Col 34)
        
        -- Metadata
        scraped_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        
        -- Constraints
        CONSTRAINT fk_qb_splits_player FOREIGN KEY (pfr_id) REFERENCES players(pfr_id) ON DELETE CASCADE,
        CONSTRAINT unique_player_season_split UNIQUE(pfr_id, season, split, value)
    );
    """
    
    cur.execute(qb_splits_sql)
    print("✅ Created qb_splits table")
    
    # Populate quarterbacks table from qb_passing_stats
    populate_qb_sql = """
    INSERT INTO quarterbacks (pfr_id, player_name, team, season, position)
    SELECT DISTINCT pfr_id, player_name, team, season, pos
    FROM qb_passing_stats
    WHERE pos = 'QB'
    ON CONFLICT (pfr_id, season) DO NOTHING
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