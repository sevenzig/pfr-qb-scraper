#!/usr/bin/env python3
"""
Utility functions for NFL QB Data Scraping System
Helper functions for data manipulation, validation, cleaning, and type conversion
"""

import re
import math
from typing import Optional, Union, Any, List, Dict
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)

def safe_int(value: Any, default: int = 0) -> int:
    """
    Safely convert value to integer with error handling
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
        
    Returns:
        Integer value or default
    """
    if value is None:
        return default
    
    if isinstance(value, int):
        return value
    
    if isinstance(value, float):
        return int(value)
    
    if isinstance(value, str):
        # Remove commas and other non-numeric characters
        cleaned = re.sub(r'[^\d.-]', '', value.strip())
        if cleaned:
            try:
                return int(float(cleaned))
            except (ValueError, TypeError):
                logger.warning(f"Could not convert '{value}' to int, using default {default}")
                return default
    
    logger.warning(f"Could not convert {type(value).__name__} '{value}' to int, using default {default}")
    return default

def safe_float(value: Any, default: float = 0.0) -> float:
    """
    Safely convert value to float with error handling
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
        
    Returns:
        Float value or default
    """
    if value is None:
        return default
    
    if isinstance(value, (int, float)):
        return float(value)
    
    if isinstance(value, str):
        # Remove commas and percentage signs
        cleaned = re.sub(r'[^\d.-]', '', value.strip())
        if cleaned:
            try:
                return float(cleaned)
            except (ValueError, TypeError):
                logger.warning(f"Could not convert '{value}' to float, using default {default}")
                return default
    
    logger.warning(f"Could not convert {type(value).__name__} '{value}' to float, using default {default}")
    return default

def safe_percentage(value: Any, default: float = 0.0) -> float:
    """
    Safely convert percentage value to float (0-100 scale)
    
    Args:
        value: Percentage value (string with % or float)
        default: Default value if conversion fails
        
    Returns:
        Float percentage (0-100 scale)
    """
    if value is None:
        return default
    
    if isinstance(value, (int, float)):
        return float(value)
    
    if isinstance(value, str):
        # Remove % sign and convert
        cleaned = value.strip().replace('%', '')
        try:
            return float(cleaned)
        except (ValueError, TypeError):
            logger.warning(f"Could not convert percentage '{value}' to float, using default {default}")
            return default
    
    logger.warning(f"Could not convert {type(value).__name__} '{value}' to percentage, using default {default}")
    return default

def clean_player_name(name: str) -> str:
    """
    Clean and standardize player name
    
    Args:
        name: Raw player name
        
    Returns:
        Cleaned player name
    """
    if not name:
        return ""
    
    # Remove extra whitespace and special characters
    cleaned = re.sub(r'\s+', ' ', name.strip())
    # Remove asterisks and other special markers
    cleaned = re.sub(r'[*†‡]', '', cleaned)
    
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
    import re
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

def calculate_passer_rating(
    completions: int,
    attempts: int,
    yards: int,
    touchdowns: int,
    interceptions: int
) -> float:
    """
    Calculate NFL passer rating manually
    
    Args:
        completions: Number of completions
        attempts: Number of attempts
        yards: Passing yards
        touchdowns: Passing touchdowns
        interceptions: Interceptions thrown
        
    Returns:
        NFL passer rating (0-158.3 scale)
    """
    if attempts == 0:
        return 0.0
    
    # NFL passer rating formula
    a = max(0, min(2.375, (completions / attempts - 0.3) * 5))
    b = max(0, min(2.375, (yards / attempts - 3) * 0.25))
    c = max(0, min(2.375, (touchdowns / attempts) * 20))
    d = max(0, min(2.375, 2.375 - (interceptions / attempts) * 25))
    
    return round(((a + b + c + d) / 6) * 100, 1)

def calculate_completion_percentage(completions: int, attempts: int) -> Optional[float]:
    """
    Calculate completion percentage
    
    Args:
        completions: Number of completions
        attempts: Number of attempts
        
    Returns:
        Completion percentage or None if no attempts
    """
    if attempts == 0:
        return None
    
    return round((completions / attempts) * 100, 1)

def calculate_yards_per_attempt(yards: int, attempts: int) -> Optional[float]:
    """
    Calculate yards per attempt
    
    Args:
        yards: Passing yards
        attempts: Number of attempts
        
    Returns:
        Yards per attempt or None if no attempts
    """
    if attempts == 0:
        return None
    
    return round(yards / attempts, 2)

def calculate_touchdown_rate(touchdowns: int, attempts: int) -> Optional[float]:
    """
    Calculate touchdown rate (touchdowns per attempt as percentage)
    
    Args:
        touchdowns: Number of touchdowns
        attempts: Number of attempts
        
    Returns:
        Touchdown rate percentage or None if no attempts
    """
    if attempts == 0:
        return None
    
    return round((touchdowns / attempts) * 100, 2)

