#!/usr/bin/env python3
"""
Configuration management for NFL QB Data Scraping System
Centralized configuration for database, scraping, and application settings
"""

import os
from typing import Dict, List, Optional
from dataclasses import dataclass, field
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
class BulkOperationConfig:
    """Bulk database operation configuration settings"""
    batch_size: int = 100
    max_batch_size: int = 1000
    min_batch_size: int = 10
    timeout_seconds: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0
    conflict_strategy: str = "UPDATE"  # UPDATE, IGNORE, FAIL
    enable_progress_tracking: bool = True
    enable_detailed_logging: bool = True
    memory_limit_mb: int = 512
    enable_streaming: bool = True
    checkpoint_interval: int = 50  # Commit every N batches
    
    @classmethod
    def from_env(cls) -> 'BulkOperationConfig':
        """Create bulk operation config from environment variables"""
        return cls(
            batch_size=int(os.getenv('BULK_BATCH_SIZE', '100')),
            max_batch_size=int(os.getenv('BULK_MAX_BATCH_SIZE', '1000')),
            min_batch_size=int(os.getenv('BULK_MIN_BATCH_SIZE', '10')),
            timeout_seconds=int(os.getenv('BULK_TIMEOUT_SECONDS', '30')),
            retry_attempts=int(os.getenv('BULK_RETRY_ATTEMPTS', '3')),
            retry_delay=float(os.getenv('BULK_RETRY_DELAY', '1.0')),
            conflict_strategy=os.getenv('BULK_CONFLICT_STRATEGY', 'UPDATE'),
            enable_progress_tracking=os.getenv('BULK_ENABLE_PROGRESS_TRACKING', 'true').lower() == 'true',
            enable_detailed_logging=os.getenv('BULK_ENABLE_DETAILED_LOGGING', 'true').lower() == 'true',
            memory_limit_mb=int(os.getenv('BULK_MEMORY_LIMIT_MB', '512')),
            enable_streaming=os.getenv('BULK_ENABLE_STREAMING', 'true').lower() == 'true',
            checkpoint_interval=int(os.getenv('BULK_CHECKPOINT_INTERVAL', '50'))
        )
    
    def validate(self) -> List[str]:
        """Validate bulk operation configuration."""
        errors = []
        
        if self.batch_size < self.min_batch_size:
            errors.append(f"Batch size {self.batch_size} is below minimum {self.min_batch_size}")
        
        if self.batch_size > self.max_batch_size:
            errors.append(f"Batch size {self.batch_size} exceeds maximum {self.max_batch_size}")
        
        if self.timeout_seconds <= 0:
            errors.append("Timeout must be positive")
        
        if self.retry_attempts < 0:
            errors.append("Retry attempts cannot be negative")
        
        if self.conflict_strategy not in ["UPDATE", "IGNORE", "FAIL"]:
            errors.append("Conflict strategy must be UPDATE, IGNORE, or FAIL")
        
        if self.memory_limit_mb <= 0:
            errors.append("Memory limit must be positive")
        
        if self.checkpoint_interval <= 0:
            errors.append("Checkpoint interval must be positive")
        
        return errors
    
    def optimize_batch_size(self, record_count: int, estimated_record_size_bytes: int = 1024) -> int:
        """Optimize batch size based on data volume and memory constraints."""
        # Calculate memory-based optimal batch size
        memory_bytes = self.memory_limit_mb * 1024 * 1024
        memory_based_batch = max(self.min_batch_size, memory_bytes // estimated_record_size_bytes)
        
        # Use smaller of configured batch size and memory-based batch size
        optimal_batch = min(self.batch_size, memory_based_batch, self.max_batch_size)
        
        # For very small datasets, reduce batch size
        if record_count < optimal_batch:
            optimal_batch = max(self.min_batch_size, record_count // 4)
        
        return optimal_batch

@dataclass
class ScrapingConfig:
    """Scraping configuration settings"""
    rate_limit_delay: float = 7.0  # Updated to match CLI defaults
    max_retries: int = 3
    timeout: int = 30
    user_agent: str = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    max_workers: int = 1  # Reduced from 3 to avoid concurrent requests
    jitter_range: float = 5.0  # Updated to provide 7-12 second range (7 + 5 = 12)
    
    @classmethod
    def from_env(cls) -> 'ScrapingConfig':
        """Create scraping config from environment variables"""
        return cls(
            rate_limit_delay=float(os.getenv('RATE_LIMIT_DELAY', '7.0')),  # Default to 7 seconds
            max_retries=int(os.getenv('MAX_RETRIES', '3')),
            timeout=int(os.getenv('REQUEST_TIMEOUT', '30')),
            user_agent=os.getenv('USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'),
            max_workers=int(os.getenv('MAX_WORKERS', '1')),  # Default to single worker
            jitter_range=float(os.getenv('JITTER_RANGE', '5.0'))  # Updated to provide 7-12 second range
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

@dataclass
class MonitoringConfig:
    """Performance monitoring configuration settings"""
    enabled: bool = True
    collection_interval_seconds: int = 5
    retention_days: int = 30
    real_time_display: bool = True
    baseline_sample_size: int = 10
    performance_degradation_threshold: float = 0.20  # 20%
    memory_alert_threshold_mb: float = 1000.0
    cpu_alert_threshold_percent: float = 80.0
    error_rate_alert_threshold: float = 0.05  # 5%
    timeout_alert_threshold_seconds: float = 30.0
    export_format: str = "json"  # json, csv, html
    auto_baseline_creation: bool = True
    alert_cooldown_minutes: int = 15
    max_stored_metrics: int = 10000
    max_stored_alerts: int = 1000
    alert_thresholds: Dict[str, float] = field(default_factory=lambda: {
        'scraping_operation': 15.0,
        'database_bulk_insert': 10.0,
        'data_validation': 5.0,
        'network_request': 30.0
    })
    
    @classmethod
    def from_env(cls) -> 'MonitoringConfig':
        """Create monitoring config from environment variables"""
        alert_thresholds = {}
        
        # Parse alert thresholds from environment
        for key, default_value in {
            'scraping_operation': 15.0,
            'database_bulk_insert': 10.0,
            'data_validation': 5.0,
            'network_request': 30.0
        }.items():
            env_key = f'MONITORING_THRESHOLD_{key.upper()}'
            alert_thresholds[key] = float(os.getenv(env_key, str(default_value)))
        
        return cls(
            enabled=os.getenv('MONITORING_ENABLED', 'true').lower() == 'true',
            collection_interval_seconds=int(os.getenv('MONITORING_COLLECTION_INTERVAL', '5')),
            retention_days=int(os.getenv('MONITORING_RETENTION_DAYS', '30')),
            real_time_display=os.getenv('MONITORING_REAL_TIME_DISPLAY', 'true').lower() == 'true',
            baseline_sample_size=int(os.getenv('MONITORING_BASELINE_SAMPLE_SIZE', '10')),
            performance_degradation_threshold=float(os.getenv('MONITORING_DEGRADATION_THRESHOLD', '0.20')),
            memory_alert_threshold_mb=float(os.getenv('MONITORING_MEMORY_ALERT_MB', '1000.0')),
            cpu_alert_threshold_percent=float(os.getenv('MONITORING_CPU_ALERT_PERCENT', '80.0')),
            error_rate_alert_threshold=float(os.getenv('MONITORING_ERROR_RATE_THRESHOLD', '0.05')),
            timeout_alert_threshold_seconds=float(os.getenv('MONITORING_TIMEOUT_THRESHOLD', '30.0')),
            export_format=os.getenv('MONITORING_EXPORT_FORMAT', 'json'),
            auto_baseline_creation=os.getenv('MONITORING_AUTO_BASELINE', 'true').lower() == 'true',
            alert_cooldown_minutes=int(os.getenv('MONITORING_ALERT_COOLDOWN_MINUTES', '15')),
            max_stored_metrics=int(os.getenv('MONITORING_MAX_METRICS', '10000')),
            max_stored_alerts=int(os.getenv('MONITORING_MAX_ALERTS', '1000')),
            alert_thresholds=alert_thresholds
        )
    
    def validate(self) -> List[str]:
        """Validate monitoring configuration"""
        errors = []
        
        if self.collection_interval_seconds <= 0:
            errors.append("Collection interval must be positive")
        
        if self.retention_days <= 0:
            errors.append("Retention days must be positive")
        
        if self.baseline_sample_size < 3:
            errors.append("Baseline sample size must be at least 3")
        
        if not 0.0 <= self.performance_degradation_threshold <= 1.0:
            errors.append("Performance degradation threshold must be between 0.0 and 1.0")
        
        if self.memory_alert_threshold_mb <= 0:
            errors.append("Memory alert threshold must be positive")
        
        if not 0.0 <= self.cpu_alert_threshold_percent <= 100.0:
            errors.append("CPU alert threshold must be between 0 and 100")
        
        if not 0.0 <= self.error_rate_alert_threshold <= 1.0:
            errors.append("Error rate alert threshold must be between 0.0 and 1.0")
        
        if self.export_format not in ['json', 'csv', 'html']:
            errors.append("Export format must be json, csv, or html")
        
        if self.max_stored_metrics <= 0:
            errors.append("Max stored metrics must be positive")
        
        if self.max_stored_alerts <= 0:
            errors.append("Max stored alerts must be positive")
        
        return errors
    
    def get_operation_threshold(self, operation_type: str) -> float:
        """Get timeout threshold for specific operation type"""
        return self.alert_thresholds.get(operation_type, self.timeout_alert_threshold_seconds)

class Config:
    """Main configuration class that combines all config sections"""
    
    def __init__(self):
        self.database = DatabaseConfig.from_env()
        self.bulk_operations = BulkOperationConfig.from_env()
        self.scraping = ScrapingConfig.from_env()
        self.logging = LoggingConfig.from_env()
        self.app = AppConfig.from_env()
        self.monitoring = MonitoringConfig.from_env()  # Add monitoring config
        self.split_types = SplitTypes()
        self.split_categories = SplitCategories()
    
    def validate(self) -> List[str]:
        """Validate configuration and return any errors"""
        errors = []
        
        # Validate database connection string
        if not self.database.connection_string:
            errors.append("DATABASE_URL is required")
        
        # Validate bulk operations
        bulk_errors = self.bulk_operations.validate()
        errors.extend([f"Bulk operations: {error}" for error in bulk_errors])
        
        # Validate monitoring configuration
        monitoring_errors = self.monitoring.validate()
        errors.extend([f"Monitoring: {error}" for error in monitoring_errors])
        
        # Validate rate limiting
        if self.scraping.rate_limit_delay < 3.0:
            errors.append("Rate limit delay must be at least 3.0 seconds to respect PFR limits")
        
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
        return max(3.0, base_delay + jitter)  # Minimum 3 seconds

# Global configuration instance
config = Config()

# Export commonly used settings
DATABASE_URL = config.get_database_url()
RATE_LIMIT_DELAY = config.scraping.rate_limit_delay
TARGET_SEASON = config.app.target_season
MAX_RETRIES = config.scraping.max_retries
USER_AGENT = config.scraping.user_agent 