#!/usr/bin/env python3
"""
Configuration management for NFL QB Data Scraping System
Centralized configuration for database, scraping, and application settings
"""

import os
from typing import Dict, List, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

@dataclass
class DatabaseConfig:
    """Database configuration settings"""
    connection_string: str
    max_connections: int = 10
    connection_timeout: int = 30
    statement_timeout: int = 300
    
    @classmethod
    def from_env(cls) -> 'DatabaseConfig':
        """Create database config from environment variables"""
        return cls(
            connection_string=os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/nfl_qb_data'),
            max_connections=int(os.getenv('DB_MAX_CONNECTIONS', '10')),
            connection_timeout=int(os.getenv('DB_CONNECTION_TIMEOUT', '30')),
            statement_timeout=int(os.getenv('DB_STATEMENT_TIMEOUT', '300'))
        )

@dataclass
class ScrapingConfig:
    """Scraping configuration settings"""
    rate_limit_delay: float = 3.0
    max_retries: int = 3
    timeout: int = 30
    user_agent: str = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    max_workers: int = 3
    jitter_range: float = 0.5
    
    @classmethod
    def from_env(cls) -> 'ScrapingConfig':
        """Create scraping config from environment variables"""
        return cls(
            rate_limit_delay=float(os.getenv('RATE_LIMIT_DELAY', '3.0')),
            max_retries=int(os.getenv('MAX_RETRIES', '3')),
            timeout=int(os.getenv('REQUEST_TIMEOUT', '30')),
            user_agent=os.getenv('USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'),
            max_workers=int(os.getenv('MAX_WORKERS', '3')),
            jitter_range=float(os.getenv('JITTER_RANGE', '0.5'))
        )

@dataclass
class LoggingConfig:
    """Logging configuration settings"""
    level: str = 'INFO'
    format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    file_path: str = 'logs/nfl_qb_scraper.log'
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    
    @classmethod
    def from_env(cls) -> 'LoggingConfig':
        """Create logging config from environment variables"""
        return cls(
            level=os.getenv('LOG_LEVEL', 'INFO'),
            format=os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
            file_path=os.getenv('LOG_FILE_PATH', 'logs/nfl_qb_scraper.log'),
            max_file_size=int(os.getenv('LOG_MAX_FILE_SIZE', str(10 * 1024 * 1024))),
            backup_count=int(os.getenv('LOG_BACKUP_COUNT', '5'))
        )

@dataclass
class AppConfig:
    """Application configuration settings"""
    target_season: int = 2024
    min_attempts_threshold: int = 100
    data_validation_enabled: bool = True
    auto_discovery_enabled: bool = True
    progress_reporting: bool = True
    
    @classmethod
    def from_env(cls) -> 'AppConfig':
        """Create app config from environment variables"""
        return cls(
            target_season=int(os.getenv('TARGET_SEASON', '2024')),
            min_attempts_threshold=int(os.getenv('MIN_ATTEMPTS_THRESHOLD', '100')),
            data_validation_enabled=os.getenv('DATA_VALIDATION_ENABLED', 'true').lower() == 'true',
            auto_discovery_enabled=os.getenv('AUTO_DISCOVERY_ENABLED', 'true').lower() == 'true',
            progress_reporting=os.getenv('PROGRESS_REPORTING', 'true').lower() == 'true'
        )

