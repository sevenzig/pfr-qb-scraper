-- NFL QB Data Database Schema for Supabase
-- Optimized for analytics and fast queries with PFR unique IDs as primary keys

-- Enable Row Level Security (RLS) for Supabase
ALTER DEFAULT PRIVILEGES REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC;

-- Create custom types for better data integrity
CREATE TYPE game_result AS ENUM ('win', 'loss', 'tie');
CREATE TYPE weather_condition AS ENUM ('clear', 'rain', 'snow', 'wind', 'dome');
CREATE TYPE field_surface AS ENUM ('grass', 'turf', 'artificial');

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
    age INTEGER,  -- Calculated age
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

-- Basic QB Statistics Table (season totals)
-- Uses composite primary key: (pfr_id, season)
CREATE TABLE IF NOT EXISTS qb_basic_stats (
    pfr_id VARCHAR(20) NOT NULL,
    season INTEGER NOT NULL CHECK (season >= 1920 AND season <= 2030),
    team VARCHAR(3) NOT NULL,
    games_played INTEGER DEFAULT 0 CHECK (games_played >= 0),
    games_started INTEGER DEFAULT 0 CHECK (games_started >= 0),
    completions INTEGER DEFAULT 0 CHECK (completions >= 0),
    attempts INTEGER DEFAULT 0 CHECK (attempts >= 0),
    completion_pct DECIMAL(5,2) CHECK (completion_pct >= 0 AND completion_pct <= 100),
    pass_yards INTEGER DEFAULT 0,
    pass_tds INTEGER DEFAULT 0 CHECK (pass_tds >= 0),
    interceptions INTEGER DEFAULT 0 CHECK (interceptions >= 0),
    longest_pass INTEGER DEFAULT 0 CHECK (longest_pass >= 0),
    rating DECIMAL(5,2) CHECK (rating >= 0 AND rating <= 158.3),
    sacks INTEGER DEFAULT 0 CHECK (sacks >= 0),
    sack_yards INTEGER DEFAULT 0,
    net_yards_per_attempt DECIMAL(4,2),
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Primary key and constraints
    PRIMARY KEY (pfr_id, season),
    CONSTRAINT fk_qb_basic_stats_player FOREIGN KEY (pfr_id) REFERENCES players(pfr_id) ON DELETE CASCADE,
    CONSTRAINT fk_qb_basic_stats_team FOREIGN KEY (team) REFERENCES teams(team_code) ON DELETE RESTRICT,
    CONSTRAINT valid_completion_ratio CHECK (attempts = 0 OR (completions <= attempts)),
    CONSTRAINT valid_games_started CHECK (games_started <= games_played)
);

-- Advanced QB Statistics Table (advanced metrics)
-- Uses composite primary key: (pfr_id, season)
CREATE TABLE IF NOT EXISTS qb_advanced_stats (
    pfr_id VARCHAR(20) NOT NULL,
    season INTEGER NOT NULL CHECK (season >= 1920 AND season <= 2030),
    qbr DECIMAL(5,2) CHECK (qbr >= 0 AND qbr <= 100),
    adjusted_net_yards_per_attempt DECIMAL(4,2),
    fourth_quarter_comebacks INTEGER DEFAULT 0 CHECK (fourth_quarter_comebacks >= 0),
    game_winning_drives INTEGER DEFAULT 0 CHECK (game_winning_drives >= 0),
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Primary key and constraints
    PRIMARY KEY (pfr_id, season),
    CONSTRAINT fk_qb_advanced_stats_player FOREIGN KEY (pfr_id) REFERENCES players(pfr_id) ON DELETE CASCADE
);