def calculate_interception_rate(interceptions: int, attempts: int) -> Optional[float]:
    """
    Calculate interception rate (interceptions per attempt as percentage)
    
    Args:
        interceptions: Number of interceptions
        attempts: Number of attempts
        
    Returns:
        Interception rate percentage or None if no attempts
    """
    if attempts == 0:
        return None
    
    return round((interceptions / attempts) * 100, 2)

def calculate_qb_efficiency_score(
    completion_pct: float,
    yards_per_attempt: float,
    td_rate: float,
    int_rate: float,
    rating: float
) -> float:
    """
    Calculate custom QB efficiency score
    
    Args:
        completion_pct: Completion percentage
        yards_per_attempt: Yards per attempt
        td_rate: Touchdown rate percentage
        int_rate: Interception rate percentage
        rating: NFL passer rating
        
    Returns:
        Efficiency score (0-100 scale)
    """
    # Weighted efficiency score
    completion_weight = 0.2
    yards_weight = 0.25
    td_weight = 0.25
    int_weight = 0.15
    rating_weight = 0.15
    
    completion_score = completion_pct * completion_weight
    yards_score = yards_per_attempt * 10 * yards_weight
    td_score = td_rate * td_weight
    int_score = max(0, (10 - int_rate)) * 5 * int_weight
    rating_score = (rating / 158.3) * 100 * rating_weight
    
    return round(completion_score + yards_score + td_score + int_score + rating_score, 2)

def validate_statistical_consistency(
    completions: int,
    attempts: int,
    completion_pct: Optional[float],
    yards: int,
    touchdowns: int,
    interceptions: int,
    rating: Optional[float]
) -> List[str]:
    """
    Validate statistical consistency between related fields
    
    Args:
        completions: Number of completions
        attempts: Number of attempts
        completion_pct: Completion percentage
        yards: Passing yards
        touchdowns: Passing touchdowns
        interceptions: Interceptions
        rating: NFL passer rating
        
    Returns:
        List of validation errors
    """
    errors = []
    
    # Check completion percentage
    if attempts > 0 and completion_pct is not None:
        calculated_pct = (completions / attempts) * 100
        if abs(completion_pct - calculated_pct) > 0.1:
            errors.append(f"Completion percentage mismatch: {completion_pct} vs calculated {calculated_pct:.1f}")
    
    # Check passer rating
    if attempts > 0 and rating is not None:
        calculated_rating = calculate_passer_rating(completions, attempts, yards, touchdowns, interceptions)
        if abs(rating - calculated_rating) > 0.1:
            errors.append(f"Passer rating mismatch: {rating} vs calculated {calculated_rating}")
    
    # Check logical consistency
    if completions > attempts:
        errors.append("Completions cannot exceed attempts")
    
    if yards < 0:
        errors.append("Passing yards cannot be negative")
    
    if touchdowns < 0:
        errors.append("Touchdowns cannot be negative")
    
    if interceptions < 0:
        errors.append("Interceptions cannot be negative")
    
    return errors

def format_percentage(value: Union[float, str, None], decimals: int = 1) -> str:
    """
    Format value as percentage string
    
    Args:
        value: Value to format
        decimals: Number of decimal places
        
    Returns:
        Formatted percentage string
    """
    if value is None:
        return "0.0%"
    
    try:
        num = float(value)
        return f"{num:.{decimals}f}%"
    except (ValueError, TypeError):
        return "0.0%"

def format_decimal(value: Union[float, str, None], decimals: int = 1) -> str:
    """
    Format value as decimal string
    
    Args:
        value: Value to format
        decimals: Number of decimal places
        
    Returns:
        Formatted decimal string
    """
    if value is None:
        return "0.0"
    
    try:
        num = float(value)
        return f"{num:.{decimals}f}"
    except (ValueError, TypeError):
        return "0.0"

def format_integer(value: Union[int, str, None]) -> str:
    """
    Format value as integer string
    
    Args:
        value: Value to format
        
    Returns:
        Formatted integer string
    """
    if value is None:
        return "0"
    
    try:
        num = int(float(value))
        return str(num)
    except (ValueError, TypeError):
        return "0"

def clean_team_code(team_code: str) -> str:
    """
    Clean and validate team code
    
    Args:
        team_code: Raw team code
        
    Returns:
        Cleaned team code (3 characters)
    """
    if not team_code:
        return ""
    
    # Remove extra whitespace and convert to uppercase
    cleaned = team_code.strip().upper()
    
    # Ensure it's exactly 3 characters
    if len(cleaned) > 3:
        cleaned = cleaned[:3]
    elif len(cleaned) < 3:
        cleaned = cleaned.ljust(3)
    
    return cleaned

def parse_height(height_str: str) -> Optional[int]:
    """
    Parse height string to inches
    
    Args:
        height_str: Height string (e.g., "6'2"", "74")
        
    Returns:
        Height in inches or None if parsing fails
    """
    if not height_str:
        return None
    
    # Handle format like "6'2""
    match = re.match(r"(\d+)'(\d+)\"", height_str)
    if match:
        feet = int(match.group(1))
        inches = int(match.group(2))
        return feet * 12 + inches
    
    # Handle format like "74" (inches)
    try:
        inches = int(height_str)
        if 60 <= inches <= 84:  # Reasonable height range
            return inches
    except (ValueError, TypeError):
        pass
    
    return None