class SplitTypes:
    """Constants for split type categories"""
    
    # Basic splits
    HOME_AWAY = 'home_away'
    BY_QUARTER = 'by_quarter'
    BY_HALF = 'by_half'
    BY_MONTH = 'by_month'
    BY_DOWN = 'by_down'
    BY_DISTANCE = 'by_distance'
    WIN_LOSS = 'win_loss'
    
    # Advanced splits
    VS_DIVISION = 'vs_division'
    INDOOR_OUTDOOR = 'indoor_outdoor'
    SURFACE = 'surface'
    WEATHER = 'weather'
    TEMPERATURE = 'temperature'
    BY_SCORE = 'by_score'
    RED_ZONE = 'red_zone'
    TIME_OF_GAME = 'time_of_game'
    VS_WINNING_TEAMS = 'vs_winning_teams'
    DAY_OF_WEEK = 'day_of_week'
    GAME_TIME = 'game_time'
    PLAYOFF_TYPE = 'playoff_type'
    
    @classmethod
    def get_all_types(cls) -> List[str]:
        """Get all split type constants"""
        return [
            cls.HOME_AWAY, cls.BY_QUARTER, cls.BY_HALF, cls.BY_MONTH,
            cls.BY_DOWN, cls.BY_DISTANCE, cls.WIN_LOSS, cls.VS_DIVISION,
            cls.INDOOR_OUTDOOR, cls.SURFACE, cls.WEATHER, cls.TEMPERATURE,
            cls.BY_SCORE, cls.RED_ZONE, cls.TIME_OF_GAME, cls.VS_WINNING_TEAMS,
            cls.DAY_OF_WEEK, cls.GAME_TIME, cls.PLAYOFF_TYPE
        ]

class SplitCategories:
    """Constants for split categories"""
    
    # Home/Away categories
    HOME_AWAY_CATEGORIES = ['Home', 'Away']
    
    # Quarter categories
    QUARTER_CATEGORIES = ['1st Quarter', '2nd Quarter', '3rd Quarter', '4th Quarter', 'Overtime']
    
    # Half categories
    HALF_CATEGORIES = ['1st Half', '2nd Half']
    
    # Month categories
    MONTH_CATEGORIES = ['September', 'October', 'November', 'December', 'January']
    
    # Down categories
    DOWN_CATEGORIES = ['1st Down', '2nd Down', '3rd Down', '4th Down']
    
    # Distance categories
    DISTANCE_CATEGORIES = ['Short (1-3)', 'Medium (4-6)', 'Long (7-9)', 'Very Long (10+)']
    
    # Win/Loss categories
    WIN_LOSS_CATEGORIES = ['Wins', 'Losses']
    
    # Division categories
    DIVISION_CATEGORIES = ['vs Division', 'vs Conference', 'vs AFC', 'vs NFC']
    
    # Indoor/Outdoor categories
    INDOOR_OUTDOOR_CATEGORIES = ['Indoor', 'Outdoor']
    
    # Surface categories
    SURFACE_CATEGORIES = ['Grass', 'Turf']
    
    # Weather categories
    WEATHER_CATEGORIES = ['Dome', 'Clear', 'Rain', 'Snow', 'Wind']
    
    # Temperature categories
    TEMPERATURE_CATEGORIES = ['Cold (< 40°F)', 'Mild (40-60°F)', 'Warm (60-80°F)', 'Hot (> 80°F)']
    
    # Score categories
    SCORE_CATEGORIES = [
        'Ahead by 1-8', 'Ahead by 9-16', 'Ahead by 17+',
        'Behind by 1-8', 'Behind by 9-16', 'Behind by 17+', 'Tied'
    ]
    
    # Red zone categories
    RED_ZONE_CATEGORIES = ['Red Zone', 'Goal Line', 'Inside 20', 'Inside 10']
    
    # Time of game categories
    TIME_OF_GAME_CATEGORIES = [
        'First 15 min', 'Second 15 min', 'Third 15 min', 
        'Fourth 15 min', 'Final 2 min'
    ]
    
    # Winning teams categories
    WINNING_TEAMS_CATEGORIES = ['vs Teams > .500', 'vs Teams < .500', 'vs Teams = .500']
    
    # Day of week categories
    DAY_OF_WEEK_CATEGORIES = ['Sunday', 'Monday', 'Thursday', 'Saturday']
    
    # Game time categories
    GAME_TIME_CATEGORIES = ['1:00 PM', '4:00 PM', '8:00 PM', 'Other']
    
    # Playoff type categories
    PLAYOFF_TYPE_CATEGORIES = [
        'Regular Season', 'Wild Card', 'Divisional', 
        'Conference Championship', 'Super Bowl'
    ]
    
    @classmethod
    def get_categories_for_type(cls, split_type: str) -> List[str]:
        """Get categories for a specific split type"""
        category_map = {
            SplitTypes.HOME_AWAY: cls.HOME_AWAY_CATEGORIES,
            SplitTypes.BY_QUARTER: cls.QUARTER_CATEGORIES,
            SplitTypes.BY_HALF: cls.HALF_CATEGORIES,
            SplitTypes.BY_MONTH: cls.MONTH_CATEGORIES,
            SplitTypes.BY_DOWN: cls.DOWN_CATEGORIES,
            SplitTypes.BY_DISTANCE: cls.DISTANCE_CATEGORIES,
            SplitTypes.WIN_LOSS: cls.WIN_LOSS_CATEGORIES,
            SplitTypes.VS_DIVISION: cls.DIVISION_CATEGORIES,
            SplitTypes.INDOOR_OUTDOOR: cls.INDOOR_OUTDOOR_CATEGORIES,
            SplitTypes.SURFACE: cls.SURFACE_CATEGORIES,
            SplitTypes.WEATHER: cls.WEATHER_CATEGORIES,
            SplitTypes.TEMPERATURE: cls.TEMPERATURE_CATEGORIES,
            SplitTypes.BY_SCORE: cls.SCORE_CATEGORIES,
            SplitTypes.RED_ZONE: cls.RED_ZONE_CATEGORIES,
            SplitTypes.TIME_OF_GAME: cls.TIME_OF_GAME_CATEGORIES,
            SplitTypes.VS_WINNING_TEAMS: cls.WINNING_TEAMS_CATEGORIES,
            SplitTypes.DAY_OF_WEEK: cls.DAY_OF_WEEK_CATEGORIES,
            SplitTypes.GAME_TIME: cls.GAME_TIME_CATEGORIES,
            SplitTypes.PLAYOFF_TYPE: cls.PLAYOFF_TYPE_CATEGORIES,
        }
        return category_map.get(split_type, [])

