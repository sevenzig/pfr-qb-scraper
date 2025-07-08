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
    """Test QBBasicStats model"""
    print("\nTesting QBBasicStats model...")
    
    basic_stats = QBBasicStats(
        pfr_id="burrjo01",
        season=2024,
        team="CIN",
        games_played=10,
        games_started=10,
        completions=245,
        attempts=360,
        completion_pct=68.1,
        pass_yards=2800,
        pass_tds=18,
        interceptions=8,
        longest_pass=75,
        rating=95.2,
        sacks=25,
        sack_yards=180,
        net_yards_per_attempt=7.2,
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
        'season': 2024,
        'team': 'CIN',
        'games_played': 10,
        'games_started': 10,
        'completions': 245,
        'attempts': 360,
        'completion_pct': 68.1,
        'pass_yards': 2800,
        'pass_tds': 18,
        'interceptions': 8,
        'longest_pass': 75,
        'rating': 95.2,
        'sacks': 25,
        'sack_yards': 180,
        'net_yards_per_attempt': 7.2
    }
    
    stats_from_dict = QBBasicStats.from_dict(stats_dict)
    if stats_from_dict.pfr_id == "burrjo01" and stats_from_dict.season == 2024:
        print("  ✓ QBBasicStats.from_dict() works correctly")
    else:
        print("  ✗ QBBasicStats.from_dict() failed")

def test_advanced_stats_model():
    """Test QBAdvancedStats model"""
    print("\nTesting QBAdvancedStats model...")
    
    advanced_stats = QBAdvancedStats(
        pfr_id="burrjo01",
        season=2024,
        qbr=85.2,
        adjusted_net_yards_per_attempt=7.8,
        fourth_quarter_comebacks=2,
        game_winning_drives=3,
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
        'season': 2024,
        'qbr': 85.2,
        'adjusted_net_yards_per_attempt': 7.8,
        'fourth_quarter_comebacks': 2,
        'game_winning_drives': 3
    }
    
    adv_from_dict = QBAdvancedStats.from_dict(adv_dict)
    if adv_from_dict.pfr_id == "burrjo01" and adv_from_dict.qbr == 85.2:
        print("  ✓ QBAdvancedStats.from_dict() works correctly")
    else:
        print("  ✗ QBAdvancedStats.from_dict() failed")

def test_splits_model():
    """Test QBSplitStats model with additional fields"""
    print("\nTesting QBSplitStats model...")
    
    split_stats = QBSplitStats(
        pfr_id="burrjo01",
        season=2024,
        split_type="basic_splits",
        split_category="Home",
        games=5,
        completions=120,
        attempts=175,
        completion_pct=68.6,
        pass_yards=1400,
        pass_tds=9,
        interceptions=3,
        rating=98.5,
        sacks=12,
        sack_yards=85,
        net_yards_per_attempt=7.5,
        rush_attempts=15,
        rush_yards=85,
        rush_tds=1,
        fumbles=2,
        fumbles_lost=1,
        fumbles_forced=0,
        fumbles_recovered=0,
        fumble_recovery_yards=0,
        fumble_recovery_tds=0,
        incompletions=55,
        wins=4,
        losses=1,
        ties=0,
        attempts_per_game=35.0,
        yards_per_game=280.0,
        rush_attempts_per_game=3.0,
        rush_yards_per_game=17.0,
        total_tds=10,
        points=60,
        scraped_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    # Test validation
    errors = split_stats.validate()
    if errors:
        print(f"  ✗ Split stats validation errors: {errors}")
    else:
        print("  ✓ Split stats validation passed")
    
    # Test from_dict
    split_dict = {
        'pfr_id': 'burrjo01',
        'season': 2024,
        'split_type': 'basic_splits',
        'split_category': 'Home',
        'games': 5,
        'completions': 120,
        'attempts': 175,
        'completion_pct': 68.6,
        'pass_yards': 1400,
        'pass_tds': 9,
        'interceptions': 3,
        'rating': 98.5,
        'sacks': 12,
        'sack_yards': 85,
        'net_yards_per_attempt': 7.5,
        'rush_attempts': 15,
        'rush_yards': 85,
        'rush_tds': 1,
        'fumbles': 2,
        'fumbles_lost': 1,
        'total_tds': 10,
        'wins': 4,
        'losses': 1
    }
    
    split_from_dict = QBSplitStats.from_dict(split_dict)
    if split_from_dict.pfr_id == "burrjo01" and split_from_dict.split_category == "Home":
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
    if team_from_dict.team_code == "CIN" and team_from_dict.conference == "AFC":
        print("  ✓ Team.from_dict() works correctly")
    else:
        print("  ✗ Team.from_dict() failed")

def test_scraping_log_model():
    """Test ScrapingLog model"""
    print("\nTesting ScrapingLog model...")
    
    log = ScrapingLog(
        session_id="test-session-123",
        season=2024,
        start_time=datetime.now(),
        end_time=datetime.now(),
        total_requests=100,
        successful_requests=95,
        failed_requests=5,
        total_players=32,
        total_basic_stats=32,
        total_advanced_stats=30,
        total_qb_splits=150,
        errors=["Rate limit hit once"],
        warnings=["Some data missing"],
        rate_limit_violations=1,
        processing_time_seconds=120.5,
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
        'session_id': 'test-session-123',
        'season': 2024,
        'start_time': datetime.now(),
        'end_time': datetime.now(),
        'total_requests': 100,
        'successful_requests': 95,
        'failed_requests': 5,
        'total_players': 32,
        'total_basic_stats': 32,
        'total_advanced_stats': 30,
        'total_qb_splits': 150,
        'errors': ["Rate limit hit once"],
        'warnings': ["Some data missing"],
        'rate_limit_violations': 1,
        'processing_time_seconds': 120.5
    }
    
    log_from_dict = ScrapingLog.from_dict(log_dict)
    if log_from_dict.session_id == "test-session-123" and log_from_dict.total_players == 32:
        print("  ✓ ScrapingLog.from_dict() works correctly")
    else:
        print("  ✗ ScrapingLog.from_dict() failed")

def main():
    """Run all tests"""
    print("Testing new schema with PFR IDs and separated tables")
    print("=" * 60)
    
    test_pfr_id_extraction()
    test_player_id_generation()
    test_player_model()
    test_basic_stats_model()
    test_advanced_stats_model()
    test_splits_model()
    test_team_model()
    test_scraping_log_model()
    
    print("\n" + "=" * 60)
    print("All tests completed!")

if __name__ == "__main__":
    main() 