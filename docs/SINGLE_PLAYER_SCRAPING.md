# Single Player Scraping Guide

This guide shows you how to scrape data for a single NFL QB player using the improved schema with PFR IDs and separated tables.

## Quick Start (Easiest Method)

### 1. Configure the Player

Edit `player_config.py` and change these lines:

```python
PLAYER_NAME = "Joe Burrow"  # Change to any QB name
SEASON = 2024  # Change to any season year
SAVE_TO_DATABASE = True  # Set to False to only scrape without saving
```

### 2. Run the Script

```bash
python quick_scrape.py
```

That's it! The script will:
- Find the player's PFR URL automatically
- Extract their PFR ID (e.g., 'burrjo01' for Joe Burrow)
- Scrape basic stats (completions, yards, TDs, etc.)
- Scrape advanced stats (QBR, comebacks, game-winning drives)
- Scrape splits data (home/away, quarters, etc.)
- Save everything to your database

## Command Line Method

### Basic Usage

```bash
python scrape_single_player.py "Joe Burrow" 2024
```

### Options

```bash
# Scrape without saving to database
python scrape_single_player.py "Patrick Mahomes" 2023 --no-db

# Examples
python scrape_single_player.py "Josh Allen" 2024
python scrape_single_player.py "Lamar Jackson" 2023 --no-db
```

## Available Players

You can scrape any QB from Pro Football Reference. Here are some popular examples:

- Joe Burrow
- Patrick Mahomes
- Josh Allen
- Lamar Jackson
- Jalen Hurts
- Dak Prescott
- Justin Herbert
- Trevor Lawrence
- Tua Tagovailoa
- Brock Purdy

## What Gets Scraped

### 1. Player Information
- PFR unique ID (e.g., 'burrjo01')
- Player name and PFR URL
- Basic biographical info

### 2. Basic Stats (Season Totals)
- Games played/started
- Completions/attempts and completion percentage
- Passing yards, touchdowns, interceptions
- Longest pass, passer rating
- Sacks and sack yards
- Net yards per attempt

### 3. Advanced Stats
- ESPN QBR (Total Quarterback Rating)
- Adjusted net yards per attempt
- Fourth quarter comebacks
- Game-winning drives

### 4. Splits Data
- Home vs Away performance
- Performance by quarter
- Red zone efficiency
- Performance vs winning teams
- And many more situational splits

## Database Tables Used

The new schema uses these tables:

- `players` - Player master data with PFR ID
- `qb_basic_stats` - Basic season statistics
- `qb_advanced_stats` - Advanced metrics
- `qb_splits` - Situational splits data

## Configuration Options

Edit `player_config.py` to customize:

```python
# Player settings
PLAYER_NAME = "Joe Burrow"
SEASON = 2024

# Scraping behavior
SAVE_TO_DATABASE = True
RATE_LIMIT_DELAY = 2.0  # Be respectful to PFR servers

# What to scrape
SCRAPE_BASIC_STATS = True
SCRAPE_ADVANCED_STATS = True
SCRAPE_SPLITS = True

# Logging
LOG_LEVEL = "INFO"
LOG_TO_FILE = True
```

## Output Examples

### Successful Scrape
```
Quick Scrape - Joe Burrow (2024)
==================================================
2024-01-15 10:30:15 - __main__ - INFO - Starting scrape for Joe Burrow (2024 season)
2024-01-15 10:30:16 - __main__ - INFO - Found PFR ID: burrjo01
2024-01-15 10:30:16 - __main__ - INFO - Player URL: https://www.pro-football-reference.com/players/B/BurrJo01.htm
2024-01-15 10:30:17 - __main__ - INFO - Scraping basic stats...
2024-01-15 10:30:18 - __main__ - INFO - Found basic stats: 2800 yards, 18 TDs
2024-01-15 10:30:19 - __main__ - INFO - Scraping splits data...
2024-01-15 10:30:25 - __main__ - INFO - Found split: basic_splits - Home
2024-01-15 10:30:25 - __main__ - INFO - Found split: basic_splits - Road
2024-01-15 10:30:26 - __main__ - INFO - Data saved to database successfully
2024-01-15 10:30:26 - __main__ - INFO - Scraping completed for Joe Burrow

=== SCRAPING RESULTS FOR JOE BURROW (2024) ===
PFR ID: burrjo01
Player URL: https://www.pro-football-reference.com/players/B/BurrJo01.htm

Basic Stats:
  Team: CIN
  Games: 10 played, 10 started
  Passing: 245/360 (68.1%)
  Yards: 2800, TDs: 18, INTs: 8
  Rating: 95.2

Advanced Stats:
  QBR: 85.2
  ANY/A: 7.8
  4QC: 2, GWD: 3

Splits Found: 15
  basic_splits - Home
  basic_splits - Road
  advanced_splits - 1st Qtr
  advanced_splits - 2nd Qtr
  advanced_splits - 3rd Qtr

🎉 SUCCESS! Scraped data for Joe Burrow
📊 Found 15 splits
💾 Data saved to database
```

## Troubleshooting

### Common Issues

1. **Player not found**
   - Make sure the player name is spelled correctly
   - Try using the full name (e.g., "Joe Burrow" not just "Burrow")
   - Check if the player played in the specified season

2. **Database connection errors**
   - Make sure your database is running
   - Check your database configuration in `src/config/config.py`
   - Set `SAVE_TO_DATABASE = False` to test without database

3. **Rate limiting**
   - Increase `RATE_LIMIT_DELAY` in `player_config.py`
   - Wait a few minutes and try again

4. **No splits data**
   - Some players may not have splits data for certain seasons
   - This is normal and not an error

### Logs

Check the logs for detailed information:
- `logs/single_player_scraping.log` - Detailed scraping logs
- `logs/main.log` - General application logs

## Advanced Usage

### Scraping Multiple Players

Create a script to scrape multiple players:

```python
from scrape_single_player import scrape_single_player

players = ["Joe Burrow", "Patrick Mahomes", "Josh Allen"]
season = 2024

for player in players:
    print(f"Scraping {player}...")
    results = scrape_single_player(player, season, save_to_db=True)
    if results['success']:
        print(f"✓ Successfully scraped {player}")
    else:
        print(f"✗ Failed to scrape {player}")
```

### Custom Database URL

If you want to use a different database:

```python
# In player_config.py
DATABASE_URL = "postgresql://username:password@localhost:5432/nfl_qb_data"
```

Then modify the scraping script to use this URL.

## Data Quality

The scraper includes comprehensive validation:

- Logical consistency checks (e.g., completions ≤ attempts)
- Range validation for all numeric fields
- PFR ID extraction and validation
- Data type validation

All validation errors are logged as warnings, so you can review them in the logs.

## Performance

- **Rate Limiting**: Default 2-second delay between requests
- **Error Handling**: Comprehensive retry logic for failed requests
- **Logging**: Detailed logs for debugging and monitoring
- **Database**: Efficient bulk inserts and proper connection management

## Next Steps

After scraping a player, you can:

1. **Query the data** using the new schema
2. **Analyze performance** using the database views
3. **Compare players** across different seasons
4. **Build analytics** on the comprehensive dataset

The new schema with PFR IDs and separated tables makes it easy to build sophisticated NFL QB analytics! 