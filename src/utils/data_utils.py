#!/usr/bin/env python3
"""
Data utility functions for NFL QB scraping system
Handles data validation, conversion, and normalization
"""

import re
import logging
from typing import Union, Optional, Dict, Any, List
from datetime import datetime
import pandas as pd
from io import StringIO

logger = logging.getLogger(__name__)

def safe_int(value: Any) -> Optional[int]:
    """Safely convert value to integer, returning None if conversion fails"""
    if value is None or value == '' or pd.isna(value):
        return None
    try:
        # Handle percentage strings like "70.55"
        if isinstance(value, str):
            value = value.replace('%', '')
        return int(float(str(value)))
    except (ValueError, TypeError):
        return None

def safe_float(value: Any) -> Optional[float]:
    """Safely convert value to float, returning None if conversion fails"""
    if value is None or value == '' or pd.isna(value):
        return None
    try:
        # Handle percentage strings like "70.55"
        if isinstance(value, str):
            value = value.replace('%', '')
        return float(str(value))
    except (ValueError, TypeError):
        return None

def safe_percentage(value: Any) -> Optional[float]:
    """Safely convert percentage value to float, handling % symbols"""
    if value is None or value == '' or pd.isna(value):
        return None
    try:
        if isinstance(value, str):
            value = value.replace('%', '')
        return float(str(value))
    except (ValueError, TypeError):
        return None

def clean_player_name(name: str) -> str:
    """Clean player name for consistent formatting"""
    if not name:
        return ""
    
    # Remove extra whitespace and normalize
    cleaned = re.sub(r'\s+', ' ', name.strip())
    
    # Handle common name variations
    cleaned = cleaned.replace(' Jr.', ' Jr')
    cleaned = cleaned.replace(' Sr.', ' Sr')
    cleaned = cleaned.replace(' III', '')
    cleaned = cleaned.replace(' II', '')
    cleaned = cleaned.replace(' IV', '')
    
    return cleaned

def extract_pfr_id(player_url: str) -> Optional[str]:
    """
    Extract PFR unique ID from player URL
    
    Args:
        player_url: Player's PFR URL (e.g., https://www.pro-football-reference.com/players/B/BurrJo01.htm)
        
    Returns:
        PFR unique ID (e.g., 'burrjo01') or None if not found
    """
    if not player_url:
        return None
    
    # Extract ID from URL pattern: /players/B/BurrJo01.htm
    match = re.search(r'/players/[A-Z]/([A-Za-z0-9]+)\.htm', player_url)
    if match:
        return match.group(1).lower()
    
    return None

def generate_player_id(player_name: str, player_url: Optional[str] = None) -> str:
    """
    Generate consistent player ID from name or PFR URL
    
    Args:
        player_name: Player's full name
        player_url: Player's PFR URL (optional)
        
    Returns:
        Consistent player ID (PFR ID if available, otherwise generated from name)
    """
    # Try to extract PFR ID first
    if player_url:
        pfr_id = extract_pfr_id(player_url)
        if pfr_id:
            return pfr_id
    
    # Fallback to name-based ID generation
    if not player_name:
        return ""
    
    # Convert to lowercase, remove spaces and special chars
    cleaned = ''.join(c.lower() for c in player_name if c.isalnum())
    return cleaned[:20]  # Limit to 20 characters

# ------------------------------------------------------------------
# URL helpers
# ------------------------------------------------------------------


def build_splits_url(pfr_id: str, season: int) -> str:
    """Construct the Pro-Football-Reference splits page URL for a given player and season.

    Args:
        pfr_id: The canonical 8-character PFR player identifier (e.g. ``'HurtJa00'`` → lowercase is fine).
        season: Season year.

    Returns:
        Full https URL to the splits page.
    """
    if not pfr_id or len(pfr_id) < 2:
        raise ValueError("Invalid PFR id")

    pfr_id = pfr_id.strip()
    first_letter = pfr_id[0].upper()
    # PFR uses the original case pattern e.g. BurrJo00, not Burrjo00
    player_code = pfr_id

    return f"https://www.pro-football-reference.com/players/{first_letter}/{player_code}/splits/{season}/"


