#!/usr/bin/env python3
"""
Data models for NFL QB statistics - Raw Data Scraping
Matches exact column structures from Pro Football Reference CSV exports
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
class QBPassingStats:
    """
    Raw QB passing statistics from 2024_passing.csv
    Contains ALL columns from the CSV with no calculations
    """
    # Primary identifiers
    pfr_id: str
    player_name: str
    player_url: str
    season: int
    
    # Raw CSV columns (matching 2024_passing.csv exactly)
    rk: Optional[int] = None  # Rank
    age: Optional[int] = None  # Age
    team: Optional[str] = None  # Team
    pos: Optional[str] = None  # Position
    g: Optional[int] = None  # Games
    gs: Optional[int] = None  # Games Started  
    qb_rec: Optional[str] = None  # QB Record (W-L-T format)
    cmp: Optional[int] = None  # Completions
    att: Optional[int] = None  # Attempts
    cmp_pct: Optional[float] = None  # Completion %
    yds: Optional[int] = None  # Yards
    td: Optional[int] = None  # Touchdowns
    td_pct: Optional[float] = None  # TD %
    int: Optional[int] = None  # Interceptions
    int_pct: Optional[float] = None  # Int %
    first_downs: Optional[int] = None  # 1D (First Downs)
    succ_pct: Optional[float] = None  # Success %
    lng: Optional[int] = None  # Longest pass
    y_a: Optional[float] = None  # Y/A (Yards per Attempt)
    ay_a: Optional[float] = None  # AY/A (Adjusted Yards per Attempt)
    y_c: Optional[float] = None  # Y/C (Yards per Completion)
    y_g: Optional[float] = None  # Y/G (Yards per Game)
    rate: Optional[float] = None  # Passer Rating
    qbr: Optional[float] = None  # QBR
    sk: Optional[int] = None  # Sacks
    sk_yds: Optional[int] = None  # Sack Yards
    sk_pct: Optional[float] = None  # Sack %
    ny_a: Optional[float] = None  # NY/A (Net Yards per Attempt)
    any_a: Optional[float] = None  # ANY/A (Adjusted Net Yards per Attempt)
    four_qc: Optional[int] = None  # 4QC (4th Quarter Comebacks)
    gwd: Optional[int] = None  # GWD (Game Winning Drives)
    awards: Optional[str] = None  # Awards
    player_additional: Optional[str] = None  # Player-additional
    
    # Metadata
    scraped_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def validate(self) -> List[str]:
        """Validate QB passing stats - minimal validation for raw data"""
        errors = []
        
        if not self.pfr_id:
            errors.append("PFR ID is required")
        
        if not self.player_name:
            errors.append("Player name is required")
        
        if self.season < 1920 or self.season > 2030:
            errors.append("Season must be between 1920 and 2030")
        
        return errors

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QBPassingStats':
        """Create QBPassingStats instance from dictionary"""
        return cls(
            pfr_id=data.get('pfr_id', ''),
            player_name=data.get('player_name', ''),
            player_url=data.get('player_url', ''),
            season=data.get('season', 0),
            rk=data.get('rk'),
            age=data.get('age'),
            team=data.get('team'),
            pos=data.get('pos'),
            g=data.get('g'),
            gs=data.get('gs'),
            qb_rec=data.get('qb_rec'),
            cmp=data.get('cmp'),
            att=data.get('att'),
            cmp_pct=data.get('cmp_pct'),
            yds=data.get('yds'),
            td=data.get('td'),
            td_pct=data.get('td_pct'),
            int=data.get('int'),
            int_pct=data.get('int_pct'),
            first_downs=data.get('first_downs'),
            succ_pct=data.get('succ_pct'),
            lng=data.get('lng'),
            y_a=data.get('y_a'),
            ay_a=data.get('ay_a'),
            y_c=data.get('y_c'),
            y_g=data.get('y_g'),
            rate=data.get('rate'),
            qbr=data.get('qbr'),
            sk=data.get('sk'),
            sk_yds=data.get('sk_yds'),
            sk_pct=data.get('sk_pct'),
            ny_a=data.get('ny_a'),
            any_a=data.get('any_a'),
            four_qc=data.get('four_qc'),
            gwd=data.get('gwd'),
            awards=data.get('awards'),
            player_additional=data.get('player_additional'),
            scraped_at=data.get('scraped_at', datetime.now()),
            updated_at=data.get('updated_at', datetime.now())
        )


@dataclass
class QBSplitsType1:
    """
    Raw QB splits data from advanced_stats_1.csv
    Contains ALL columns from the CSV with no calculations
    """
    # Primary identifiers
    pfr_id: str
    player_name: str
    season: int
    
    # Split identifiers
    split: Optional[str] = None  # Split type (e.g., "League", "Place", "Result")
    value: Optional[str] = None  # Split value (e.g., "NFL", "Home", "Win")
    
    # Raw CSV columns (matching advanced_stats_1.csv exactly)
    g: Optional[int] = None  # Games
    w: Optional[int] = None  # Wins
    l: Optional[int] = None  # Losses
    t: Optional[int] = None  # Ties
    cmp: Optional[int] = None  # Completions
    att: Optional[int] = None  # Attempts
    inc: Optional[int] = None  # Incompletions
    cmp_pct: Optional[float] = None  # Completion %
    yds: Optional[int] = None  # Passing Yards
    td: Optional[int] = None  # Passing TDs
    int: Optional[int] = None  # Interceptions
    rate: Optional[float] = None  # Passer Rating
    sk: Optional[int] = None  # Sacks
    sk_yds: Optional[int] = None  # Sack Yards
    y_a: Optional[float] = None  # Y/A (Yards per Attempt)
    ay_a: Optional[float] = None  # AY/A (Adjusted Yards per Attempt)
    a_g: Optional[float] = None  # A/G (Attempts per Game)
    y_g: Optional[float] = None  # Y/G (Yards per Game)
    rush_att: Optional[int] = None  # Rush Attempts
    rush_yds: Optional[int] = None  # Rush Yards
    rush_y_a: Optional[float] = None  # Rush Y/A
    rush_td: Optional[int] = None  # Rush TDs
    rush_a_g: Optional[float] = None  # Rush A/G (Rush Attempts per Game)
    rush_y_g: Optional[float] = None  # Rush Y/G (Rush Yards per Game)
    total_td: Optional[int] = None  # Total TDs
    pts: Optional[int] = None  # Points
    fmb: Optional[int] = None  # Fumbles
    fl: Optional[int] = None  # Fumbles Lost
    ff: Optional[int] = None  # Fumbles Forced
    fr: Optional[int] = None  # Fumbles Recovered
    fr_yds: Optional[int] = None  # Fumble Recovery Yards
    fr_td: Optional[int] = None  # Fumble Recovery TDs
    
    # Metadata
    scraped_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def validate(self) -> List[str]:
        """Validate QB splits type 1 - minimal validation for raw data"""
        errors = []
        
        if not self.pfr_id:
            errors.append("PFR ID is required")
        
        if self.season < 1920 or self.season > 2030:
            errors.append("Season must be between 1920 and 2030")
        
        return errors

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QBSplitsType1':
        """Create QBSplitsType1 instance from dictionary"""
        return cls(
            pfr_id=data.get('pfr_id', ''),
            player_name=data.get('player_name', ''),
            season=data.get('season', 0),
            split=data.get('split'),
            value=data.get('value'),
            g=data.get('g'),
            w=data.get('w'),
            l=data.get('l'),
            t=data.get('t'),
            cmp=data.get('cmp'),
            att=data.get('att'),
            inc=data.get('inc'),
            cmp_pct=data.get('cmp_pct'),
            yds=data.get('yds'),
            td=data.get('td'),
            int=data.get('int'),
            rate=data.get('rate'),
            sk=data.get('sk'),
            sk_yds=data.get('sk_yds'),
            y_a=data.get('y_a'),
            ay_a=data.get('ay_a'),
            a_g=data.get('a_g'),
            y_g=data.get('y_g'),
            rush_att=data.get('rush_att'),
            rush_yds=data.get('rush_yds'),
            rush_y_a=data.get('rush_y_a'),
            rush_td=data.get('rush_td'),
            rush_a_g=data.get('rush_a_g'),
            rush_y_g=data.get('rush_y_g'),
            total_td=data.get('total_td'),
            pts=data.get('pts'),
            fmb=data.get('fmb'),
            fl=data.get('fl'),
            ff=data.get('ff'),
            fr=data.get('fr'),
            fr_yds=data.get('fr_yds'),
            fr_td=data.get('fr_td'),
            scraped_at=data.get('scraped_at', datetime.now()),
            updated_at=data.get('updated_at', datetime.now())
        )


@dataclass
class QBSplitsType2:
    """
    Raw QB splits data from advanced_stats.2.csv
    Contains ALL columns from the CSV with no calculations
    """
    # Primary identifiers
    pfr_id: str
    player_name: str
    season: int
    
    # Split identifiers
    split: Optional[str] = None  # Split type (e.g., "Down", "Yards To Go")
    value: Optional[str] = None  # Split value (e.g., "1st", "1-3")
    
    # Raw CSV columns (matching advanced_stats.2.csv exactly)
    cmp: Optional[int] = None  # Completions
    att: Optional[int] = None  # Attempts
    inc: Optional[int] = None  # Incompletions
    cmp_pct: Optional[float] = None  # Completion %
    yds: Optional[int] = None  # Passing Yards
    td: Optional[int] = None  # Passing TDs
    first_downs: Optional[int] = None  # 1D (First Downs)
    int: Optional[int] = None  # Interceptions
    rate: Optional[float] = None  # Passer Rating
    sk: Optional[int] = None  # Sacks
    sk_yds: Optional[int] = None  # Sack Yards
    y_a: Optional[float] = None  # Y/A (Yards per Attempt)
    ay_a: Optional[float] = None  # AY/A (Adjusted Yards per Attempt)
    rush_att: Optional[int] = None  # Rush Attempts
    rush_yds: Optional[int] = None  # Rush Yards
    rush_y_a: Optional[float] = None  # Rush Y/A
    rush_td: Optional[int] = None  # Rush TDs
    rush_first_downs: Optional[int] = None  # Rush First Downs
    
    # Metadata
    scraped_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def validate(self) -> List[str]:
        """Validate QB splits type 2 - minimal validation for raw data"""
        errors = []
        
        if not self.pfr_id:
            errors.append("PFR ID is required")
        
        if self.season < 1920 or self.season > 2030:
            errors.append("Season must be between 1920 and 2030")
        
        return errors

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QBSplitsType2':
        """Create QBSplitsType2 instance from dictionary"""
        return cls(
            pfr_id=data.get('pfr_id', ''),
            player_name=data.get('player_name', ''),
            season=data.get('season', 0),
            split=data.get('split'),
            value=data.get('value'),
            cmp=data.get('cmp'),
            att=data.get('att'),
            inc=data.get('inc'),
            cmp_pct=data.get('cmp_pct'),
            yds=data.get('yds'),
            td=data.get('td'),
            first_downs=data.get('first_downs'),
            int=data.get('int'),
            rate=data.get('rate'),
            sk=data.get('sk'),
            sk_yds=data.get('sk_yds'),
            y_a=data.get('y_a'),
            ay_a=data.get('ay_a'),
            rush_att=data.get('rush_att'),
            rush_yds=data.get('rush_yds'),
            rush_y_a=data.get('rush_y_a'),
            rush_td=data.get('rush_td'),
            rush_first_downs=data.get('rush_first_downs'),
            scraped_at=data.get('scraped_at', datetime.now()),
            updated_at=data.get('updated_at', datetime.now())
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
    total_passing_stats: int = 0
    total_splits: int = 0
    total_splits_advanced: int = 0
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
        
        if self.total_passing_stats < 0:
            errors.append("Total passing stats cannot be negative")
        
        if self.total_splits < 0:
            errors.append("Total splits cannot be negative")
        
        if self.total_splits_advanced < 0:
            errors.append("Total splits advanced cannot be negative")
        
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
            total_passing_stats=data.get('total_passing_stats', 0),
            total_splits=data.get('total_splits', 0),
            total_splits_advanced=data.get('total_splits_advanced', 0),
            errors=data.get('errors', []),
            warnings=data.get('warnings', []),
            rate_limit_violations=data.get('rate_limit_violations', 0),
            processing_time_seconds=data.get('processing_time_seconds'),
            created_at=data.get('created_at', datetime.now())
        )


def generate_player_id(player_name: str, player_url: Optional[str] = None) -> str:
    """Generate a player ID from name and URL"""
    if player_url:
        return extract_pfr_id(player_url) or generate_player_id(player_name)
    
    # Generate ID from name if URL not available
    parts = player_name.lower().split()
    if len(parts) >= 2:
        return f"{parts[-1][:4]}{parts[0][:2]}01"
    return f"{parts[0][:6]}01"


# Legacy aliases for backward compatibility
QBBasicStats = QBPassingStats
# QBSplitStats is the model for the qb_splits table (basic splits)
QBSplitStats = QBSplitsType1
# QBAdvancedStats is the model for the qb_splits_advanced table (advanced splits)
QBAdvancedStats = QBSplitsType2 