class Config:
    """Main configuration class that combines all config sections"""
    
    def __init__(self):
        self.database = DatabaseConfig.from_env()
        self.scraping = ScrapingConfig.from_env()
        self.logging = LoggingConfig.from_env()
        self.app = AppConfig.from_env()
        self.split_types = SplitTypes()
        self.split_categories = SplitCategories()
    
    def validate(self) -> List[str]:
        """Validate configuration and return any errors"""
        errors = []
        
        # Validate database connection string
        if not self.database.connection_string:
            errors.append("DATABASE_URL is required")
        
        # Validate rate limiting
        if self.scraping.rate_limit_delay < 2.0:
            errors.append("Rate limit delay must be at least 2.0 seconds to respect PFR limits")
        
        # Validate season
        if self.app.target_season < 1920 or self.app.target_season > 2030:
            errors.append("Target season must be between 1920 and 2030")
        
        return errors
    
    def get_database_url(self) -> str:
        """Get database URL with fallback"""
        return self.database.connection_string
    
    def get_rate_limit_delay(self) -> float:
        """Get rate limit delay with jitter"""
        import random
        base_delay = self.scraping.rate_limit_delay
        jitter = random.uniform(-self.scraping.jitter_range, self.scraping.jitter_range)
        return max(2.0, base_delay + jitter)  # Minimum 2 seconds

# Global configuration instance
config = Config()

# Export commonly used settings
DATABASE_URL = config.get_database_url()
RATE_LIMIT_DELAY = config.scraping.rate_limit_delay
TARGET_SEASON = config.app.target_season
MAX_RETRIES = config.scraping.max_retries
USER_AGENT = config.scraping.user_agent 