def build_enhanced_splits_url(pfr_id: str, season: int, fallback_methods: bool = True) -> Optional[str]:
    """
    Enhanced splits URL construction with multiple fallback mechanisms
    
    Args:
        pfr_id: Player's PFR ID
        season: Season year
        fallback_methods: Whether to use fallback URL construction methods
        
    Returns:
        Constructed splits URL or None if all methods fail
    """
    if not pfr_id or not pfr_id.strip():
        logger.error("Invalid PFR ID provided for URL construction")
        return None
    
    pfr_id = pfr_id.strip()
    
    # Method 1: Use the standard build_splits_url function
    try:
        url = build_splits_url(pfr_id, season)
        logger.debug(f"Built splits URL using standard method: {url}")
        return url
    except Exception as e:
        logger.warning(f"Standard URL construction failed: {e}")
    
    if not fallback_methods:
        return None
    
    # Method 2: Handle different PFR ID formats
    try:
        if len(pfr_id) < 2:
            logger.error(f"PFR ID too short: {pfr_id}")
            return None
        
        first_letter = pfr_id[0].upper()
        
        # Handle different PFR ID formats
        if len(pfr_id) >= 8:
            # Standard format: BurrJo00
            player_code = pfr_id
        elif len(pfr_id) == 7:
            # Short format: burrjo01
            player_code = pfr_id
        else:
            # Very short format - try to pad
            player_code = pfr_id.ljust(7, '0')
        
        url = f"https://www.pro-football-reference.com/players/{first_letter}/{player_code}/splits/{season}/"
        logger.debug(f"Built splits URL using fallback method: {url}")
        return url
        
    except Exception as e:
        logger.error(f"Fallback URL construction failed: {e}")
        return None


def validate_splits_url(url: str) -> bool:
    """
    Validate a splits URL format
    
    Args:
        url: URL to validate
        
    Returns:
        True if URL format is valid, False otherwise
    """
    if not url:
        return False
    
    # Check basic URL structure
    expected_pattern = r'https://www\.pro-football-reference\.com/players/[A-Z]/[A-Za-z0-9]+/splits/\d{4}/'
    if not re.match(expected_pattern, url):
        return False
    
    # Check for valid season year
    season_match = re.search(r'/splits/(\d{4})/', url)
    if not season_match:
        return False
    
    season = int(season_match.group(1))
    if season < 1920 or season > 2030:
        return False
    
    return True


def extract_pfr_id_from_splits_url(url: str) -> Optional[str]:
    """
    Extract PFR ID from a splits URL
    
    Args:
        url: Splits URL
        
    Returns:
        PFR ID or None if extraction fails
    """
    if not url:
        return None
    
    # Pattern: /players/{first_letter}/{player_id}/splits/{season}/
    match = re.search(r'/players/[A-Z]/([A-Za-z0-9]+)/splits/\d{4}/', url)
    return match.group(1) if match else None


def build_splits_url_from_player_url(player_url: str, season: int) -> Optional[str]:
    """
    Build splits URL from a player's main page URL
    
    Args:
        player_url: Player's main PFR URL
        season: Season year
        
    Returns:
        Splits URL or None if construction fails
    """
    if not player_url:
        return None
    
    # Extract PFR ID from player URL
    pfr_id = extract_pfr_id(player_url)
    if not pfr_id:
        return None
    
    # Build splits URL using the extracted PFR ID
    return build_enhanced_splits_url(pfr_id, season)

