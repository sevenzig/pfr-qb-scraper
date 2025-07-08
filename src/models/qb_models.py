#!/usr/bin/env python3
"""
Data models for NFL QB statistics and related data
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from utils.data_utils import generate_player_id, extract_pfr_id


@dataclass
class Player:
    """Data class for player information"""
    pfr_id: str  # PFR unique ID (e.g., 'burrjo01')
    player_name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    position: str = 'QB'
    height_inches: Optional[int] = None
    weight_lbs: Optional[int] = None
    birth_date: Optional[date] = None
    age: Optional[int] = None
    college: Optional[str] = None
    draft_year: Optional[int] = None
    draft_round: Optional[int] = None
    draft_pick: Optional[int] = None
    pfr_url: str = ''
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def validate(self) -> List[str]:
        """Validate player data"""
        errors = []
        
        if not self.pfr_id:
            errors.append("PFR ID is required")
        
        if not self.player_name:
            errors.append("Player name is required")
        
        if self.pfr_url and not extract_pfr_id(self.pfr_url):
            errors.append("Invalid PFR URL format")
        
        if self.height_inches is not None and (self.height_inches < 60 or self.height_inches > 84):
            errors.append("Height must be between 60 and 84 inches")
        
        if self.weight_lbs is not None and (self.weight_lbs < 150 or self.weight_lbs > 350):
            errors.append("Weight must be between 150 and 350 pounds")
        
        if self.age is not None and (self.age < 15 or self.age > 50):
            errors.append("Age must be between 15 and 50")
        
        if self.draft_year is not None and (self.draft_year < 1936 or self.draft_year > 2030):
            errors.append("Draft year must be between 1936 and 2030")
        
        if self.draft_round is not None and (self.draft_round < 1 or self.draft_round > 10):
            errors.append("Draft round must be between 1 and 10")
        
        if self.draft_pick is not None and (self.draft_pick < 1 or self.draft_pick > 300):
            errors.append("Draft pick must be between 1 and 300")
        
        return errors

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Player':
        """Create Player instance from dictionary"""
        return cls(
            pfr_id=data.get('pfr_id', ''),
            player_name=data.get('player_name', ''),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            position=data.get('position', 'QB'),
            height_inches=data.get('height_inches'),
            weight_lbs=data.get('weight_lbs'),
            birth_date=data.get('birth_date'),
            age=data.get('age'),
            college=data.get('college'),
            draft_year=data.get('draft_year'),
            draft_round=data.get('draft_round'),
            draft_pick=data.get('draft_pick'),
            pfr_url=data.get('pfr_url', ''),
            created_at=data.get('created_at', datetime.now()),
            updated_at=data.get('updated_at', datetime.now())
        )


@dataclass
class QBBasicStats:
    """Data class for basic QB statistics (season totals)
    
    Attributes:
        pfr_id: PFR unique player ID
        player_name: Full player name (e.g., 'Joe Burrow')
        player_url: URL to the player's PFR page
        season: Season year
        team: Team code
        ... (other fields unchanged)
    """
    pfr_id: str
    player_name: str
    player_url: str
    season: int
    team: str
    games_played: int = 0
    games_started: int = 0
    completions: int = 0
    attempts: int = 0
    completion_pct: Optional[float] = None
    pass_yards: int = 0
    pass_tds: int = 0
    interceptions: int = 0
    longest_pass: int = 0
    rating: Optional[float] = None
    sacks: int = 0
    sack_yards: int = 0
    net_yards_per_attempt: Optional[float] = None
    scraped_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def validate(self) -> List[str]:
        """Validate QB basic stats"""
        errors = []
        
        if not self.pfr_id:
            errors.append("PFR ID is required")
        
        if self.season < 1920 or self.season > 2030:
            errors.append("Season must be between 1920 and 2030")
        
        if not self.team:
            errors.append("Team is required")
        
        if self.games_played < 0:
            errors.append("Games played cannot be negative")
        
        if self.games_started < 0:
            errors.append("Games started cannot be negative")
        
        if self.games_started > self.games_played:
            errors.append("Games started cannot exceed games played")
        
        if self.completions < 0:
            errors.append("Completions cannot be negative")
        
        if self.attempts < 0:
            errors.append("Attempts cannot be negative")
        
        if self.completions > self.attempts:
            errors.append("Completions cannot exceed attempts")
        
        if self.completion_pct is not None and (self.completion_pct < 0 or self.completion_pct > 100):
            errors.append("Completion percentage must be between 0 and 100")
        
        if self.pass_yards < 0:
            errors.append("Pass yards cannot be negative")
        
        if self.pass_tds < 0:
            errors.append("Pass touchdowns cannot be negative")
        
        if self.interceptions < 0:
            errors.append("Interceptions cannot be negative")
        
        if self.longest_pass < 0:
            errors.append("Longest pass cannot be negative")
        
        if self.rating is not None and (self.rating < 0 or self.rating > 158.3):
            errors.append("Rating must be between 0 and 158.3")
        
        if self.sacks < 0:
            errors.append("Sacks cannot be negative")
        
        return errors

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QBBasicStats':
        """Create QBBasicStats instance from dictionary"""
        return cls(
            pfr_id=data.get('pfr_id', ''),
            player_name=data.get('player_name', ''),
            player_url=data.get('player_url', ''),
            season=data.get('season', 0),
            team=data.get('team', ''),
            games_played=data.get('games_played', 0),
            games_started=data.get('games_started', 0),
            completions=data.get('completions', 0),
            attempts=data.get('attempts', 0),
            completion_pct=data.get('completion_pct'),
            pass_yards=data.get('pass_yards', 0),
            pass_tds=data.get('pass_tds', 0),
            interceptions=data.get('interceptions', 0),
            longest_pass=data.get('longest_pass', 0),
            rating=data.get('rating'),
            sacks=data.get('sacks', 0),
            sack_yards=data.get('sack_yards', 0),
            net_yards_per_attempt=data.get('net_yards_per_attempt'),
            scraped_at=data.get('scraped_at', datetime.now()),
            updated_at=data.get('updated_at', datetime.now())
        )


@dataclass
class QBAdvancedStats:
    """Data class for advanced QB statistics"""
    pfr_id: str
    season: int
    qbr: Optional[float] = None
    adjusted_net_yards_per_attempt: Optional[float] = None
    fourth_quarter_comebacks: int = 0
    game_winning_drives: int = 0
    scraped_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def validate(self) -> List[str]:
        """Validate QB advanced stats"""
        errors = []
        
        if not self.pfr_id:
            errors.append("PFR ID is required")
        
        if self.season < 1920 or self.season > 2030:
            errors.append("Season must be between 1920 and 2030")
        
        if self.qbr is not None and (self.qbr < 0 or self.qbr > 100):
            errors.append("QBR must be between 0 and 100")
        
        if self.fourth_quarter_comebacks < 0:
            errors.append("Fourth quarter comebacks cannot be negative")
        
        if self.game_winning_drives < 0:
            errors.append("Game winning drives cannot be negative")
        
        return errors

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QBAdvancedStats':
        """Create QBAdvancedStats instance from dictionary"""
        return cls(
            pfr_id=data.get('pfr_id', ''),
            season=data.get('season', 0),
            qbr=data.get('qbr'),
            adjusted_net_yards_per_attempt=data.get('adjusted_net_yards_per_attempt'),
            fourth_quarter_comebacks=data.get('fourth_quarter_comebacks', 0),
            game_winning_drives=data.get('game_winning_drives', 0),
            scraped_at=data.get('scraped_at', datetime.now()),
            updated_at=data.get('updated_at', datetime.now())
        )


@dataclass
class QBSplitStats:
    """Data class for QB split statistics"""
    pfr_id: str
    season: int
    split_type: str
    split_category: str
    games: int = 0
    completions: int = 0
    attempts: int = 0
    completion_pct: Optional[float] = None
    pass_yards: int = 0
    pass_tds: int = 0
    interceptions: int = 0
    rating: Optional[float] = None
    sacks: int = 0
    sack_yards: int = 0
    net_yards_per_attempt: Optional[float] = None
    scraped_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # Additional fields for comprehensive QB splits data
    rush_attempts: int = 0
    rush_yards: int = 0
    rush_tds: int = 0
    fumbles: int = 0
    fumbles_lost: int = 0
    fumbles_forced: int = 0
    fumbles_recovered: int = 0
    fumble_recovery_yards: int = 0
    fumble_recovery_tds: int = 0
    incompletions: int = 0
    wins: int = 0
    losses: int = 0
    ties: int = 0
    attempts_per_game: Optional[float] = None
    yards_per_game: Optional[float] = None
    rush_attempts_per_game: Optional[float] = None
    rush_yards_per_game: Optional[float] = None
    total_tds: int = 0
    points: int = 0

    def validate(self) -> List[str]:
        """Validate QB split stats"""
        errors = []
        
        if not self.pfr_id:
            errors.append("PFR ID is required")
        
        if self.season < 1920 or self.season > 2030:
            errors.append("Season must be between 1920 and 2030")
        
        if not self.split_type:
            errors.append("Split type is required")
        
        if not self.split_category:
            errors.append("Split category is required")
        
        if self.games < 0:
            errors.append("Games cannot be negative")
        
        if self.completions < 0:
            errors.append("Completions cannot be negative")
        
        if self.attempts < 0:
            errors.append("Attempts cannot be negative")
        
        if self.completions > self.attempts:
            errors.append("Completions cannot exceed attempts")
        
        if self.completion_pct is not None and (self.completion_pct < 0 or self.completion_pct > 100):
            errors.append("Completion percentage must be between 0 and 100")
        
        if self.pass_yards < 0:
            errors.append("Pass yards cannot be negative")
        
        if self.pass_tds < 0:
            errors.append("Pass touchdowns cannot be negative")
        
        if self.interceptions < 0:
            errors.append("Interceptions cannot be negative")
        
        if self.rating is not None and (self.rating < 0 or self.rating > 158.3):
            errors.append("Rating must be between 0 and 158.3")
        
        if self.sacks < 0:
            errors.append("Sacks cannot be negative")
        
        # Additional field validation
        if self.rush_attempts < 0:
            errors.append("Rush attempts cannot be negative")
        
        if self.rush_yards < 0:
            errors.append("Rush yards cannot be negative")
        
        if self.rush_tds < 0:
            errors.append("Rush touchdowns cannot be negative")
        
        if self.fumbles < 0:
            errors.append("Fumbles cannot be negative")
        
        if self.fumbles_lost < 0:
            errors.append("Fumbles lost cannot be negative")
        
        if self.fumbles_forced < 0:
            errors.append("Fumbles forced cannot be negative")
        
        if self.fumbles_recovered < 0:
            errors.append("Fumbles recovered cannot be negative")
        
        if self.fumble_recovery_yards < 0:
            errors.append("Fumble recovery yards cannot be negative")
        
        if self.fumble_recovery_tds < 0:
            errors.append("Fumble recovery touchdowns cannot be negative")
        
        if self.incompletions < 0:
            errors.append("Incompletions cannot be negative")
        
        if self.wins < 0:
            errors.append("Wins cannot be negative")
        
        if self.losses < 0:
            errors.append("Losses cannot be negative")
        
        if self.ties < 0:
            errors.append("Ties cannot be negative")
        
        if self.total_tds < 0:
            errors.append("Total touchdowns cannot be negative")
        
        if self.points < 0:
            errors.append("Points cannot be negative")
        
        # Logical consistency checks
        if self.fumbles_lost > self.fumbles:
            errors.append("Fumbles lost cannot exceed total fumbles")
        
        if self.fumbles_recovered > self.fumbles:
            errors.append("Fumbles recovered cannot exceed total fumbles")
        
        expected_total_tds = self.pass_tds + self.rush_tds + self.fumble_recovery_tds
        if self.total_tds < expected_total_tds:
            errors.append(f"Total touchdowns ({self.total_tds}) should be at least {expected_total_tds}")
        
        return errors

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QBSplitStats':
        """Create QBSplitStats instance from dictionary"""
        return cls(
            pfr_id=data.get('pfr_id', ''),
            season=data.get('season', 0),
            split_type=data.get('split_type', ''),
            split_category=data.get('split_category', ''),
            games=data.get('games', 0),
            completions=data.get('completions', 0),
            attempts=data.get('attempts', 0),
            completion_pct=data.get('completion_pct'),
            pass_yards=data.get('pass_yards', 0),
            pass_tds=data.get('pass_tds', 0),
            interceptions=data.get('interceptions', 0),
            rating=data.get('rating'),
            sacks=data.get('sacks', 0),
            sack_yards=data.get('sack_yards', 0),
            net_yards_per_attempt=data.get('net_yards_per_attempt'),
            scraped_at=data.get('scraped_at', datetime.now()),
            updated_at=data.get('updated_at', datetime.now()),
            rush_attempts=data.get('rush_attempts', 0),
            rush_yards=data.get('rush_yards', 0),
            rush_tds=data.get('rush_tds', 0),
            fumbles=data.get('fumbles', 0),
            fumbles_lost=data.get('fumbles_lost', 0),
            fumbles_forced=data.get('fumbles_forced', 0),
            fumbles_recovered=data.get('fumbles_recovered', 0),
            fumble_recovery_yards=data.get('fumble_recovery_yards', 0),
            fumble_recovery_tds=data.get('fumble_recovery_tds', 0),
            incompletions=data.get('incompletions', 0),
            wins=data.get('wins', 0),
            losses=data.get('losses', 0),
            ties=data.get('ties', 0),
            attempts_per_game=data.get('attempts_per_game'),
            yards_per_game=data.get('yards_per_game'),
            rush_attempts_per_game=data.get('rush_attempts_per_game'),
            rush_yards_per_game=data.get('rush_yards_per_game'),
            total_tds=data.get('total_tds', 0),
            points=data.get('points', 0)
        )


@dataclass
class Team:
    """Data class for team information"""
    team_code: str
    team_name: str
    city: str
    conference: Optional[str] = None
    division: Optional[str] = None
    founded_year: Optional[int] = None
    stadium_name: Optional[str] = None
    stadium_capacity: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)

    def validate(self) -> List[str]:
        """Validate team data"""
        errors = []
        
        if not self.team_code:
            errors.append("Team code is required")
        
        if not self.team_name:
            errors.append("Team name is required")
        
        if not self.city:
            errors.append("City is required")
        
        if self.conference and self.conference not in ['AFC', 'NFC']:
            errors.append("Conference must be AFC or NFC")
        
        if self.division and self.division not in ['North', 'South', 'East', 'West']:
            errors.append("Division must be North, South, East, or West")
        
        if self.founded_year and (self.founded_year < 1920 or self.founded_year > 2030):
            errors.append("Founded year must be between 1920 and 2030")
        
        if self.stadium_capacity and self.stadium_capacity < 0:
            errors.append("Stadium capacity cannot be negative")
        
        return errors

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Team':
        """Create Team instance from dictionary"""
        return cls(
            team_code=data.get('team_code', ''),
            team_name=data.get('team_name', ''),
            city=data.get('city', ''),
            conference=data.get('conference'),
            division=data.get('division'),
            founded_year=data.get('founded_year'),
            stadium_name=data.get('stadium_name'),
            stadium_capacity=data.get('stadium_capacity'),
            created_at=data.get('created_at', datetime.now())
        )


@dataclass
class ScrapingLog:
    """Data class for scraping session logs"""
    session_id: str
    season: int
    start_time: datetime
    end_time: Optional[datetime] = None
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_players: int = 0
    total_basic_stats: int = 0
    total_advanced_stats: int = 0
    total_qb_splits: int = 0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    rate_limit_violations: int = 0
    processing_time_seconds: Optional[float] = None
    created_at: datetime = field(default_factory=datetime.now)

    def validate(self) -> List[str]:
        """Validate scraping log data"""
        errors = []
        
        if not self.session_id:
            errors.append("Session ID is required")
        
        if self.season < 1920 or self.season > 2030:
            errors.append("Season must be between 1920 and 2030")
        
        if self.total_requests < 0:
            errors.append("Total requests cannot be negative")
        
        if self.successful_requests < 0:
            errors.append("Successful requests cannot be negative")
        
        if self.failed_requests < 0:
            errors.append("Failed requests cannot be negative")
        
        if self.successful_requests + self.failed_requests != self.total_requests:
            errors.append("Total requests must equal successful + failed requests")
        
        if self.total_players < 0:
            errors.append("Total players cannot be negative")
        
        if self.total_basic_stats < 0:
            errors.append("Total basic stats cannot be negative")
        
        if self.total_advanced_stats < 0:
            errors.append("Total advanced stats cannot be negative")
        
        if self.total_qb_splits < 0:
            errors.append("Total QB splits cannot be negative")
        
        if self.rate_limit_violations < 0:
            errors.append("Rate limit violations cannot be negative")
        
        if self.processing_time_seconds is not None and self.processing_time_seconds < 0:
            errors.append("Processing time cannot be negative")
        
        return errors

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ScrapingLog':
        """Create ScrapingLog instance from dictionary"""
        return cls(
            session_id=data.get('session_id', ''),
            season=data.get('season', 0),
            start_time=data.get('start_time', datetime.now()),
            end_time=data.get('end_time'),
            total_requests=data.get('total_requests', 0),
            successful_requests=data.get('successful_requests', 0),
            failed_requests=data.get('failed_requests', 0),
            total_players=data.get('total_players', 0),
            total_basic_stats=data.get('total_basic_stats', 0),
            total_advanced_stats=data.get('total_advanced_stats', 0),
            total_qb_splits=data.get('total_qb_splits', 0),
            errors=data.get('errors', []),
            warnings=data.get('warnings', []),
            rate_limit_violations=data.get('rate_limit_violations', 0),
            processing_time_seconds=data.get('processing_time_seconds'),
            created_at=data.get('created_at', datetime.now())
        )


# Legacy compatibility - keep old method for backward compatibility
def generate_player_id(player_name: str, player_url: Optional[str] = None) -> str:
    """
    Generate consistent player ID from name or PFR URL
    
    Args:
        player_name: Player's full name
        player_url: Player's PFR URL (optional)
        
    Returns:
        Consistent player ID (PFR ID if available, otherwise generated from name)
    """
    from src.utils.data_utils import generate_player_id as utils_generate_player_id
    return utils_generate_player_id(player_name, player_url) 