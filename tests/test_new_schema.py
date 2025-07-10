#!/usr/bin/env python3
"""
Test script to verify the new schema with PFR IDs and separated tables
"""

import sys
import os
from datetime import datetime, date
from typing import List

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models.qb_models import Player, QBBasicStats, QBAdvancedStats, QBSplitStats, Team, ScrapingLog
from utils.data_utils import generate_player_id, extract_pfr_id

def test_pfr_id_extraction():
    """Test PFR ID extraction from URLs"""
    print("Testing PFR ID extraction...")
    
    test_cases = [
        ("https://www.pro-football-reference.com/players/B/BurrJo01.htm", "burrjo01"),
        ("https://www.pro-football-reference.com/players/M/MahoPa00.htm", "mahopa00"),
        ("https://www.pro-football-reference.com/players/B/BradTo00.htm", "bradto00"),
        ("https://www.pro-football-reference.com/players/R/RogeAa00.htm", "rogeaa00"),
        ("invalid_url", None),
        ("", None),
    ]
    
    for url, expected in test_cases:
        result = extract_pfr_id(url)
        status = "✓" if result == expected else "✗"
        print(f"  {status} {url} -> {result} (expected: {expected})")

def test_player_id_generation():
    """Test player ID generation with PFR URLs"""
    print("\nTesting player ID generation...")
    
    test_cases = [
        ("Joe Burrow", "https://www.pro-football-reference.com/players/B/BurrJo01.htm", "burrjo01"),
        ("Patrick Mahomes", "https://www.pro-football-reference.com/players/M/MahoPa00.htm", "mahopa00"),
        ("Tom Brady", "https://www.pro-football-reference.com/players/B/BradTo00.htm", "bradto00"),
        ("Aaron Rodgers", "https://www.pro-football-reference.com/players/R/RogeAa00.htm", "rogeaa00"),
        ("Unknown Player", None, "unknownplayer"),  # Fallback to name-based ID
    ]
    
    for name, url, expected in test_cases:
        result = generate_player_id(name, url)
        status = "✓" if result == expected else "✗"
        print(f"  {status} {name} -> {result} (expected: {expected})")