def normalize_pfr_team_code(team_code: str) -> str:
    """
    Normalize team codes to match Pro Football Reference standards
    
    Args:
        team_code: Raw team code from PFR
        
    Returns:
        Standardized PFR team code
    """
    if not team_code:
        return ""
    
    # Clean the team code
    team_code = team_code.strip().upper()
    
    # Handle multi-team codes (like "2TM", "3TM")
    if re.match(r'\d+TM', team_code):
        return team_code  # Keep as-is for multi-team players
    
    # PFR team code mapping - standardize to PFR's current codes
    pfr_team_mapping = {
        # Handle variations and ensure we use PFR's standard codes
        'SF': 'SFO',           # San Francisco 49ers
        'GB': 'GNB',           # Green Bay Packers  
        'KC': 'KAN',           # Kansas City Chiefs
        'LV': 'LVR',           # Las Vegas Raiders
        'NE': 'NWE',           # New England Patriots
        'NO': 'NOR',           # New Orleans Saints
        'TB': 'TAM',           # Tampa Bay Buccaneers
        'TBB': 'TAM',          # Tampa Bay Buccaneers (alternate)
        
        # Standard codes that match (keep as-is)
        'ARI': 'ARI',          # Arizona Cardinals
        'ATL': 'ATL',          # Atlanta Falcons
        'BAL': 'BAL',          # Baltimore Ravens
        'BUF': 'BUF',          # Buffalo Bills
        'CAR': 'CAR',          # Carolina Panthers
        'CHI': 'CHI',          # Chicago Bears
        'CIN': 'CIN',          # Cincinnati Bengals
        'CLE': 'CLE',          # Cleveland Browns
        'DAL': 'DAL',          # Dallas Cowboys
        'DEN': 'DEN',          # Denver Broncos
        'DET': 'DET',          # Detroit Lions
        'HOU': 'HOU',          # Houston Texans
        'IND': 'IND',          # Indianapolis Colts
        'JAX': 'JAX',          # Jacksonville Jaguars (sometimes JAC)
        'JAC': 'JAX',          # Jacksonville Jaguars (alternate)
        'LAC': 'LAC',          # Los Angeles Chargers
        'LAR': 'LAR',          # Los Angeles Rams
        'MIA': 'MIA',          # Miami Dolphins
        'MIN': 'MIN',          # Minnesota Vikings
        'NYG': 'NYG',          # New York Giants
        'NYJ': 'NYJ',          # New York Jets
        'PHI': 'PHI',          # Philadelphia Eagles
        'PIT': 'PIT',          # Pittsburgh Steelers
        'SEA': 'SEA',          # Seattle Seahawks
        'TEN': 'TEN',          # Tennessee Titans
        'WAS': 'WAS',          # Washington Commanders
        
        # PFR standard codes (ensure they stay standard)
        'SFO': 'SFO',          # San Francisco 49ers
        'GNB': 'GNB',          # Green Bay Packers
        'KAN': 'KAN',          # Kansas City Chiefs  
        'LVR': 'LVR',          # Las Vegas Raiders
        'NWE': 'NWE',          # New England Patriots
        'NOR': 'NOR',          # New Orleans Saints
        'TAM': 'TAM',          # Tampa Bay Buccaneers
    }
    
    # Return mapped code or original if not found
    mapped_code = pfr_team_mapping.get(team_code, team_code)
    
    # Log if we're doing a mapping
    if mapped_code != team_code:
        logger.debug(f"Mapped team code: {team_code} -> {mapped_code}")
    
    return mapped_code

def validate_team_code(team_code: str) -> bool:
    """
    Validate if team code is a valid NFL team code
    
    Args:
        team_code: Team code to validate
        
    Returns:
        True if valid NFL team code
    """
    valid_pfr_codes = {
        'ARI', 'ATL', 'BAL', 'BUF', 'CAR', 'CHI', 'CIN', 'CLE',
        'DAL', 'DEN', 'DET', 'GNB', 'HOU', 'IND', 'JAX', 'KAN',
        'LAC', 'LAR', 'LVR', 'MIA', 'MIN', 'NWE', 'NOR', 'NYG',
        'NYJ', 'PHI', 'PIT', 'SEA', 'SFO', 'TAM', 'TEN', 'WAS'
    }
    
    # Also allow multi-team codes
    if re.match(r'\d+TM', team_code):
        return True
    
    return team_code in valid_pfr_codes