-- QB Splits Statistics Table (situational splits)
-- Uses auto-incrementing ID for splits records
CREATE TABLE IF NOT EXISTS qb_splits (
    id BIGSERIAL PRIMARY KEY,
    pfr_id VARCHAR(20) NOT NULL,
    season INTEGER NOT NULL CHECK (season >= 1920 AND season <= 2030),
    split_type VARCHAR(50) NOT NULL,
    split_category VARCHAR(100) NOT NULL,
    games INTEGER DEFAULT 0 CHECK (games >= 0),
    completions INTEGER DEFAULT 0 CHECK (completions >= 0),
    attempts INTEGER DEFAULT 0 CHECK (attempts >= 0),
    completion_pct DECIMAL(5,2) CHECK (completion_pct >= 0 AND completion_pct <= 100),
    pass_yards INTEGER DEFAULT 0,
    pass_tds INTEGER DEFAULT 0 CHECK (pass_tds >= 0),
    interceptions INTEGER DEFAULT 0 CHECK (interceptions >= 0),
    rating DECIMAL(5,2) CHECK (rating >= 0 AND rating <= 158.3),
    sacks INTEGER DEFAULT 0 CHECK (sacks >= 0),
    sack_yards INTEGER DEFAULT 0,
    net_yards_per_attempt DECIMAL(4,2),
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Additional fields for comprehensive QB splits data
    rush_attempts INTEGER DEFAULT 0 CHECK (rush_attempts >= 0),
    rush_yards INTEGER DEFAULT 0,
    rush_tds INTEGER DEFAULT 0 CHECK (rush_tds >= 0),
    fumbles INTEGER DEFAULT 0 CHECK (fumbles >= 0),
    fumbles_lost INTEGER DEFAULT 0 CHECK (fumbles_lost >= 0),
    fumbles_forced INTEGER DEFAULT 0 CHECK (fumbles_forced >= 0),
    fumbles_recovered INTEGER DEFAULT 0 CHECK (fumbles_recovered >= 0),
    fumble_recovery_yards INTEGER DEFAULT 0,
    fumble_recovery_tds INTEGER DEFAULT 0 CHECK (fumble_recovery_tds >= 0),
    incompletions INTEGER DEFAULT 0 CHECK (incompletions >= 0),
    wins INTEGER DEFAULT 0 CHECK (wins >= 0),
    losses INTEGER DEFAULT 0 CHECK (losses >= 0),
    ties INTEGER DEFAULT 0 CHECK (ties >= 0),
    attempts_per_game DECIMAL(4,2),
    yards_per_game DECIMAL(6,2),
    rush_attempts_per_game DECIMAL(4,2),
    rush_yards_per_game DECIMAL(6,2),
    total_tds INTEGER DEFAULT 0 CHECK (total_tds >= 0),
    points INTEGER DEFAULT 0,
    
    -- Constraints
    CONSTRAINT fk_qb_splits_player FOREIGN KEY (pfr_id) REFERENCES players(pfr_id) ON DELETE CASCADE,
    CONSTRAINT unique_player_season_split UNIQUE(pfr_id, season, split_type, split_category),
    CONSTRAINT valid_split_completion_ratio CHECK (attempts = 0 OR (completions <= attempts)),
    CONSTRAINT valid_fumbles_lost CHECK (fumbles_lost <= fumbles),
    CONSTRAINT valid_fumbles_recovered CHECK (fumbles_recovered <= fumbles),
    CONSTRAINT valid_total_tds CHECK (total_tds >= (pass_tds + rush_tds + fumble_recovery_tds))
);

