# NFL QB Data Schema Improvements

## Overview

This document outlines the major improvements made to the NFL QB data scraping
project schema to enhance data quality, normalization, and maintainability.

## Key Improvements

### 1. PFR Unique IDs as Primary Keys

**Before**: Used generated player IDs based on player names **After**: Use PFR
unique IDs (e.g., 'burrjo01' for Joe Burrow) as primary keys

**Benefits**:

- Consistent identification across different data sources
- No conflicts from name variations or duplicates
- Direct mapping to Pro Football Reference URLs
- Better data integrity and referential consistency

**Implementation**:

- Added `extract_pfr_id()` function to parse PFR URLs
- Updated `generate_player_id()` to prioritize PFR IDs
- All tables now use `pfr_id` as the primary key or foreign key

### 2. Separated Basic and Advanced Statistics

**Before**: Single `qb_stats` table with all statistics mixed together
**After**: Three separate tables:

- `players` - Player master data
- `qb_basic_stats` - Basic season statistics
- `qb_advanced_stats` - Advanced metrics

**Benefits**:

- Better data normalization
- Easier to maintain and extend
- Clear separation of concerns
- More efficient queries for specific data types

**Table Structure**:

#### Players Table

````sql
CREATE TABLE players (
    pfr_id VARCHAR(20) PRIMARY KEY,  -- PFR unique ID
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
```text
#### QB Basic Stats Table

```sql
CREATE TABLE qb_basic_stats (
    pfr_id VARCHAR(20) NOT NULL,
    season INTEGER NOT NULL,
    team VARCHAR(3) NOT NULL,
    games_played INTEGER DEFAULT 0,
    games_started INTEGER DEFAULT 0,
    completions INTEGER DEFAULT 0,
    attempts INTEGER DEFAULT 0,
    completion_pct DECIMAL(5,2),
    pass_yards INTEGER DEFAULT 0,
    pass_tds INTEGER DEFAULT 0,
    interceptions INTEGER DEFAULT 0,
    longest_pass INTEGER DEFAULT 0,
    rating DECIMAL(5,2),
    sacks INTEGER DEFAULT 0,
    sack_yards INTEGER DEFAULT 0,
    net_yards_per_attempt DECIMAL(4,2),
    PRIMARY KEY (pfr_id, season),
    FOREIGN KEY (pfr_id) REFERENCES players(pfr_id) ON DELETE CASCADE,
    FOREIGN KEY (team) REFERENCES teams(team_code) ON DELETE RESTRICT
);
```text
#### QB Advanced Stats Table

```sql
CREATE TABLE qb_advanced_stats (
    pfr_id VARCHAR(20) NOT NULL,
    season INTEGER NOT NULL,
    qbr DECIMAL(5,2),
    adjusted_net_yards_per_attempt DECIMAL(4,2),
    fourth_quarter_comebacks INTEGER DEFAULT 0,
    game_winning_drives INTEGER DEFAULT 0,
    PRIMARY KEY (pfr_id, season),
    FOREIGN KEY (pfr_id) REFERENCES players(pfr_id) ON DELETE CASCADE
);
```text
### 3. Enhanced QB Splits Table

**Improvements**:

- Added comprehensive rush statistics
- Added fumble statistics (total, lost, forced, recovered)
- Added game outcome statistics (wins, losses, ties)
- Added per-game averages
- Added total touchdowns and points
- Better validation constraints

**New Fields**:

- `rush_attempts`, `rush_yards`, `rush_tds`
- `fumbles`, `fumbles_lost`, `fumbles_forced`, `fumbles_recovered`
- `fumble_recovery_yards`, `fumble_recovery_tds`
- `incompletions`
- `wins`, `losses`, `ties`
- `attempts_per_game`, `yards_per_game`
- `rush_attempts_per_game`, `rush_yards_per_game`
- `total_tds`, `points`

### 4. Improved Data Validation

**Enhanced Constraints**:

- Logical consistency checks (e.g., completions ≤ attempts)
- Range validation for all numeric fields
- Foreign key relationships with proper cascade/restrict rules
- Check constraints for business rules

**Examples**:

```sql
CONSTRAINT valid_completion_ratio CHECK (attempts = 0 OR (completions <= attempts))
CONSTRAINT valid_fumbles_lost CHECK (fumbles_lost <= fumbles)
CONSTRAINT valid_total_tds CHECK (total_tds >= (pass_tds + rush_tds + fumble_recovery_tds))
```text
### 5. Updated Python Models

**New Model Classes**:

- `Player` - Player master data with PFR ID
- `QBBasicStats` - Basic season statistics
- `QBAdvancedStats` - Advanced metrics
- `QBSplitStats` - Enhanced splits with all additional fields
- `Team` - Team information
- `ScrapingLog` - Enhanced logging with separated stats counts

**Features**:

- Comprehensive validation methods
- `from_dict()` factory methods
- Type hints for all fields
- Proper default values
- Dataclass decorators for clean syntax

### 6. Enhanced Database Views

**New Views**:

- `qb_season_summary` - Combines basic and advanced stats
- `qb_home_away_splits` - Home vs away performance
- `qb_quarter_performance` - Performance by quarter
- `qb_red_zone_performance` - Red zone efficiency
- `qb_vs_winning_teams` - Performance vs quality opponents

**Benefits**:

- Pre-computed common queries
- Consistent data presentation
- Performance optimization
- Easier application development

### 7. Improved Indexing Strategy

**New Indexes**:

- Composite indexes for common query patterns
- Performance indexes for sorting and filtering
- Foreign key indexes for join optimization

**Examples**:

```sql
CREATE INDEX idx_qb_basic_stats_season_rating ON qb_basic_stats(season, rating DESC);
CREATE INDEX idx_qb_splits_player_season ON qb_splits(pfr_id, season);
CREATE INDEX idx_qb_basic_stats_team_season ON qb_basic_stats(team, season);
```text
## Migration Strategy

### For Existing Data

1. **Extract PFR IDs**: Use the new `extract_pfr_id()` function to identify PFR
   IDs from existing URLs
2. **Create Players**: Insert player records with PFR IDs as primary keys
3. **Split Statistics**: Separate existing `qb_stats` data into `qb_basic_stats`
   and `qb_advanced_stats`
4. **Update Foreign Keys**: Update all references to use PFR IDs instead of
   generated IDs
5. **Validate Data**: Run validation on all migrated data

### For New Data

1. **Use PFR URLs**: Always scrape player URLs to get PFR IDs
2. **Separate Data**: Store basic and advanced stats in separate tables
3. **Enhanced Splits**: Use the new comprehensive splits structure
4. **Validate**: Run validation on all new data before insertion

## Benefits Summary

### Data Quality

- Consistent player identification
- Better data normalization
- Comprehensive validation
- Reduced data redundancy

### Performance

- Optimized indexes for common queries
- Separated tables for focused queries
- Better join performance with proper foreign keys

### Maintainability

- Clear table structure
- Separated concerns
- Comprehensive documentation
- Type-safe Python models

### Extensibility

- Easy to add new player attributes
- Flexible splits structure
- Modular design for future enhancements

## Testing

All improvements have been tested with comprehensive test suites:

- PFR ID extraction and generation
- Model validation and serialization
- Database schema constraints
- Data integrity checks

## Next Steps

1. **Database Migration**: Create migration scripts for existing data
2. **Scraper Updates**: Update all scrapers to use new models
3. **Application Updates**: Update any applications using the old schema
4. **Documentation**: Update API documentation and user guides
5. **Monitoring**: Add monitoring for data quality and performance

## Files Modified

- `sql/schema.sql` - Complete schema rewrite
- `src/lib/db/schema.ts` - TypeScript schema updates
- `src/models/qb_models.py` - New Python models
- `src/models/__init__.py` - Updated imports
- `src/utils/data_utils.py` - PFR ID extraction functions
- `src/scrapers/enhanced_scraper.py` - Updated to use new models
- `test_new_schema.py` - Comprehensive test suite

This represents a significant improvement in the project's data architecture,
making it more robust, maintainable, and scalable for future NFL data analysis
needs.
````