def parse_weight(weight_str: str) -> Optional[int]:
    """
    Parse weight string to pounds
    
    Args:
        weight_str: Weight string (e.g., "220 lbs", "220")
        
    Returns:
        Weight in pounds or None if parsing fails
    """
    if not weight_str:
        return None
    
    # Extract numeric value
    match = re.search(r'(\d+)', weight_str)
    if match:
        weight = int(match.group(1))
        if 150 <= weight <= 350:  # Reasonable weight range
            return weight
    
    return None

def parse_date(date_str: str) -> Optional[date]:
    """
    Parse date string to date object
    
    Args:
        date_str: Date string in various formats
        
    Returns:
        Date object or None if parsing fails
    """
    if not date_str:
        return None
    
    # Common date formats
    formats = [
        '%Y-%m-%d',
        '%m/%d/%Y',
        '%m-%d-%Y',
        '%B %d, %Y',
        '%b %d, %Y'
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    
    return None

def extract_numeric_value(text: str) -> Optional[float]:
    """
    Extract numeric value from text containing numbers
    
    Args:
        text: Text that may contain numbers
        
    Returns:
        Numeric value or None if not found
    """
    if not text:
        return None
    
    # Find first number in text
    match = re.search(r'[-+]?\d*\.?\d+', text)
    if match:
        try:
            return float(match.group())
        except (ValueError, TypeError):
            pass
    
    return None

def is_valid_season(season: int) -> bool:
    """
    Check if season is within valid range
    
    Args:
        season: Season year
        
    Returns:
        True if valid season
    """
    return 1920 <= season <= 2030

def is_valid_rating(rating: float) -> bool:
    """
    Check if passer rating is within valid range
    
    Args:
        rating: NFL passer rating
        
    Returns:
        True if valid rating
    """
    return 0.0 <= rating <= 158.3

def is_valid_qbr(qbr: float) -> bool:
    """
    Check if QBR is within valid range
    
    Args:
        qbr: ESPN Total QBR
        
    Returns:
        True if valid QBR
    """
    return 0.0 <= qbr <= 100.0

def is_valid_completion_percentage(pct: float) -> bool:
    """
    Check if completion percentage is within valid range
    
    Args:
        pct: Completion percentage
        
    Returns:
        True if valid percentage
    """
    return 0.0 <= pct <= 100.0

def normalize_split_type(split_type: str) -> str:
    """
    Normalize split type string to standard format
    
    Args:
        split_type: Raw split type string
        
    Returns:
        Normalized split type
    """
    if not split_type:
        return ""
    
    # Convert to lowercase and replace spaces with underscores
    normalized = split_type.lower().replace(' ', '_')
    
    # Common mappings
    mappings = {
        'home_away': 'home_away',
        'by_quarter': 'by_quarter',
        'by_half': 'by_half',
        'by_month': 'by_month',
        'by_down': 'by_down',
        'by_distance': 'by_distance',
        'win_loss': 'win_loss',
        'vs_division': 'vs_division',
        'indoor_outdoor': 'indoor_outdoor',
        'surface': 'surface',
        'weather': 'weather',
        'temperature': 'temperature',
        'by_score': 'by_score',
        'red_zone': 'red_zone',
        'time_of_game': 'time_of_game',
        'vs_winning_teams': 'vs_winning_teams',
        'day_of_week': 'day_of_week',
        'game_time': 'game_time',
        'playoff_type': 'playoff_type'
    }
    
    return mappings.get(normalized, normalized)

def generate_session_id() -> str:
    """
    Generate unique session ID for scraping logs
    
    Returns:
        Unique session ID
    """
    import uuid
    return str(uuid.uuid4())

def calculate_processing_time(start_time: datetime, end_time: datetime) -> float:
    """
    Calculate processing time in seconds
    
    Args:
        start_time: Start datetime
        end_time: End datetime
        
    Returns:
        Processing time in seconds
    """
    return (end_time - start_time).total_seconds()

def format_duration(seconds: float) -> str:
    """
    Format duration in human-readable format
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} minutes"
    else:
        hours = seconds / 3600
        return f"{hours:.1f} hours"

def log_data_quality_metrics(
    total_records: int,
    valid_records: int,
    invalid_records: int,
    errors_by_type: Dict[str, int]
) -> None:
    """
    Log data quality metrics
    
    Args:
        total_records: Total number of records processed
        valid_records: Number of valid records
        invalid_records: Number of invalid records
        errors_by_type: Dictionary of error counts by type
    """
    logger.info(f"Data Quality Report:")
    logger.info(f"  Total Records: {total_records}")
    logger.info(f"  Valid Records: {valid_records}")
    logger.info(f"  Invalid Records: {invalid_records}")
    logger.info(f"  Success Rate: {(valid_records/total_records*100):.1f}%" if total_records > 0 else "  Success Rate: 0%")
    
    if errors_by_type:
        logger.info("  Errors by Type:")
        for error_type, count in errors_by_type.items():
            logger.info(f"    {error_type}: {count}") 