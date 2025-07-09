#!/usr/bin/env python3
"""
Data utility functions for NFL QB scraping system
Handles data validation, conversion, and normalization
"""

import re
import logging
from typing import Union, Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

def safe_int(value: Union[str, int, float, None], default: int = 0) -> int:
    """
    Safely convert value to integer
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
        
    Returns:
        Integer value or default
    """
    if value is None or value == '':
        return default
    try:
        # Handle percentage strings
        if isinstance(value, str) and value.endswith('%'):
            return int(float(value[:-1]))
        return int(float(str(value)))
    except (ValueError, TypeError):
        return default

def safe_float(value: Union[str, int, float, None], default: float = 0.0) -> float:
    """
    Safely convert value to float
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
        
    Returns:
        Float value or default
    """
    if value is None or value == '':
        return default
    try:
        # Handle percentage strings
        if isinstance(value, str) and value.endswith('%'):
            return float(value[:-1])
        return float(str(value))
    except (ValueError, TypeError):
        return default

def safe_percentage(value: Union[str, int, float, None], default: float = 0.0) -> float:
    """
    Safely convert percentage value to float
    
    Args:
        value: Percentage value to convert (may include % symbol)
        default: Default value if conversion fails
        
    Returns:
        Float percentage value or default
    """
    if value is None or value == '':
        return default
    try:
        if isinstance(value, str):
            # Remove % symbol if present
            clean_value = value.replace('%', '').strip()
            return float(clean_value)
        return float(value)
    except (ValueError, TypeError):
        return default

def clean_player_name(name: str) -> str:
    """
    Clean and normalize player name
    
    Args:
        name: Raw player name
        
    Returns:
        Cleaned player name
    """
    if not name:
        return ""
    
    # Remove extra whitespace
    name = ' '.join(name.split())
    
    # Handle common name formatting issues
    name = name.replace('*', '').replace('+', '')  # Remove PFR indicators
    
    return name.strip()

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
    """
    Calculate processing time between two timestamps
    
    Args:
        start_time: Start timestamp
        end_time: End timestamp
        
    Returns:
        Processing time in seconds
    """
    if not start_time or not end_time:
        return 0.0
    
    delta = end_time - start_time
    return delta.total_seconds() 