def test_player_model():
    """Test Player model with PFR ID"""
    print("\nTesting Player model...")
    
    player = Player(
        pfr_id="burrjo01",
        player_name="Joe Burrow",
        first_name="Joe",
        last_name="Burrow",
        position="QB",
        height_inches=76,
        weight_lbs=221,
        birth_date=date(1996, 12, 10),
        age=27,
        college="LSU",
        draft_year=2020,
        draft_round=1,
        draft_pick=1,
        pfr_url="https://www.pro-football-reference.com/players/B/BurrJo01.htm",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    # Test validation
    errors = player.validate()
    if errors:
        print(f"  ✗ Player validation errors: {errors}")
    else:
        print("  ✓ Player validation passed")
    
    # Test from_dict
    player_dict = {
        'pfr_id': 'burrjo01',
        'player_name': 'Joe Burrow',
        'first_name': 'Joe',
        'last_name': 'Burrow',
        'position': 'QB',
        'height_inches': 76,
        'weight_lbs': 221,
        'birth_date': date(1996, 12, 10),
        'age': 27,
        'college': 'LSU',
        'draft_year': 2020,
        'draft_round': 1,
        'draft_pick': 1,
        'pfr_url': 'https://www.pro-football-reference.com/players/B/BurrJo01.htm'
    }
    
    player_from_dict = Player.from_dict(player_dict)
    if player_from_dict.pfr_id == "burrjo01":
        print("  ✓ Player.from_dict() works correctly")
    else:
        print("  ✗ Player.from_dict() failed")

def test_basic_stats_model():
    """Test QBBasicStats model (aliased to QBPassingStats)"""
    print("\nTesting QBBasicStats model...")
    
    # Using the actual field names from QBPassingStats model
    basic_stats = QBBasicStats(
        pfr_id="burrjo01",
        player_name="Joe Burrow",
        player_url="https://www.pro-football-reference.com/players/B/BurrJo01.htm",
        season=2024,
        rk=1,                    # Rank
        age=27,                  # Age
        team="CIN",              # Team
        pos="QB",                # Position
        g=10,                    # Games
        gs=10,                   # Games Started
        qb_rec="6-4-0",          # QB Record
        cmp=245,                 # Completions
        att=360,                 # Attempts
        cmp_pct=68.1,            # Completion %
        yds=2800,                # Yards
        td=18,                   # Touchdowns
        td_pct=5.0,              # TD %
        int=8,                   # Interceptions
        int_pct=2.2,             # Int %
        first_downs=140,         # First Downs
        succ_pct=65.0,           # Success %
        lng=75,                  # Longest pass
        y_a=7.8,                 # Y/A
        ay_a=8.2,                # AY/A
        y_c=11.4,                # Y/C
        y_g=280.0,               # Y/G
        rate=95.2,               # Passer Rating
        qbr=85.2,                # QBR
        sk=25,                   # Sacks
        sk_yds=180,              # Sack Yards
        sk_pct=6.5,              # Sack %
        ny_a=7.2,                # NY/A
        any_a=7.6,               # ANY/A
        four_qc=2,               # 4QC
        gwd=3,                   # GWD
        awards="",               # Awards
        player_additional="",    # Player-additional
        scraped_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    # Test validation
    errors = basic_stats.validate()
    if errors:
        print(f"  ✗ Basic stats validation errors: {errors}")
    else:
        print("  ✓ Basic stats validation passed")
    
    # Test from_dict
    stats_dict = {
        'pfr_id': 'burrjo01',
        'player_name': 'Joe Burrow',
        'player_url': 'https://www.pro-football-reference.com/players/B/BurrJo01.htm',
        'season': 2024,
        'team': 'CIN',
        'g': 10,
        'gs': 10,
        'cmp': 245,
        'att': 360,
        'cmp_pct': 68.1,
        'yds': 2800,
        'td': 18,
        'int': 8,
        'lng': 75,
        'rate': 95.2,
        'sk': 25,
        'sk_yds': 180,
        'ny_a': 7.2
    }
    
    stats_from_dict = QBBasicStats.from_dict(stats_dict)
    if stats_from_dict.pfr_id == "burrjo01" and stats_from_dict.season == 2024:
        print("  ✓ QBBasicStats.from_dict() works correctly")
    else:
        print("  ✗ QBBasicStats.from_dict() failed")

def test_advanced_stats_model():
    """Test QBAdvancedStats model (aliased to QBSplitsType2)"""
    print("\nTesting QBAdvancedStats model...")
    
    # Using the actual field names from QBSplitsType2 model
    advanced_stats = QBAdvancedStats(
        pfr_id="burrjo01",
        player_name="Joe Burrow",
        season=2024,
        split="Down",            # Split type
        value="1st",             # Split value
        cmp=180,                 # Completions
        att=250,                 # Attempts
        inc=70,                  # Incompletions
        cmp_pct=72.0,            # Completion %
        yds=2100,                # Passing Yards
        td=15,                   # Passing TDs
        first_downs=120,         # First Downs
        int=5,                   # Interceptions
        rate=98.5,               # Passer Rating
        sk=15,                   # Sacks
        sk_yds=110,              # Sack Yards
        y_a=8.4,                 # Y/A
        ay_a=8.8,                # AY/A
        rush_att=20,             # Rush Attempts
        rush_yds=120,            # Rush Yards
        rush_y_a=6.0,            # Rush Y/A
        rush_td=2,               # Rush TDs
        rush_first_downs=8,      # Rush First Downs
        scraped_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    # Test validation
    errors = advanced_stats.validate()
    if errors:
        print(f"  ✗ Advanced stats validation errors: {errors}")
    else:
        print("  ✓ Advanced stats validation passed")
    
    # Test from_dict
    adv_dict = {
        'pfr_id': 'burrjo01',
        'player_name': 'Joe Burrow',
        'season': 2024,
        'split': 'Down',
        'value': '1st',
        'cmp': 180,
        'att': 250,
        'cmp_pct': 72.0,
        'yds': 2100,
        'td': 15,
        'first_downs': 120,
        'int': 5,
        'rate': 98.5,
        'sk': 15,
        'sk_yds': 110,
        'y_a': 8.4,
        'ay_a': 8.8,
        'rush_att': 20,
        'rush_yds': 120,
        'rush_y_a': 6.0,
        'rush_td': 2,
        'rush_first_downs': 8
    }
    
    adv_from_dict = QBAdvancedStats.from_dict(adv_dict)
    if adv_from_dict.pfr_id == "burrjo01" and adv_from_dict.split == "Down":
        print("  ✓ QBAdvancedStats.from_dict() works correctly")
    else:
        print("  ✗ QBAdvancedStats.from_dict() failed")

def test_splits_model():
    """Test QBSplitStats model (aliased to QBSplitsType1)"""
    print("\nTesting QBSplitStats model...")
    
    # Using the actual field names from QBSplitsType1 model
    splits_stats = QBSplitStats(
        pfr_id="burrjo01",
        player_name="Joe Burrow",
        season=2024,
        split="Place",           # Split type
        value="Home",            # Split value
        g=8,                     # Games
        w=6,                     # Wins
        l=2,                     # Losses
        t=0,                     # Ties
        cmp=223,                 # Completions
        att=299,                 # Attempts
        inc=76,                  # Incompletions
        cmp_pct=74.58,           # Completion %
        yds=2338,                # Passing Yards
        td=23,                   # Passing TDs
        int=4,                   # Interceptions
        rate=116.90,             # Passer Rating
        sk=25,                   # Sacks
        sk_yds=160,              # Sack Yards
        y_a=7.82,                # Y/A
        ay_a=8.1,                # AY/A
        a_g=37.4,                # A/G
        y_g=292.3,               # Y/G
        rush_att=15,             # Rush Attempts
        rush_yds=89,             # Rush Yards
        rush_y_a=5.9,            # Rush Y/A
        rush_td=2,               # Rush TDs
        rush_a_g=1.9,            # Rush A/G
        rush_y_g=11.1,           # Rush Y/G
        total_td=25,             # Total TDs
        pts=168,                 # Points
        fmb=3,                   # Fumbles
        fl=1,                    # Fumbles Lost
        ff=0,                    # Fumbles Forced
        fr=0,                    # Fumbles Recovered
        fr_yds=0,                # Fumble Recovery Yards
        fr_td=0,                 # Fumble Recovery TDs
        scraped_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    # Test validation
    errors = splits_stats.validate()
    if errors:
        print(f"  ✗ Splits stats validation errors: {errors}")
    else:
        print("  ✓ Splits stats validation passed")
    
    # Test from_dict
    splits_dict = {
        'pfr_id': 'burrjo01',
        'player_name': 'Joe Burrow',
        'season': 2024,
        'split': 'Place',
        'value': 'Home',
        'g': 8,
        'w': 6,
        'l': 2,
        't': 0,
        'cmp': 223,
        'att': 299,
        'cmp_pct': 74.58,
        'yds': 2338,
        'td': 23,
        'int': 4,
        'rate': 116.90,
        'sk': 25,
        'sk_yds': 160,
        'y_a': 7.82,
        'ay_a': 8.1,
        'a_g': 37.4,
        'y_g': 292.3,
        'rush_att': 15,
        'rush_yds': 89,
        'rush_y_a': 5.9,
        'rush_td': 2,
        'rush_a_g': 1.9,
        'rush_y_g': 11.1,
        'total_td': 25,
        'pts': 168,
        'fmb': 3,
        'fl': 1,
        'ff': 0,
        'fr': 0,
        'fr_yds': 0,
        'fr_td': 0
    }
    
    splits_from_dict = QBSplitStats.from_dict(splits_dict)
    if splits_from_dict.pfr_id == "burrjo01" and splits_from_dict.split == "Place":
        print("  ✓ QBSplitStats.from_dict() works correctly")
    else:
        print("  ✗ QBSplitStats.from_dict() failed")

def test_team_model():
    """Test Team model"""
    print("\nTesting Team model...")
    
    team = Team(
        team_code="CIN",
        team_name="Bengals",
        city="Cincinnati",
        conference="AFC",
        division="North",
        founded_year=1968,
        stadium_name="Paycor Stadium",
        stadium_capacity=65515,
        created_at=datetime.now()
    )
    
    # Test validation
    errors = team.validate()
    if errors:
        print(f"  ✗ Team validation errors: {errors}")
    else:
        print("  ✓ Team validation passed")
    
    # Test from_dict
    team_dict = {
        'team_code': 'CIN',
        'team_name': 'Bengals',
        'city': 'Cincinnati',
        'conference': 'AFC',
        'division': 'North',
        'founded_year': 1968,
        'stadium_name': 'Paycor Stadium',
        'stadium_capacity': 65515
    }
    
    team_from_dict = Team.from_dict(team_dict)
    if team_from_dict.team_code == "CIN":
        print("  ✓ Team.from_dict() works correctly")
    else:
        print("  ✗ Team.from_dict() failed")

def test_scraping_log_model():
    """Test ScrapingLog model"""
    print("\nTesting ScrapingLog model...")
    
    log = ScrapingLog(
        session_id="test_session_123",
        season=2024,
        start_time=datetime.now(),
        end_time=datetime.now(),
        total_requests=100,
        successful_requests=95,
        failed_requests=5,
        total_players=50,
        total_passing_stats=50,
        total_splits_type1=200,
        total_splits_type2=150,
        errors=["Error 1", "Error 2"],
        warnings=["Warning 1"],
        rate_limit_violations=2,
        processing_time_seconds=300.5,
        created_at=datetime.now()
    )
    
    # Test validation
    errors = log.validate()
    if errors:
        print(f"  ✗ ScrapingLog validation errors: {errors}")
    else:
        print("  ✓ ScrapingLog validation passed")
    
    # Test from_dict
    log_dict = {
        'session_id': 'test_session_123',
        'season': 2024,
        'start_time': datetime.now(),
        'end_time': datetime.now(),
        'total_requests': 100,
        'successful_requests': 95,
        'failed_requests': 5,
        'total_players': 50,
        'total_passing_stats': 50,
        'total_splits_type1': 200,
        'total_splits_type2': 150,
        'errors': ["Error 1", "Error 2"],
        'warnings': ["Warning 1"],
        'rate_limit_violations': 2,
        'processing_time_seconds': 300.5
    }
    
    log_from_dict = ScrapingLog.from_dict(log_dict)
    if log_from_dict.session_id == "test_session_123":
        print("  ✓ ScrapingLog.from_dict() works correctly")
    else:
        print("  ✗ ScrapingLog.from_dict() failed")

def main():
    """Run all tests"""
    print("Testing New Schema with PFR IDs")
    print("=" * 50)
    
    # Test utility functions
    test_pfr_id_extraction()
    test_player_id_generation()
    
    # Test models
    test_player_model()
    test_basic_stats_model()
    test_advanced_stats_model()
    test_splits_model()
    test_team_model()
    test_scraping_log_model()
    
    print("\n" + "=" * 50)
    print("✓ All tests completed!")

if __name__ == "__main__":
    main() 