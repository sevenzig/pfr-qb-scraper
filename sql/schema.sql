-- NFL QB Data Database Schema for Supabase
-- Raw Data Tables matching Pro Football Reference CSV exports exactly
-- NO CALCULATIONS - Raw data only

-- Enable Row Level Security (RLS) for Supabase
ALTER DEFAULT PRIVILEGES REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC;

-- Player Master Table (for normalization and player info)
-- Uses PFR unique ID as primary key (e.g., 'burrjo01' for Joe Burrow)
CREATE TABLE IF NOT EXISTS players (
    pfr_id VARCHAR(20) PRIMARY KEY,  -- PFR unique ID (e.g., 'burrjo01')
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

-- Team Master Table
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

-- QB Passing Statistics Table (matches 2024_passing.csv exactly)
-- Raw data from main passing stats table with ALL columns
CREATE TABLE IF NOT EXISTS qb_passing_stats (
    pfr_id VARCHAR(20) NOT NULL,
    player_name VARCHAR(100) NOT NULL,
    player_url VARCHAR(255) NOT NULL,
    season INTEGER NOT NULL CHECK (season >= 1920 AND season <= 2030),
    
    -- Raw CSV columns (matching 2024_passing.csv exactly)
    rk INTEGER,  -- Rank
    age INTEGER,  -- Age
    team VARCHAR(10),  -- Team (allows multi-team players like "nyj,gb")
    pos VARCHAR(5),  -- Position
    g INTEGER,  -- Games
    gs INTEGER,  -- Games Started
    qb_rec VARCHAR(20),  -- QB Record (W-L-T format)
    cmp INTEGER,  -- Completions
    att INTEGER,  -- Attempts
    cmp_pct DECIMAL(5,2),  -- Completion %
    yds INTEGER,  -- Yards
    td INTEGER,  -- Touchdowns
    td_pct DECIMAL(5,2),  -- TD %
    int INTEGER,  -- Interceptions
    int_pct DECIMAL(5,2),  -- Int %
    first_downs INTEGER,  -- 1D (First Downs)
    succ_pct DECIMAL(5,2),  -- Success %
    lng INTEGER,  -- Longest pass
    y_a DECIMAL(5,2),  -- Y/A (Yards per Attempt)
    ay_a DECIMAL(5,2),  -- AY/A (Adjusted Yards per Attempt)
    y_c DECIMAL(5,2),  -- Y/C (Yards per Completion)
    y_g DECIMAL(6,2),  -- Y/G (Yards per Game)
    rate DECIMAL(5,2),  -- Passer Rating
    qbr DECIMAL(5,2),  -- QBR
    sk INTEGER,  -- Sacks
    sk_yds INTEGER,  -- Sack Yards
    sk_pct DECIMAL(5,2),  -- Sack %
    ny_a DECIMAL(5,2),  -- NY/A (Net Yards per Attempt)
    any_a DECIMAL(5,2),  -- ANY/A (Adjusted Net Yards per Attempt)
    four_qc INTEGER,  -- 4QC (4th Quarter Comebacks)
    gwd INTEGER,  -- GWD (Game Winning Drives)
    awards TEXT,  -- Awards
    player_additional VARCHAR(20),  -- Player-additional
    
    -- Metadata
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Primary key and constraints
    PRIMARY KEY (pfr_id, season),
    CONSTRAINT fk_qb_passing_stats_player FOREIGN KEY (pfr_id) REFERENCES players(pfr_id) ON DELETE CASCADE,
    CONSTRAINT fk_qb_passing_stats_team FOREIGN KEY (team) REFERENCES teams(team_code) ON DELETE RESTRICT
);

-- QB Splits Table (matches advanced_stats_1.csv exactly)
-- Raw data from splits page with ALL columns
CREATE TABLE IF NOT EXISTS qb_splits (
    id BIGSERIAL PRIMARY KEY,
    pfr_id VARCHAR(20) NOT NULL,
    player_name VARCHAR(100) NOT NULL,
    season INTEGER NOT NULL CHECK (season >= 1920 AND season <= 2030),
    
    -- Split identifiers
    split VARCHAR(50),  -- Split type (e.g., "League", "Place", "Result")
    value VARCHAR(100),  -- Split value (e.g., "NFL", "Home", "Win")
    
    -- Raw CSV columns (matching advanced_stats_1.csv exactly)
    g INTEGER,  -- Games
    w INTEGER,  -- Wins
    l INTEGER,  -- Losses
    t INTEGER,  -- Ties
    cmp INTEGER,  -- Completions
    att INTEGER,  -- Attempts
    inc INTEGER,  -- Incompletions
    cmp_pct DECIMAL(5,2),  -- Completion %
    yds INTEGER,  -- Passing Yards
    td INTEGER,  -- Passing TDs
    int INTEGER,  -- Interceptions
    rate DECIMAL(5,2),  -- Passer Rating
    sk INTEGER,  -- Sacks
    sk_yds INTEGER,  -- Sack Yards
    y_a DECIMAL(5,2),  -- Y/A (Yards per Attempt)
    ay_a DECIMAL(5,2),  -- AY/A (Adjusted Yards per Attempt)
    a_g DECIMAL(5,2),  -- A/G (Attempts per Game)
    y_g DECIMAL(6,2),  -- Y/G (Yards per Game)
    rush_att INTEGER,  -- Rush Attempts
    rush_yds INTEGER,  -- Rush Yards
    rush_y_a DECIMAL(5,2),  -- Rush Y/A
    rush_td INTEGER,  -- Rush TDs
    rush_a_g DECIMAL(5,2),  -- Rush A/G (Rush Attempts per Game)
    rush_y_g DECIMAL(6,2),  -- Rush Y/G (Rush Yards per Game)
    total_td INTEGER,  -- Total TDs
    pts INTEGER,  -- Points
    fmb INTEGER,  -- Fumbles
    fl INTEGER,  -- Fumbles Lost
    ff INTEGER,  -- Fumbles Forced
    fr INTEGER,  -- Fumbles Recovered
    fr_yds INTEGER,  -- Fumble Recovery Yards
    fr_td INTEGER,  -- Fumble Recovery TDs
    
    -- Metadata
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT fk_qb_splits_player FOREIGN KEY (pfr_id) REFERENCES players(pfr_id) ON DELETE CASCADE,
    CONSTRAINT unique_player_season_split UNIQUE(pfr_id, season, split, value)
);

-- QB Splits Advanced Table (matches advanced_stats.2.csv exactly)
-- Raw data from advanced splits page with ALL columns
CREATE TABLE IF NOT EXISTS qb_splits_advanced (
    id BIGSERIAL PRIMARY KEY,
    pfr_id VARCHAR(20) NOT NULL,
    player_name VARCHAR(100) NOT NULL,
    season INTEGER NOT NULL CHECK (season >= 1920 AND season <= 2030),
    
    -- Split identifiers
    split VARCHAR(50),  -- Split type (e.g., "Down", "Yards To Go")
    value VARCHAR(100),  -- Split value (e.g., "1st", "1-3")
    
    -- Raw CSV columns (matching advanced_stats.2.csv exactly)
    cmp INTEGER,  -- Completions
    att INTEGER,  -- Attempts
    inc INTEGER,  -- Incompletions
    cmp_pct DECIMAL(5,2),  -- Completion %
    yds INTEGER,  -- Passing Yards
    td INTEGER,  -- Passing TDs
    first_downs INTEGER,  -- 1D (First Downs)
    int INTEGER,  -- Interceptions
    rate DECIMAL(5,2),  -- Passer Rating
    sk INTEGER,  -- Sacks
    sk_yds INTEGER,  -- Sack Yards
    y_a DECIMAL(5,2),  -- Y/A (Yards per Attempt)
    ay_a DECIMAL(5,2),  -- AY/A (Adjusted Yards per Attempt)
    rush_att INTEGER,  -- Rush Attempts
    rush_yds INTEGER,  -- Rush Yards
    rush_y_a DECIMAL(5,2),  -- Rush Y/A
    rush_td INTEGER,  -- Rush TDs
    rush_first_downs INTEGER,  -- Rush First Downs
    
    -- Metadata
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT fk_qb_splits_advanced_player FOREIGN KEY (pfr_id) REFERENCES players(pfr_id) ON DELETE CASCADE,
    CONSTRAINT unique_player_season_split_advanced UNIQUE(pfr_id, season, split, value)
);

-- Scraping Log Table (for monitoring and audit trail)
CREATE TABLE IF NOT EXISTS scraping_logs (
    id BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(50) NOT NULL,
    season INTEGER NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE,
    total_requests INTEGER DEFAULT 0,
    successful_requests INTEGER DEFAULT 0,
    failed_requests INTEGER DEFAULT 0,
    total_players INTEGER DEFAULT 0,
    total_passing_stats INTEGER DEFAULT 0,
    total_splits INTEGER DEFAULT 0,
    total_splits_advanced INTEGER DEFAULT 0,
    errors TEXT[],
    warnings TEXT[],
    rate_limit_violations INTEGER DEFAULT 0,
    processing_time_seconds DECIMAL(10,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance optimization

-- Player table indexes
CREATE INDEX IF NOT EXISTS idx_players_name ON players(player_name);
CREATE INDEX IF NOT EXISTS idx_players_position ON players(position);
CREATE INDEX IF NOT EXISTS idx_players_college ON players(college);
CREATE INDEX IF NOT EXISTS idx_players_draft_year ON players(draft_year);

-- Team table indexes
CREATE INDEX IF NOT EXISTS idx_teams_conference ON teams(conference);
CREATE INDEX IF NOT EXISTS idx_teams_division ON teams(division);

-- QB Passing Stats table indexes
CREATE INDEX IF NOT EXISTS idx_qb_passing_stats_season ON qb_passing_stats(season);
CREATE INDEX IF NOT EXISTS idx_qb_passing_stats_team ON qb_passing_stats(team);
CREATE INDEX IF NOT EXISTS idx_qb_passing_stats_player_name ON qb_passing_stats(player_name);
CREATE INDEX IF NOT EXISTS idx_qb_passing_stats_rate ON qb_passing_stats(rate DESC);
CREATE INDEX IF NOT EXISTS idx_qb_passing_stats_yds ON qb_passing_stats(yds DESC);
CREATE INDEX IF NOT EXISTS idx_qb_passing_stats_td ON qb_passing_stats(td DESC);
CREATE INDEX IF NOT EXISTS idx_qb_passing_stats_cmp_pct ON qb_passing_stats(cmp_pct DESC);
CREATE INDEX IF NOT EXISTS idx_qb_passing_stats_qbr ON qb_passing_stats(qbr DESC);

-- QB Splits table indexes
CREATE INDEX IF NOT EXISTS idx_qb_splits_pfr_id ON qb_splits(pfr_id);
CREATE INDEX IF NOT EXISTS idx_qb_splits_season ON qb_splits(season);
CREATE INDEX IF NOT EXISTS idx_qb_splits_split ON qb_splits(split);
CREATE INDEX IF NOT EXISTS idx_qb_splits_value ON qb_splits(value);
CREATE INDEX IF NOT EXISTS idx_qb_splits_player_season ON qb_splits(pfr_id, season);
CREATE INDEX IF NOT EXISTS idx_qb_splits_split_value ON qb_splits(split, value);

-- QB Splits Advanced table indexes
CREATE INDEX IF NOT EXISTS idx_qb_splits_advanced_pfr_id ON qb_splits_advanced(pfr_id);
CREATE INDEX IF NOT EXISTS idx_qb_splits_advanced_season ON qb_splits_advanced(season);
CREATE INDEX IF NOT EXISTS idx_qb_splits_advanced_split ON qb_splits_advanced(split);
CREATE INDEX IF NOT EXISTS idx_qb_splits_advanced_value ON qb_splits_advanced(value);
CREATE INDEX IF NOT EXISTS idx_qb_splits_advanced_player_season ON qb_splits_advanced(pfr_id, season);
CREATE INDEX IF NOT EXISTS idx_qb_splits_advanced_split_value ON qb_splits_advanced(split, value);

-- Scraping log table indexes
CREATE INDEX IF NOT EXISTS idx_scraping_logs_session_id ON scraping_logs(session_id);
CREATE INDEX IF NOT EXISTS idx_scraping_logs_season ON scraping_logs(season);
CREATE INDEX IF NOT EXISTS idx_scraping_logs_start_time ON scraping_logs(start_time);

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_qb_passing_stats_season_rate ON qb_passing_stats(season, rate DESC);
CREATE INDEX IF NOT EXISTS idx_qb_passing_stats_team_season ON qb_passing_stats(team, season);
CREATE INDEX IF NOT EXISTS idx_qb_splits_season_split ON qb_splits(season, split);
CREATE INDEX IF NOT EXISTS idx_qb_splits_advanced_season_split ON qb_splits_advanced(season, split);

-- Trigger function for updating updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for auto-updating updated_at columns
CREATE TRIGGER update_players_updated_at 
    BEFORE UPDATE ON players 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_qb_passing_stats_updated_at 
    BEFORE UPDATE ON qb_passing_stats 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_qb_splits_updated_at 
    BEFORE UPDATE ON qb_splits 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_qb_splits_advanced_updated_at 
    BEFORE UPDATE ON qb_splits_advanced 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Helpful views for data analysis

-- Season summary view (combines all data types)
CREATE OR REPLACE VIEW qb_season_summary AS
SELECT 
    p.pfr_id,
    p.player_name,
    ps.season,
    ps.team,
    ps.age,
    ps.g as games,
    ps.gs as games_started,
    ps.cmp as completions,
    ps.att as attempts,
    ps.cmp_pct as completion_pct,
    ps.yds as pass_yards,
    ps.td as pass_tds,
    ps.int as interceptions,
    ps.rate as passer_rating,
    ps.qbr,
    ps.sk as sacks,
    ps.sk_yds as sack_yards,
    ps.four_qc as fourth_quarter_comebacks,
    ps.gwd as game_winning_drives,
    ps.awards
FROM players p
JOIN qb_passing_stats ps ON p.pfr_id = ps.pfr_id
ORDER BY ps.season DESC, ps.rate DESC NULLS LAST;

-- Function to get all data for a specific player and season
CREATE OR REPLACE FUNCTION get_player_season_data(target_pfr_id VARCHAR(20), target_season INTEGER)
RETURNS TABLE(
    data_type VARCHAR(20),
    json_data JSONB
) AS $$
BEGIN
    -- Return passing stats
    RETURN QUERY
    SELECT 
        'passing_stats'::VARCHAR(20) as data_type,
        row_to_json(ps)::JSONB as json_data
    FROM qb_passing_stats ps
    WHERE ps.pfr_id = target_pfr_id AND ps.season = target_season;
    
    -- Return splits
    RETURN QUERY
    SELECT 
        'splits'::VARCHAR(20) as data_type,
        row_to_json(s)::JSONB as json_data
    FROM qb_splits s
    WHERE s.pfr_id = target_pfr_id AND s.season = target_season;
    
    -- Return splits advanced
    RETURN QUERY
    SELECT 
        'splits_advanced'::VARCHAR(20) as data_type,
        row_to_json(sa)::JSONB as json_data
    FROM qb_splits_advanced sa
    WHERE sa.pfr_id = target_pfr_id AND sa.season = target_season;
    
    RETURN;
END;
$$ LANGUAGE plpgsql;

-- Function to get splits data by type
CREATE OR REPLACE FUNCTION get_splits_by_type(
    target_pfr_id VARCHAR(20), 
    target_season INTEGER, 
    split_type VARCHAR(50)
)
RETURNS TABLE(
    table_name VARCHAR(20),
    split VARCHAR(50),
    value VARCHAR(100),
    json_data JSONB
) AS $$
BEGIN
    -- Return from splits
    RETURN QUERY
    SELECT 
        'qb_splits'::VARCHAR(20) as table_name,
        s.split,
        s.value,
        row_to_json(s)::JSONB as json_data
    FROM qb_splits s
    WHERE s.pfr_id = target_pfr_id 
      AND s.season = target_season 
      AND s.split = split_type;
    
    -- Return from splits advanced
    RETURN QUERY
    SELECT 
        'qb_splits_advanced'::VARCHAR(20) as table_name,
        sa.split,
        sa.value,
        row_to_json(sa)::JSONB as json_data
    FROM qb_splits_advanced sa
    WHERE sa.pfr_id = target_pfr_id 
      AND sa.season = target_season 
      AND sa.split = split_type;
    
    RETURN;
END;
$$ LANGUAGE plpgsql;

-- Database statistics view
CREATE OR REPLACE VIEW database_stats AS
SELECT 
    'players' as table_name,
    COUNT(*) as record_count,
    MIN(created_at) as earliest_record,
    MAX(created_at) as latest_record
FROM players
UNION ALL
SELECT 
    'qb_passing_stats' as table_name,
    COUNT(*) as record_count,
    MIN(scraped_at) as earliest_record,
    MAX(scraped_at) as latest_record
FROM qb_passing_stats
UNION ALL
SELECT 
    'qb_splits' as table_name,
    COUNT(*) as record_count,
    MIN(scraped_at) as earliest_record,
    MAX(scraped_at) as latest_record
FROM qb_splits
UNION ALL
SELECT 
    'qb_splits_advanced' as table_name,
    COUNT(*) as record_count,
    MIN(scraped_at) as earliest_record,
    MAX(scraped_at) as latest_record
FROM qb_splits_advanced
UNION ALL
SELECT 
    'scraping_logs' as table_name,
    COUNT(*) as record_count,
    MIN(created_at) as earliest_record,
    MAX(created_at) as latest_record
FROM scraping_logs
ORDER BY table_name;

-- Grant permissions for Supabase
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO anon, authenticated;
GRANT INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO authenticated; 