-- Game Log Table (for individual game performance)
CREATE TABLE IF NOT EXISTS qb_game_log (
    id BIGSERIAL PRIMARY KEY,
    pfr_id VARCHAR(20) NOT NULL,
    season INTEGER NOT NULL,
    week INTEGER NOT NULL CHECK (week >= 1 AND week <= 22),
    game_date DATE NOT NULL,
    opponent VARCHAR(3) NOT NULL,
    home_away VARCHAR(4) CHECK (home_away IN ('Home', 'Away')),
    result game_result,
    completions INTEGER DEFAULT 0 CHECK (completions >= 0),
    attempts INTEGER DEFAULT 0 CHECK (attempts >= 0),
    completion_pct DECIMAL(5,2),
    pass_yards INTEGER DEFAULT 0,
    pass_tds INTEGER DEFAULT 0 CHECK (pass_tds >= 0),
    interceptions INTEGER DEFAULT 0 CHECK (interceptions >= 0),
    rating DECIMAL(5,2) CHECK (rating >= 0 AND rating <= 158.3),
    sacks INTEGER DEFAULT 0 CHECK (sacks >= 0),
    sack_yards INTEGER DEFAULT 0,
    rush_attempts INTEGER DEFAULT 0 CHECK (rush_attempts >= 0),
    rush_yards INTEGER DEFAULT 0,
    rush_tds INTEGER DEFAULT 0 CHECK (rush_tds >= 0),
    fumbles INTEGER DEFAULT 0 CHECK (fumbles >= 0),
    fumbles_lost INTEGER DEFAULT 0 CHECK (fumbles_lost >= 0),
    game_winning_drive BOOLEAN DEFAULT FALSE,
    fourth_quarter_comeback BOOLEAN DEFAULT FALSE,
    weather weather_condition,
    temperature INTEGER,
    wind_speed INTEGER,
    field_surface field_surface,
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT fk_qb_game_log_player FOREIGN KEY (pfr_id) REFERENCES players(pfr_id) ON DELETE CASCADE,
    CONSTRAINT fk_qb_game_log_opponent FOREIGN KEY (opponent) REFERENCES teams(team_code) ON DELETE RESTRICT,
    CONSTRAINT unique_player_game UNIQUE(pfr_id, season, week, game_date),
    CONSTRAINT valid_game_completion_ratio CHECK (attempts = 0 OR (completions <= attempts)),
    CONSTRAINT valid_fumbles_lost CHECK (fumbles_lost <= fumbles)
);

