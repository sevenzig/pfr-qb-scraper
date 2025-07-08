#!/usr/bin/env python3
"""
Configuration file for single player scraping
Modify these settings to customize your scraping behavior
"""

# Player to scrape
PLAYER_NAME = "Joe Burrow"  # Change this to any QB name
SEASON = 2024  # Change this to any season year

# Scraping settings
SAVE_TO_DATABASE = True  # Set to False to only scrape without saving
RATE_LIMIT_DELAY = 2.0  # Seconds between requests (be respectful!)

# Database settings (if using local database)
DATABASE_URL = None  # Set to your database URL if different from config

# Logging settings
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_TO_FILE = True  # Whether to save logs to file

# What to scrape
SCRAPE_BASIC_STATS = True  # Season totals (completions, yards, TDs, etc.)
SCRAPE_ADVANCED_STATS = True  # QBR, comebacks, game-winning drives
SCRAPE_SPLITS = True  # Situational splits (home/away, quarters, etc.)

# Example player names you can use:
EXAMPLE_PLAYERS = [
    "Joe Burrow",
    "Patrick Mahomes", 
    "Josh Allen",
    "Lamar Jackson",
    "Jalen Hurts",
    "Dak Prescott",
    "Justin Herbert",
    "Trevor Lawrence",
    "Tua Tagovailoa",
    "Brock Purdy"
] 