def validate_qb_stats(stats_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate QB statistics for data integrity
    
    Args:
        stats_dict: Dictionary of QB statistics
        
    Returns:
        Dictionary with validation results and cleaned stats
    """
    errors = []
    warnings = []
    
    # Extract stats with safe conversion
    completions = safe_int(stats_dict.get('cmp', 0))
    attempts = safe_int(stats_dict.get('att', 0))
    yards = safe_int(stats_dict.get('yds', 0))
    touchdowns = safe_int(stats_dict.get('td', 0))
    interceptions = safe_int(stats_dict.get('int', 0))
    rating = safe_float(stats_dict.get('rate', 0.0))
    
    # Logical consistency checks
    if completions > attempts and attempts > 0:
        errors.append(f"Completions ({completions}) cannot exceed attempts ({attempts})")
    
    if rating < 0 or rating > 158.3:
        warnings.append(f"Unusual passer rating: {rating} (valid range: 0-158.3)")
    
    if touchdowns < 0:
        errors.append(f"Touchdowns cannot be negative: {touchdowns}")
    
    if interceptions < 0:
        errors.append(f"Interceptions cannot be negative: {interceptions}")
    
    if yards < 0:
        errors.append(f"Passing yards cannot be negative: {yards}")
    
    # Range validation
    if attempts > 1000:
        warnings.append(f"Unusually high attempts: {attempts}")
    
    if yards > 6000:
        warnings.append(f"Unusually high passing yards: {yards}")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings,
        'cleaned_stats': {
            'cmp': completions,
            'att': attempts,
            'yds': yards,
            'td': touchdowns,
            'int': interceptions,
            'rate': rating
        }
    }

def generate_session_id() -> str:
    """Generate a unique session ID for tracking scraping sessions"""
    from uuid import uuid4
    return str(uuid4())

def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human readable string
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"

def calculate_processing_time(start_time: datetime, end_time: datetime) -> float:
    """Calculate processing time in seconds"""
    delta = end_time - start_time
    return delta.total_seconds() 

def parse_qb_splits_csv_by_position(csv_content: str) -> List[Dict[str, Any]]:
    """
    Parse QB splits CSV content by column position to handle duplicate column names.
    
    This function parses the CSV exactly as it appears in advanced_stats_1.csv,
    handling duplicate column names like 'Yds', 'TD', 'Att', 'Y/A', 'A/G', 'Y/G'
    by using their position in the CSV rather than their names.
    
    CSV Structure (34 columns):
    1: Split, 2: Value, 3: G, 4: W, 5: L, 6: T, 7: Cmp, 8: Att, 9: Inc, 10: Cmp%, 
    11: Yds, 12: TD, 13: Int, 14: Rate, 15: Sk, 16: Yds, 17: Y/A, 18: AY/A, 19: A/G, 20: Y/G, 
    21: Att, 22: Yds, 23: Y/A, 24: TD, 25: A/G, 26: Y/G, 27: TD, 28: Pts, 29: Fmb, 30: FL, 
    31: FF, 32: FR, 33: Yds, 34: TD
    
    Args:
        csv_content: Raw CSV content as string
        
    Returns:
        List of dictionaries containing parsed split data
    """
    try:
        # Read CSV with pandas, but don't use column names for parsing
        df = pd.read_csv(StringIO(csv_content), header=0)
        
        # Get the actual column names from the header
        column_names = df.columns.tolist()
        logger.info(f"CSV columns: {column_names}")
        
        # Verify we have the expected number of columns
        if len(column_names) != 34:
            logger.error(f"Expected 34 columns, got {len(column_names)}")
            return []
        
        parsed_splits = []
        
        for index, row in df.iterrows():
            try:
                # Parse by position (0-indexed, so subtract 1 from CSV column numbers)
                split_data = {
                    # Split identifiers
                    'split': str(row.iloc[0]) if pd.notna(row.iloc[0]) else None,  # Col 1
                    'value': str(row.iloc[1]) if pd.notna(row.iloc[1]) else None,  # Col 2
                    
                    # Game Stats (Cols 3-6)
                    'g': safe_int(row.iloc[2]),   # Games
                    'w': safe_int(row.iloc[3]),   # Wins
                    'l': safe_int(row.iloc[4]),   # Losses
                    't': safe_int(row.iloc[5]),   # Ties
                    
                    # Passing Stats (Cols 7-20)
                    'cmp': safe_int(row.iloc[6]),      # Completions
                    'att': safe_int(row.iloc[7]),      # Passing Attempts
                    'inc': safe_int(row.iloc[8]),      # Incompletions
                    'cmp_pct': safe_percentage(row.iloc[9]),  # Completion %
                    'yds': safe_int(row.iloc[10]),     # Passing Yards
                    'td': safe_int(row.iloc[11]),      # Passing TDs
                    'int': safe_int(row.iloc[12]),     # Interceptions
                    'rate': safe_float(row.iloc[13]),  # Passer Rating
                    'sk': safe_int(row.iloc[14]),      # Sacks
                    'sk_yds': safe_int(row.iloc[15]),  # Sack Yards
                    'y_a': safe_float(row.iloc[16]),   # Passing Y/A
                    'ay_a': safe_float(row.iloc[17]),  # AY/A
                    'a_g': safe_float(row.iloc[18]),   # Passing A/G
                    'y_g': safe_float(row.iloc[19]),   # Passing Y/G
                    
                    # Rushing Stats (Cols 21-26)
                    'rush_att': safe_int(row.iloc[20]),    # Rush Attempts
                    'rush_yds': safe_int(row.iloc[21]),    # Rush Yards
                    'rush_y_a': safe_float(row.iloc[22]),  # Rush Y/A
                    'rush_td': safe_int(row.iloc[23]),     # Rush TDs
                    'rush_a_g': safe_float(row.iloc[24]),  # Rush A/G
                    'rush_y_g': safe_float(row.iloc[25]),  # Rush Y/G
                    
                    # Total Stats (Cols 27-28)
                    'total_td': safe_int(row.iloc[26]),    # Total TDs
                    'pts': safe_int(row.iloc[27]),         # Points
                    
                    # Fumble Stats (Cols 29-34)
                    'fmb': safe_int(row.iloc[28]),         # Fumbles
                    'fl': safe_int(row.iloc[29]),          # Fumbles Lost
                    'ff': safe_int(row.iloc[30]),          # Fumbles Forced
                    'fr': safe_int(row.iloc[31]),          # Fumbles Recovered
                    'fr_yds': safe_int(row.iloc[32]),      # Fumble Recovery Yards
                    'fr_td': safe_int(row.iloc[33]),       # Fumble Recovery TDs
                }
                
                # Validate required fields
                if split_data['split'] is None or split_data['value'] is None:
                    logger.warning(f"Skipping row {index}: missing split or value")
                    continue
                
                parsed_splits.append(split_data)
                logger.debug(f"Parsed split: {split_data['split']}/{split_data['value']}")
                
            except Exception as e:
                logger.error(f"Error parsing row {index}: {e}")
                continue
        
        logger.info(f"Successfully parsed {len(parsed_splits)} splits from CSV")
        return parsed_splits
        
    except Exception as e:
        logger.error(f"Error parsing CSV content: {e}")
        return []

def validate_qb_splits_data(splits_data: List[Dict[str, Any]]) -> List[str]:
    """
    Validate QB splits data for consistency and completeness.
    
    Args:
        splits_data: List of parsed split dictionaries
        
    Returns:
        List of validation error messages
    """
    errors = []
    
    if not splits_data:
        errors.append("No splits data provided")
        return errors
    
    # Check for required split categories
    required_splits = {
        'Place', 'Result', 'Final Margin', 'Month', 'Game Number', 
        'Day', 'Time', 'Conference', 'Division', 'Opponent', 'Stadium', 'QB Start'
    }
    
    found_splits = set()
    for split in splits_data:
        if split.get('split'):
            found_splits.add(split['split'])
    
    missing_splits = required_splits - found_splits
    if missing_splits:
        errors.append(f"Missing required split categories: {missing_splits}")
    
    # Validate data consistency for each split type
    for split_type in found_splits:
        type_splits = [s for s in splits_data if s.get('split') == split_type]
        
        # Check that games sum correctly
        total_games = sum(s.get('g', 0) or 0 for s in type_splits)
        if total_games > 0:
            # Find the "League" or total row for this split type
            league_row = next((s for s in type_splits if s.get('value') in ['NFL', 'League']), None)
            if league_row and league_row.get('g'):
                league_games = league_row.get('g', 0)
                if total_games != league_games:
                    errors.append(f"Games don't sum correctly for {split_type}: expected {league_games}, got {total_games}")
    
    # Validate individual split values
    for split in splits_data:
        # Check for negative values where they shouldn't be
        if split.get('g', 0) < 0:
            errors.append(f"Negative games value: {split.get('g')} for {split.get('split')}/{split.get('value')}")
        
        if split.get('w', 0) < 0 or split.get('l', 0) < 0 or split.get('t', 0) < 0:
            errors.append(f"Negative W/L/T values for {split.get('split')}/{split.get('value')}")
        
        # Check that W + L + T = G
        g = split.get('g', 0) or 0
        w = split.get('w', 0) or 0
        l = split.get('l', 0) or 0
        t = split.get('t', 0) or 0
        
        if g > 0 and (w + l + t) != g:
            errors.append(f"W+L+T != G for {split.get('split')}/{split.get('value')}: {w}+{l}+{t} != {g}")
    
    return errors

def convert_splits_to_qb_splits_type1(splits_data: List[Dict[str, Any]], 
                                     pfr_id: str, 
                                     player_name: str, 
                                     season: int) -> List[Any]:
    """
    Convert splits data to QBSplitsType1 objects
    
    Args:
        splits_data: List of splits data dictionaries
        pfr_id: Player's PFR ID
        player_name: Player's name
        season: Season year
        
    Returns:
        List of QBSplitsType1 objects
    """
    from models.qb_models import QBSplitsType1
    
    qb_splits = []
    
    for split_data in splits_data:
        try:
            # Extract split type and value
            split = split_data.get('split', '')
            value = split_data.get('value', '')
            
            # Create QBSplitsType1 object
            qb_split = QBSplitsType1(
                pfr_id=pfr_id,
                player_name=player_name,
                season=season,
                split=split,
                value=value,
                g=safe_int(split_data.get('g')),
                w=safe_int(split_data.get('w')),
                l=safe_int(split_data.get('l')),
                t=safe_int(split_data.get('t')),
                cmp=safe_int(split_data.get('cmp')),
                att=safe_int(split_data.get('att')),
                inc=safe_int(split_data.get('inc')),
                cmp_pct=safe_percentage(split_data.get('cmp_pct')),
                yds=safe_int(split_data.get('yds')),
                td=safe_int(split_data.get('td')),
                int=safe_int(split_data.get('int')),
                rate=safe_float(split_data.get('rate')),
                sk=safe_int(split_data.get('sk')),
                sk_yds=safe_int(split_data.get('sk_yds')),
                y_a=safe_float(split_data.get('y_a')),
                ay_a=safe_float(split_data.get('ay_a')),
                a_g=safe_float(split_data.get('a_g')),
                y_g=safe_float(split_data.get('y_g')),
                rush_att=safe_int(split_data.get('rush_att')),
                rush_yds=safe_int(split_data.get('rush_yds')),
                rush_y_a=safe_float(split_data.get('rush_y_a')),
                rush_td=safe_int(split_data.get('rush_td')),
                rush_a_g=safe_float(split_data.get('rush_a_g')),
                rush_y_g=safe_float(split_data.get('rush_y_g')),
                total_td=safe_int(split_data.get('total_td')),
                pts=safe_int(split_data.get('pts')),
                fmb=safe_int(split_data.get('fmb')),
                fl=safe_int(split_data.get('fl')),
                ff=safe_int(split_data.get('ff')),
                fr=safe_int(split_data.get('fr')),
                fr_yds=safe_int(split_data.get('fr_yds')),
                fr_td=safe_int(split_data.get('fr_td')),
                scraped_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            qb_splits.append(qb_split)
            
        except Exception as e:
            logger.error(f"Error converting split data for {player_name}: {e}")
            continue
    
    return qb_splits 