-- Scraping Log Table (for monitoring and audit trail)
CREATE TABLE IF NOT EXISTS scraping_log (
    id BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(36) NOT NULL,
    season INTEGER NOT NULL CHECK (season >= 1920 AND season <= 2030),
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE,
    total_requests INTEGER DEFAULT 0 CHECK (total_requests >= 0),
    successful_requests INTEGER DEFAULT 0 CHECK (successful_requests >= 0),
    failed_requests INTEGER DEFAULT 0 CHECK (failed_requests >= 0),
    total_players INTEGER DEFAULT 0 CHECK (total_players >= 0),
    total_basic_stats INTEGER DEFAULT 0 CHECK (total_basic_stats >= 0),
    total_advanced_stats INTEGER DEFAULT 0 CHECK (total_advanced_stats >= 0),
    total_qb_splits INTEGER DEFAULT 0 CHECK (total_qb_splits >= 0),
    errors TEXT[],
    warnings TEXT[],
    rate_limit_violations INTEGER DEFAULT 0 CHECK (rate_limit_violations >= 0),
    processing_time_seconds DECIMAL(10,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_request_counts CHECK (successful_requests + failed_requests = total_requests)
);

-- Indexes for Performance Optimization
-- Player Indexes
CREATE INDEX IF NOT EXISTS idx_players_name ON players(player_name);
CREATE INDEX IF NOT EXISTS idx_players_position ON players(position);
CREATE INDEX IF NOT EXISTS idx_players_college ON players(college);
CREATE INDEX IF NOT EXISTS idx_players_draft_year ON players(draft_year);

-- Team Indexes
CREATE INDEX IF NOT EXISTS idx_teams_conference ON teams(conference);
CREATE INDEX IF NOT EXISTS idx_teams_division ON teams(division);

-- Basic Stats Indexes
CREATE INDEX IF NOT EXISTS idx_qb_basic_stats_season ON qb_basic_stats(season);
CREATE INDEX IF NOT EXISTS idx_qb_basic_stats_team ON qb_basic_stats(team);
CREATE INDEX IF NOT EXISTS idx_qb_basic_stats_rating ON qb_basic_stats(rating DESC);
CREATE INDEX IF NOT EXISTS idx_qb_basic_stats_pass_yards ON qb_basic_stats(pass_yards DESC);
CREATE INDEX IF NOT EXISTS idx_qb_basic_stats_pass_tds ON qb_basic_stats(pass_tds DESC);
CREATE INDEX IF NOT EXISTS idx_qb_basic_stats_completion_pct ON qb_basic_stats(completion_pct DESC);

-- Advanced Stats Indexes
CREATE INDEX IF NOT EXISTS idx_qb_advanced_stats_season ON qb_advanced_stats(season);
CREATE INDEX IF NOT EXISTS idx_qb_advanced_stats_qbr ON qb_advanced_stats(qbr DESC);

-- Splits Indexes
CREATE INDEX IF NOT EXISTS idx_qb_splits_pfr_id ON qb_splits(pfr_id);
CREATE INDEX IF NOT EXISTS idx_qb_splits_season ON qb_splits(season);
CREATE INDEX IF NOT EXISTS idx_qb_splits_split_type ON qb_splits(split_type);
CREATE INDEX IF NOT EXISTS idx_qb_splits_split_category ON qb_splits(split_category);
CREATE INDEX IF NOT EXISTS idx_qb_splits_player_season ON qb_splits(pfr_id, season);
CREATE INDEX IF NOT EXISTS idx_qb_splits_type_category ON qb_splits(split_type, split_category);

-- Game Log Indexes
CREATE INDEX IF NOT EXISTS idx_game_log_pfr_id ON qb_game_log(pfr_id);
CREATE INDEX IF NOT EXISTS idx_game_log_season ON qb_game_log(season);
CREATE INDEX IF NOT EXISTS idx_game_log_week ON qb_game_log(week);
CREATE INDEX IF NOT EXISTS idx_game_log_game_date ON qb_game_log(game_date);
CREATE INDEX IF NOT EXISTS idx_game_log_opponent ON qb_game_log(opponent);
CREATE INDEX IF NOT EXISTS idx_game_log_home_away ON qb_game_log(home_away);

-- Scraping Log Indexes
CREATE INDEX IF NOT EXISTS idx_scraping_log_session_id ON scraping_log(session_id);
CREATE INDEX IF NOT EXISTS idx_scraping_log_season ON scraping_log(season);
CREATE INDEX IF NOT EXISTS idx_scraping_log_start_time ON scraping_log(start_time);

-- Composite Indexes for Common Queries
CREATE INDEX IF NOT EXISTS idx_qb_basic_stats_season_rating ON qb_basic_stats(season, rating DESC);
CREATE INDEX IF NOT EXISTS idx_qb_basic_stats_team_season ON qb_basic_stats(team, season);
CREATE INDEX IF NOT EXISTS idx_qb_splits_season_type ON qb_splits(season, split_type);

-- Updated At Trigger Function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply Updated At Triggers
CREATE TRIGGER update_players_updated_at 
    BEFORE UPDATE ON players 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_qb_basic_stats_updated_at 
    BEFORE UPDATE ON qb_basic_stats 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_qb_advanced_stats_updated_at 
    BEFORE UPDATE ON qb_advanced_stats 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_qb_splits_updated_at 
    BEFORE UPDATE ON qb_splits 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Useful Views for Analytics
-- QB Season Summary View (combines basic and advanced stats)
CREATE OR REPLACE VIEW qb_season_summary AS
SELECT 
    p.pfr_id,
    p.player_name,
    p.first_name,
    p.last_name,
    p.position,
    p.college,
    p.draft_year,
    p.draft_round,
    p.draft_pick,
    bs.season,
    bs.team,
    bs.games_played,
    bs.games_started,
    bs.completions,
    bs.attempts,
    bs.completion_pct,
    bs.pass_yards,
    bs.pass_tds,
    bs.interceptions,
    bs.longest_pass,
    bs.rating,
    bs.sacks,
    bs.sack_yards,
    bs.net_yards_per_attempt,
    -- Advanced stats
    adv.qbr,
    adv.adjusted_net_yards_per_attempt,
    adv.fourth_quarter_comebacks,
    adv.game_winning_drives,
    -- Calculated fields
    CASE 
        WHEN bs.attempts > 0 THEN ROUND((bs.pass_yards::DECIMAL / bs.attempts), 2)
        ELSE NULL 
    END as yards_per_attempt,
    CASE 
        WHEN bs.attempts > 0 THEN ROUND((bs.pass_tds::DECIMAL / bs.attempts * 100), 2)
        ELSE NULL 
    END as td_percentage,
    CASE 
        WHEN bs.attempts > 0 THEN ROUND((bs.interceptions::DECIMAL / bs.attempts * 100), 2)
        ELSE NULL 
    END as int_percentage
FROM players p
JOIN qb_basic_stats bs ON p.pfr_id = bs.pfr_id
LEFT JOIN qb_advanced_stats adv ON p.pfr_id = adv.pfr_id AND bs.season = adv.season
WHERE p.position = 'QB';

-- QB Home/Away Splits View
CREATE OR REPLACE VIEW qb_home_away_splits AS
SELECT 
    p.pfr_id,
    p.player_name,
    s.season,
    s.split_category,
    s.games,
    s.completions,
    s.attempts,
    s.completion_pct,
    s.pass_yards,
    s.pass_tds,
    s.interceptions,
    s.rating,
    s.sacks,
    s.net_yards_per_attempt,
    s.rush_attempts,
    s.rush_yards,
    s.rush_tds,
    s.total_tds,
    s.wins,
    s.losses,
    s.ties,
    CASE 
        WHEN s.games > 0 THEN ROUND(s.wins::DECIMAL / s.games * 100, 1)
        ELSE NULL 
    END as win_percentage
FROM players p
JOIN qb_splits s ON p.pfr_id = s.pfr_id
WHERE s.split_type = 'basic_splits' 
AND s.split_category IN ('Home', 'Road')
AND p.position = 'QB';

-- QB Quarter Performance View
CREATE OR REPLACE VIEW qb_quarter_performance AS
SELECT 
    p.pfr_id,
    p.player_name,
    s.season,
    s.split_category,
    s.games,
    s.completions,
    s.attempts,
    s.completion_pct,
    s.pass_yards,
    s.pass_tds,
    s.interceptions,
    s.rating,
    s.net_yards_per_attempt,
    CASE 
        WHEN s.attempts > 0 THEN ROUND(s.pass_yards::DECIMAL / s.attempts, 2)
        ELSE NULL 
    END as yards_per_attempt
FROM players p
JOIN qb_splits s ON p.pfr_id = s.pfr_id
WHERE s.split_type = 'advanced_splits' 
AND s.split_category IN ('1st Qtr', '2nd Qtr', '3rd Qtr', '4th Qtr', 'OT')
AND p.position = 'QB';

-- QB Red Zone Performance View
CREATE OR REPLACE VIEW qb_red_zone_performance AS
SELECT 
    p.pfr_id,
    p.player_name,
    s.season,
    s.split_category,
    s.games,
    s.completions,
    s.attempts,
    s.completion_pct,
    s.pass_yards,
    s.pass_tds,
    s.interceptions,
    s.rating,
    s.net_yards_per_attempt,
    CASE 
        WHEN s.attempts > 0 THEN ROUND(s.pass_tds::DECIMAL / s.attempts * 100, 2)
        ELSE NULL 
    END as td_percentage
FROM players p
JOIN qb_splits s ON p.pfr_id = s.pfr_id
WHERE s.split_type = 'advanced_splits' 
AND s.split_category IN ('Red Zone', 'Opp 1-10')
AND p.position = 'QB';

-- QB vs Winning Teams View
CREATE OR REPLACE VIEW qb_vs_winning_teams AS
SELECT 
    p.pfr_id,
    p.player_name,
    s.season,
    s.split_category,
    s.games,
    s.completions,
    s.attempts,
    s.completion_pct,
    s.pass_yards,
    s.pass_tds,
    s.interceptions,
    s.rating,
    s.net_yards_per_attempt,
    s.wins,
    s.losses,
    s.ties,
    CASE 
        WHEN s.games > 0 THEN ROUND(s.wins::DECIMAL / s.games * 100, 1)
        ELSE NULL 
    END as win_percentage
FROM players p
JOIN qb_splits s ON p.pfr_id = s.pfr_id
WHERE s.split_type = 'basic_splits' 
AND s.split_category IN ('0-7 points', '8-14 points', '15+ points')
AND p.position = 'QB';

-- Functions for Data Retrieval
CREATE OR REPLACE FUNCTION get_qb_stats_by_season(target_season INTEGER)
RETURNS TABLE (
    pfr_id VARCHAR(20),
    player_name VARCHAR(100),
    team VARCHAR(3),
    games_played INTEGER,
    completions INTEGER,
    attempts INTEGER,
    completion_pct DECIMAL(5,2),
    pass_yards INTEGER,
    pass_tds INTEGER,
    interceptions INTEGER,
    rating DECIMAL(5,2),
    qbr DECIMAL(5,2),
    sacks INTEGER,
    net_yards_per_attempt DECIMAL(4,2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.pfr_id,
        p.player_name,
        bs.team,
        bs.games_played,
        bs.completions,
        bs.attempts,
        bs.completion_pct,
        bs.pass_yards,
        bs.pass_tds,
        bs.interceptions,
        bs.rating,
        adv.qbr,
        bs.sacks,
        bs.net_yards_per_attempt
    FROM players p
    JOIN qb_basic_stats bs ON p.pfr_id = bs.pfr_id
    LEFT JOIN qb_advanced_stats adv ON p.pfr_id = adv.pfr_id AND bs.season = adv.season
    WHERE bs.season = target_season
    AND p.position = 'QB'
    ORDER BY bs.rating DESC NULLS LAST;
END;
$$ LANGUAGE plpgsql;

-- Function to get QB splits by type
CREATE OR REPLACE FUNCTION get_qb_splits_by_type(
    target_pfr_id VARCHAR(20),
    target_season INTEGER,
    target_split_type VARCHAR(50)
)
RETURNS TABLE (
    split_category VARCHAR(100),
    games INTEGER,
    completions INTEGER,
    attempts INTEGER,
    completion_pct DECIMAL(5,2),
    pass_yards INTEGER,
    pass_tds INTEGER,
    interceptions INTEGER,
    rating DECIMAL(5,2),
    sacks INTEGER,
    net_yards_per_attempt DECIMAL(4,2),
    rush_attempts INTEGER,
    rush_yards INTEGER,
    rush_tds INTEGER,
    total_tds INTEGER,
    wins INTEGER,
    losses INTEGER,
    ties INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        s.split_category,
        s.games,
        s.completions,
        s.attempts,
        s.completion_pct,
        s.pass_yards,
        s.pass_tds,
        s.interceptions,
        s.rating,
        s.sacks,
        s.net_yards_per_attempt,
        s.rush_attempts,
        s.rush_yards,
        s.rush_tds,
        s.total_tds,
        s.wins,
        s.losses,
        s.ties
    FROM qb_splits s
    WHERE s.pfr_id = target_pfr_id
    AND s.season = target_season
    AND s.split_type = target_split_type
    ORDER BY s.split_category;
END;
$$ LANGUAGE plpgsql;

-- Database Statistics View
CREATE OR REPLACE VIEW database_stats AS
SELECT 
    'players' as table_name,
    COUNT(*) as record_count,
    MAX(created_at) as last_updated
FROM players
UNION ALL
SELECT 
    'qb_basic_stats' as table_name,
    COUNT(*) as record_count,
    MAX(updated_at) as last_updated
FROM qb_basic_stats
UNION ALL
SELECT 
    'qb_advanced_stats' as table_name,
    COUNT(*) as record_count,
    MAX(updated_at) as last_updated
FROM qb_advanced_stats
UNION ALL
SELECT 
    'qb_splits' as table_name,
    COUNT(*) as record_count,
    MAX(updated_at) as last_updated
FROM qb_splits
UNION ALL
SELECT 
    'qb_game_log' as table_name,
    COUNT(*) as record_count,
    MAX(scraped_at) as last_updated
FROM qb_game_log
UNION ALL
SELECT 
    'teams' as table_name,
    COUNT(*) as record_count,
    MAX(created_at) as last_updated
FROM teams
UNION ALL
SELECT 
    'scraping_log' as table_name,
    COUNT(*) as record_count,
    MAX(created_at) as last_updated
FROM scraping_log;

-- Enable Row Level Security
ALTER TABLE players ENABLE ROW LEVEL SECURITY;
ALTER TABLE qb_basic_stats ENABLE ROW LEVEL SECURITY;
ALTER TABLE qb_advanced_stats ENABLE ROW LEVEL SECURITY;
ALTER TABLE qb_splits ENABLE ROW LEVEL SECURITY;
ALTER TABLE qb_game_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE teams ENABLE ROW LEVEL SECURITY;
ALTER TABLE scraping_log ENABLE ROW LEVEL SECURITY; 