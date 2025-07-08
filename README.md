# NFL QB Data Scraping System

## Quickstart

Follow these steps to set up the project, initialize the database, and run your first scrape:

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd qb-scraper
   ```

2. **Install Python dependencies**
   ```bash
   # Using uv (recommended)
   uv sync
   # Or using pip
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   - Copy the example file and edit as needed:
     ```bash
     cp env.example .env
     # Edit .env with your Supabase/Postgres credentials and config
     ```
   - Or use the interactive setup script (if available):
     ```bash
     python scripts/setup_supabase_env.py
     ```

4. **Initialize the Supabase/Postgres database**
   - Create a new database on [Supabase](https://app.supabase.com/) or your local Postgres instance.
   - Deploy the schema:
     ```bash
     psql -d <your_database_url> -f sql/schema.sql
     # Or use the helper script:
     python scripts/deploy_schema_to_supabase.py
     ```

5. **(Optional) Populate teams table**
   - If your schema requires NFL teams, run:
     ```bash
     python scripts/populate_teams.py
     ```

6. **Run the main scraping script**
   - To scrape all QB data for the 2024 season:
     ```bash
     python scripts/scrape_qb_data_2024.py
     ```
   - To scrape a single player (e.g., Joe Burrow):
     ```bash
     python scripts/scrape_joe_burrow.py
     ```
   - For quick tests or debugging, see scripts in the `scripts/` and `debug/` directories.

7. **Check logs and results**
   - Logs are stored in the `logs/` directory.
   - Data files and outputs may be in `data/` or your configured database.

8. **Run tests**
   - To verify your setup:
     ```bash
     pytest
     # Or run specific test scripts in the tests/ directory
     ```

---

A comprehensive system for scraping NFL quarterback statistics and splits data from Pro Football Reference, storing it in a PostgreSQL database via Supabase, and providing type-safe access via Drizzle ORM.

## Features

### Data Collection
- **Comprehensive QB Statistics**: Scrapes all main QB stats including passing, rushing, and advanced metrics
- **Automatic Split Discovery**: Automatically discovers and scrapes all available split categories on player pages
- **Multi-Season Support**: Supports scraping data for any NFL season (currently optimized for 2024)
- **Real-time Data**: Scrapes current season data from Pro Football Reference
- **Historical Data**: Can scrape historical seasons for analysis and comparison

### Technical Features
- **Robust Error Handling**: Implements retries, exponential backoff, and rate limiting (respects PFR's 20 requests/minute limit)
- **Data Validation**: Comprehensive validation pipelines for statistical consistency and completeness
- **Performance Monitoring**: Detailed logging and metrics for scraping progress and data quality
- **Concurrent Processing**: Multi-threaded scraping with rate limiting and jitter
- **Database Integration**: Optimized PostgreSQL schema with proper constraints, indexes, and RLS policies
- **Type-Safe Access**: Drizzle ORM schema with TypeScript types for frontend applications

### User Experience
- **CLI Interface**: Command-line interface with options for season selection, splits-only mode, validation, and monitoring
- **Flexible Configuration**: Environment-based configuration with sensible defaults
- **Comprehensive Logging**: Detailed logs for debugging and monitoring
- **Test Suite**: Comprehensive test coverage for all components
- **Documentation**: Extensive documentation and examples

## Tech Stack

### Backend & Data Processing
- **Python 3.8+**: Core scraping and data processing
- **Requests + BeautifulSoup**: Web scraping and HTML parsing
- **Pandas**: Data manipulation, cleaning, and analysis
- **SQLAlchemy**: Database ORM and connection management
- **psycopg2**: PostgreSQL database adapter

### Database & Infrastructure
- **PostgreSQL**: Primary database storage
- **Supabase**: Database hosting, management, and real-time features
- **Drizzle ORM**: Type-safe database access for TypeScript applications
- **Connection Pooling**: Efficient database connection management

### Development & Testing
- **pytest**: Testing framework
- **uv**: Fast Python package manager
- **TypeScript**: Type definitions for frontend integration
- **Git**: Version control
- **Docker**: Containerization (optional)

### Monitoring & Logging
- **Python logging**: Comprehensive application logging
- **Custom metrics**: Performance and data quality monitoring
- **Error tracking**: Detailed error reporting and debugging

## Project Structure

```
qb-scraper/
├── src/                          # Main source code
│   ├── scrapers/                 # Web scraping modules
│   │   ├── enhanced_scraper.py   # Enhanced scraper with split discovery
│   │   └── nfl_qb_scraper.py     # Main pipeline orchestrator
│   ├── database/                 # Database operations
│   │   └── db_manager.py         # Database manager with connection pooling
│   ├── models/                   # Data models and schemas
│   │   └── qb_models.py          # Python dataclasses for data models
│   ├── utils/                    # Utility functions
│   │   └── data_utils.py         # Data processing utilities
│   ├── config/                   # Configuration files
│   │   ├── config.py             # Centralized configuration management
│   │   └── player_config.py      # Player-specific configuration
│   └── cli/                      # Command-line interface
│       └── scraper_cli.py        # CLI with multiple commands
├── scripts/                      # Utility and execution scripts
│   ├── scrape_qb_data_2024.py    # Main 2024 season scraper
│   ├── scrape_joe_burrow.py      # Single player scraper example
│   ├── enhanced_qb_scraper.py    # Enhanced scraper with all features
│   ├── populate_teams.py         # Populate teams table
│   ├── deploy_schema_to_supabase.py # Database schema deployment
│   └── setup_supabase_env.py     # Environment setup helper
├── debug/                        # Debug and troubleshooting scripts
│   ├── debug_*.py                # Various debugging utilities
│   └── check_*.py                # Data validation and checking scripts
├── tests/                        # Test files and test data
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   └── fixtures/                 # Test data fixtures
├── docs/                         # Documentation
│   ├── setup-guide.md            # Detailed setup instructions
│   ├── SUPABASE_DEPLOYMENT.md    # Supabase deployment guide
│   └── SINGLE_PLAYER_SCRAPING.md # Single player scraping guide
├── sql/                          # SQL schemas and migrations
│   └── schema.sql                # Complete database schema
├── data/                         # Data files and outputs
│   └── player_urls_2024.txt      # Player URL lists
├── logs/                         # Application logs
│   ├── nfl_qb_scraper.log        # Main application logs
│   ├── cli.log                   # CLI operation logs
│   └── *.log                     # Various log files
├── setup/                        # Setup and installation files
├── main.py                       # Main entry point
├── requirements.txt              # Python dependencies
├── pyproject.toml               # Project configuration
├── uv.lock                      # Dependency lock file
└── README.md                    # This file
```

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd qb-scraper
   ```

2. **Install Python dependencies**:
   ```bash
   # Using uv (recommended)
   uv sync
   
   # Or using pip
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   # Interactive setup (recommended)
   python setup_env.py
   
   # Or manually
   cp env.example .env
   # Edit .env with your database credentials and configuration
   ```

4. **Set up database**:
   - Create a PostgreSQL database (local or Supabase)
   - Run the schema: `psql -d your_database -f sql/schema.sql`
   - Update `DATABASE_URL` in your `.env` file

## Configuration

The system uses environment variables for configuration. Create a `.env` file in the root directory with the following settings:

### Required Environment Variables

#### Database Configuration
```bash
# Supabase/PostgreSQL connection string
DATABASE_URL=postgresql://username:password@host:port/database

# Connection pool settings
DB_MAX_CONNECTIONS=10
DB_CONNECTION_TIMEOUT=30
```

#### Scraping Configuration
```bash
# Rate limiting (respects PFR's 20 requests/minute limit)
RATE_LIMIT_DELAY=3.0
MAX_RETRIES=3
MAX_WORKERS=4
JITTER_RANGE=0.5

# Target season for scraping
TARGET_SEASON=2024
```

### Optional Environment Variables

#### Application Configuration
```bash
# Enable/disable features
DATA_VALIDATION_ENABLED=true
AUTO_DISCOVERY_ENABLED=true
LOG_LEVEL=INFO

# Output settings
SAVE_TO_CSV=false
SAVE_TO_DATABASE=true
```

#### Advanced Configuration
```bash
# Request settings
REQUEST_TIMEOUT=30
USER_AGENT=Mozilla/5.0 (compatible; NFL-QB-Scraper/1.0)

# Database settings
DB_POOL_RECYCLE=3600
DB_POOL_PRE_PING=true
```

### Configuration Files

#### `src/config/config.py`
Centralized configuration management with environment variable loading and validation.

#### `src/config/player_config.py`
Player-specific configuration for custom scraping scenarios.

### Environment Setup Helper

Use the provided setup script to configure your environment:
```bash
python scripts/setup_supabase_env.py
```

This script will:
- Prompt for your Supabase credentials
- Create a `.env` file with proper configuration
- Validate the database connection
- Set up initial database schema

## Usage

### Available Scripts

The project includes several scripts for different use cases:

#### Main Scraping Scripts

**`scripts/scrape_qb_data_2024.py`** - Main scraper for 2024 season
```bash
# Run the main 2024 season scraper
python scripts/scrape_qb_data_2024.py

# This script will:
# - Scrape all QB stats for the 2024 season
# - Discover and scrape all available splits
# - Save data to the configured database
# - Generate comprehensive logs
```

**`scripts/enhanced_qb_scraper.py`** - Enhanced scraper with all features
```bash
# Run the enhanced scraper
python scripts/enhanced_qb_scraper.py

# Features:
# - Automatic split discovery
# - Comprehensive error handling
# - Data validation
# - Performance monitoring
```

**`scripts/scrape_joe_burrow.py`** - Single player scraper example
```bash
# Scrape data for Joe Burrow
python scripts/scrape_joe_burrow.py

# Use as a template for scraping other players
```

#### Utility Scripts

**`scripts/populate_teams.py`** - Populate teams table
```bash
# Populate the teams table with NFL team data
python scripts/populate_teams.py
```

**`scripts/deploy_schema_to_supabase.py`** - Deploy database schema
```bash
# Deploy the complete database schema to Supabase
python scripts/deploy_schema_to_supabase.py
```

**`scripts/reset_database.py`** - Reset database (use with caution)
```bash
# Reset the database (drops and recreates all tables)
python scripts/reset_database.py
```

#### Debug Scripts

**`debug/debug_*.py`** - Various debugging utilities
```bash
# Debug specific aspects of the scraping process
python debug/debug_column_names.py
python debug/debug_name_matching.py
python debug/debug_2024_stats.py
```

**`debug/check_*.py`** - Data validation scripts
```bash
# Check data integrity and validation
python debug/check_teams.py
python debug/check_2024_tables.py
```

### Command Line Interface

The system provides a comprehensive CLI with multiple commands:

#### Scrape Data
```bash
# Scrape all QB data for 2024 season
python main.py scrape --season 2024

# Scrape only splits data (skip main stats)
python main.py scrape --season 2024 --splits-only

# Scrape specific players
python main.py scrape --season 2024 --players "Patrick Mahomes" "Josh Allen"

# Custom rate limiting
python main.py scrape --season 2024 --rate-limit 5.0

# Validate data during scraping
python main.py scrape --season 2024 --validate
```

#### Validate Data
```bash
# Validate data integrity
python main.py validate

# Validate with database statistics
python main.py validate --stats

# Validate specific tables
python main.py validate --table qb_stats
```

#### Monitor System
```bash
# Show recent scraping sessions
python main.py monitor --recent

# Show performance metrics
python main.py monitor --performance

# Show data quality metrics
python main.py monitor --quality

# Show all monitoring data
python main.py monitor

# Export monitoring data
python main.py monitor --export monitoring_report.csv
```

#### Health Check
```bash
# Perform system health check
python main.py health

# Detailed health check
python main.py health --verbose
```

#### Cleanup
```bash
# Clean up old scraping logs (older than 30 days)
python main.py cleanup --days 30

# Clean up old data
python main.py cleanup --data --older-than 90
```

### Programmatic Usage

#### Basic Usage
```python
from src.scrapers.nfl_qb_scraper import NFLQBDataPipeline

# Initialize pipeline
pipeline = NFLQBDataPipeline()

# Run scraping for 2024 season
results = pipeline.run_pipeline(season=2024)

# Check results
print(f"Success: {results['success']}")
print(f"QB Stats: {results['qb_stats_count']}")
print(f"QB Splits: {results['qb_splits_count']}")
```

#### Advanced Usage
```python
from src.scrapers.enhanced_scraper import EnhancedQBScraper
from src.database.db_manager import DatabaseManager

# Initialize components
scraper = EnhancedQBScraper()
db_manager = DatabaseManager()

# Configure scraping options
scraper.set_rate_limit(3.0)
scraper.enable_validation(True)
scraper.set_max_workers(4)

# Scrape specific player
player_data = scraper.scrape_player("Patrick Mahomes", season=2024)

# Save to database
db_manager.save_qb_stats(player_data['stats'])
db_manager.save_qb_splits(player_data['splits'])
```

#### Custom Data Processing
```python
from src.models.qb_models import QBStats, QBSplitStats
from src.utils.data_utils import validate_qb_stats

# Create custom QB stats
stats = QBStats(
    player_id="mahoPa00",
    player_name="Patrick Mahomes",
    team="KAN",
    season=2024,
    games_played=17,
    # ... other fields
)

# Validate data
errors = validate_qb_stats(stats)
if not errors:
    # Save to database
    db_manager.save_qb_stats([stats])
```

## Database Schema

The system uses a comprehensive PostgreSQL schema with the following main tables:

### Core Tables
- `qb_stats`: Main quarterback statistics by season
- `qb_splits`: Quarterback performance splits by various categories
- `players`: Player master data and biographical information
- `teams`: NFL team information and organizational data
- `qb_game_log`: Individual game performance data
- `scraping_log`: Scraping session logs and monitoring data

### Key Features
- **Constraints**: Data integrity constraints (completion ratios, rating ranges, etc.)
- **Indexes**: Optimized indexes for common query patterns
- **Views**: Pre-built views for common analytics queries
- **Functions**: Stored procedures for data validation and common queries
- **RLS Policies**: Row-level security for Supabase integration

## Data Models

### QBStats
```python
@dataclass
class QBStats:
    player_id: str
    player_name: str
    team: str
    season: int
    games_played: int
    games_started: int
    completions: int
    attempts: int
    completion_pct: Decimal
    pass_yards: int
    pass_tds: int
    interceptions: int
    rating: Decimal
    qbr: Optional[Decimal]
    # ... additional fields
```

### QBSplitStats
```python
@dataclass
class QBSplitStats:
    player_id: str
    player_name: str
    team: str
    season: int
    split_type: str
    split_category: str
    games: int
    completions: int
    attempts: int
    completion_pct: Decimal
    pass_yards: int
    pass_tds: int
    interceptions: int
    rating: Decimal
    # ... additional fields
```

## Split Types

The system automatically discovers and scrapes the following split categories:

### Basic Splits
- **Home/Away**: Performance in home vs away games
- **By Quarter**: Performance by game quarter
- **By Half**: Performance by game half
- **By Month**: Performance by calendar month
- **By Down**: Performance by down (1st, 2nd, 3rd, 4th)
- **By Distance**: Performance by distance needed
- **Win/Loss**: Performance in wins vs losses

### Advanced Splits
- **vs Division**: Performance against division opponents
- **Indoor/Outdoor**: Performance in indoor vs outdoor games
- **Surface**: Performance on different field surfaces
- **Weather**: Performance in different weather conditions
- **Temperature**: Performance in different temperature ranges
- **By Score**: Performance based on game situation
- **Red Zone**: Performance in red zone situations
- **Time of Game**: Performance by game time
- **vs Winning Teams**: Performance against teams with different records
- **Day of Week**: Performance by day of the week
- **Game Time**: Performance by game start time
- **Playoff Type**: Performance in different playoff scenarios

## Error Handling

The system implements comprehensive error handling:

### Rate Limiting
- Respects PFR's 20 requests/minute limit
- Implements exponential backoff with jitter
- Tracks rate limit violations

### Retry Logic
- Automatic retries for failed requests
- Configurable retry attempts and delays
- Different retry strategies for different error types

### Data Validation
- Statistical consistency checks
- Range validation for all numeric fields
- Relationship validation between fields
- Completeness checks for required data

### Monitoring
- Detailed logging of all operations
- Performance metrics tracking
- Error aggregation and reporting
- Data quality metrics

## Performance Optimization

### Scraping Performance
- Concurrent processing with rate limiting
- Connection pooling for database operations
- Bulk insert operations for efficiency
- Memory-efficient data processing

### Database Performance
- Optimized indexes for common queries
- Partitioned tables for large datasets
- Query optimization with EXPLAIN analysis
- Connection pooling and statement caching

### Memory Management
- Streaming data processing for large datasets
- Proper resource cleanup
- Memory monitoring and optimization
- Efficient data structures

## Security Considerations

### Data Protection
- Environment variable configuration
- No hardcoded credentials
- Input validation and sanitization
- SQL injection prevention with parameterized queries

### API Security
- Proper User-Agent headers
- Rate limiting compliance
- HTTPS for all external communications
- SSL certificate validation

### Database Security
- Row-level security policies
- Connection encryption
- Proper authentication
- Audit logging

## Monitoring and Logging

### Logging Levels
- **DEBUG**: Detailed debugging information
- **INFO**: General operational information
- **WARNING**: Warning conditions
- **ERROR**: Error conditions
- **CRITICAL**: Critical system failures

### Metrics Tracked
- Request success/failure rates
- Processing times
- Data quality metrics
- Rate limit violations
- Database performance
- Memory usage

### Log Files
- `logs/nfl_qb_scraper.log`: Main application logs
- `logs/cli.log`: CLI operation logs
- `logs/main.log`: Entry point logs

## Testing

### Unit Tests
- Test all public methods and functions
- Mock external dependencies
- Test both success and failure scenarios
- Maintain high test coverage

### Integration Tests
- Test database operations
- Test web scraping with mock responses
- Test end-to-end data flow
- Test error scenarios

### Test Data
- Use realistic but anonymized test data
- Create test fixtures for common scenarios
- Implement data factories for test objects

## Development

### Development Environment Setup

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd qb-scraper
   uv sync
   ```

2. **Install development dependencies**:
   ```bash
   # Install pre-commit hooks
   pre-commit install
   
   # Install development tools
   pip install black flake8 mypy pytest pytest-cov
   ```

3. **Setup local database** (optional):
   ```bash
   # Use Docker for local PostgreSQL
   docker run --name qb-scraper-db -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres:15
   
   # Update .env with local database URL
   DATABASE_URL=postgresql://postgres:password@localhost:5432/qb_scraper
   ```

### Code Quality Standards

#### Python Code Style
- Follow **PEP 8** style guidelines strictly
- Use **Black** for code formatting
- Use **flake8** for linting
- Use **mypy** for type checking

#### Code Structure
- Use **type hints** for all function parameters and return values
- Include **comprehensive docstrings** for all public functions
- Implement **proper error handling** with specific exception types
- Use **dataclasses** for data models
- Follow **SOLID principles** for class design

#### Example Code Structure
```python
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class QBStats:
    """Quarterback statistics data model."""
    player_id: str
    player_name: str
    season: int
    # ... other fields

def scrape_qb_data(player_id: str, season: int) -> Optional[QBStats]:
    """
    Scrape quarterback data for a specific player and season.
    
    Args:
        player_id: Pro Football Reference player ID
        season: NFL season year
        
    Returns:
        QBStats object if successful, None otherwise
        
    Raises:
        ScrapingError: If scraping fails
        ValidationError: If data validation fails
    """
    try:
        # Implementation here
        pass
    except Exception as e:
        logger.error(f"Failed to scrape data for {player_id}: {e}")
        raise ScrapingError(f"Scraping failed: {e}")
```

### Testing Guidelines

#### Unit Tests
- Test all public methods and functions
- Use **pytest** as the testing framework
- Maintain **>80% test coverage**
- Mock external dependencies (APIs, databases)
- Use **parameterized tests** for multiple scenarios

#### Integration Tests
- Test database operations with actual database
- Test web scraping with mock responses
- Test end-to-end data flow
- Use **test fixtures** for consistent data

#### Example Test Structure
```python
import pytest
from unittest.mock import Mock, patch
from src.scrapers.enhanced_scraper import EnhancedQBScraper

class TestEnhancedQBScraper:
    """Test cases for EnhancedQBScraper."""
    
    @pytest.fixture
    def scraper(self):
        """Create scraper instance for testing."""
        return EnhancedQBScraper()
    
    @pytest.fixture
    def mock_response(self):
        """Mock HTTP response."""
        mock = Mock()
        mock.status_code = 200
        mock.text = "<html>...</html>"
        return mock
    
    def test_scrape_player_success(self, scraper, mock_response):
        """Test successful player scraping."""
        with patch('requests.get', return_value=mock_response):
            result = scraper.scrape_player("mahoPa00", 2024)
            assert result is not None
            assert result.player_id == "mahoPa00"
    
    def test_scrape_player_failure(self, scraper):
        """Test player scraping failure."""
        with patch('requests.get', side_effect=Exception("Network error")):
            with pytest.raises(ScrapingError):
                scraper.scrape_player("invalid", 2024)
```

### Git Workflow

#### Branch Naming
- `feature/feature-name` - New features
- `bugfix/bug-description` - Bug fixes
- `hotfix/urgent-fix` - Critical fixes
- `refactor/component-name` - Code refactoring

#### Commit Messages
Follow conventional commit format:
```
type(scope): description

[optional body]

[optional footer]
```

Examples:
```
feat(scraper): add support for advanced splits

fix(database): resolve foreign key constraint issue

docs(readme): update installation instructions

test(validation): add comprehensive data validation tests
```

#### Pull Request Process
1. Create feature branch from `main`
2. Make changes with proper tests
3. Run all tests and linting
4. Create pull request with detailed description
5. Request code review
6. Address review feedback
7. Merge after approval

### Code Review Checklist

#### Functionality
- [ ] Code implements the intended feature/fix
- [ ] All edge cases are handled
- [ ] Error handling is comprehensive
- [ ] Performance considerations are addressed

#### Code Quality
- [ ] Code follows project style guidelines
- [ ] All functions have proper docstrings
- [ ] Type hints are used consistently
- [ ] No hardcoded values or magic numbers
- [ ] Code is readable and maintainable

#### Testing
- [ ] Tests are included and passing
- [ ] Test coverage is adequate
- [ ] Edge cases are tested
- [ ] Error scenarios are tested

#### Security
- [ ] No sensitive data in code
- [ ] Input validation is implemented
- [ ] SQL injection prevention
- [ ] Rate limiting is respected

#### Documentation
- [ ] README is updated if needed
- [ ] Code comments explain complex logic
- [ ] API changes are documented
- [ ] Configuration changes are documented

### Performance Guidelines

#### Database Operations
- Use **connection pooling**
- Implement **bulk operations** for large datasets
- Use **appropriate indexes**
- Monitor **query performance**

#### Scraping Performance
- Respect **rate limits**
- Use **concurrent processing** appropriately
- Implement **caching** where beneficial
- Monitor **memory usage**

#### Memory Management
- Use **generators** for large datasets
- Implement **proper cleanup**
- Monitor **memory leaks**
- Use **efficient data structures**

### Debugging and Monitoring

#### Logging
- Use **structured logging**
- Include **context information**
- Log at **appropriate levels**
- Include **timing information**

#### Monitoring
- Track **key metrics**
- Monitor **error rates**
- Track **performance metrics**
- Set up **alerts** for critical issues

## Troubleshooting

### Common Issues and Solutions

#### Database Connection Issues

**Problem**: Cannot connect to database
```bash
Error: connection to server at "host" failed
```

**Solutions**:
1. Verify `DATABASE_URL` in `.env` file
2. Check database server status
3. Verify network connectivity
4. Check firewall settings
5. Test connection manually:
   ```bash
   python scripts/quick_supabase_test.py
   ```

**Problem**: Connection pool exhausted
```bash
Error: too many connections
```

**Solutions**:
1. Reduce `DB_MAX_CONNECTIONS` in `.env`
2. Check for connection leaks in code
3. Restart the application

#### Scraping Issues

**Problem**: Rate limiting errors
```bash
Error: 429 Too Many Requests
```

**Solutions**:
1. Increase `RATE_LIMIT_DELAY` in `.env`
2. Reduce `MAX_WORKERS` for concurrent requests
3. Add more jitter with `JITTER_RANGE`

**Problem**: Missing data fields
```bash
Warning: Field 'team' is empty for player
```

**Solutions**:
1. Check if teams table is populated: `python debug/check_teams.py`
2. Verify player URL is correct
3. Check PFR website structure changes

**Problem**: HTML parsing errors
```bash
Error: Could not find table with expected structure
```

**Solutions**:
1. Check if PFR website structure changed
2. Update scraper logic if needed
3. Use debug scripts to inspect HTML:
   ```bash
   python debug/debug_splits_page.py
   ```

#### Data Validation Issues

**Problem**: Validation errors
```bash
Error: Completions (350) exceed attempts (300)
```

**Solutions**:
1. Review validation error messages
2. Check data source for changes
3. Verify configuration settings
4. Review scraping logic

**Problem**: Foreign key constraint violations
```bash
Error: insert or update on table violates foreign key constraint
```

**Solutions**:
1. Ensure teams table is populated: `python scripts/populate_teams.py`
2. Check player data integrity
3. Verify database schema matches models

### Debug Mode

Enable debug logging for detailed troubleshooting:
```bash
export LOG_LEVEL=DEBUG
python main.py scrape --season 2024
```

### Debug Scripts

Use the provided debug scripts to diagnose specific issues:

```bash
# Check database connection
python debug/check_supabase_connection.py

# Validate table structure
python debug/check_2024_tables.py

# Debug specific player scraping
python debug/debug_joe_burrow_2024.py

# Check column names in scraped data
python debug/debug_column_names.py
```

### Log Analysis

Check log files for detailed error information:
```bash
# View recent logs
tail -f logs/nfl_qb_scraper.log

# Search for errors
grep -i error logs/*.log

# Check scraping progress
grep -i "scraping" logs/nfl_qb_scraper.log
```

### Performance Issues

**Problem**: Slow scraping
- Increase `MAX_WORKERS` (but respect rate limits)
- Reduce `RATE_LIMIT_DELAY` (but stay within PFR limits)
- Check network connectivity

**Problem**: High memory usage
- Reduce batch sizes in database operations
- Process data in smaller chunks
- Monitor memory usage with system tools

### Getting Help

1. Check the logs in `logs/` directory
2. Run relevant debug scripts
3. Review this troubleshooting section
4. Check the documentation in `docs/` directory
5. Create an issue with:
   - Error messages and stack traces
   - Configuration (without sensitive data)
   - Steps to reproduce
   - Log files (if relevant)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## API Reference

### Core Classes

#### `EnhancedQBScraper`
Main scraper class for quarterback data collection.

```python
from src.scrapers.enhanced_scraper import EnhancedQBScraper

scraper = EnhancedQBScraper()

# Configure scraper
scraper.set_rate_limit(3.0)
scraper.enable_validation(True)
scraper.set_max_workers(4)

# Scrape player data
player_data = scraper.scrape_player("mahoPa00", season=2024)
```

**Methods**:
- `scrape_player(player_id: str, season: int) -> Dict[str, Any]`
- `scrape_all_players(season: int) -> List[Dict[str, Any]]`
- `discover_splits(player_id: str, season: int) -> List[str]`
- `set_rate_limit(delay: float) -> None`
- `enable_validation(enabled: bool) -> None`

#### `DatabaseManager`
Database operations and connection management.

```python
from src.database.db_manager import DatabaseManager

db_manager = DatabaseManager()

# Save data
db_manager.save_qb_stats(stats_list)
db_manager.save_qb_splits(splits_list)

# Query data
stats = db_manager.get_qb_stats(player_id="mahoPa00", season=2024)
splits = db_manager.get_qb_splits(player_id="mahoPa00", season=2024)
```

**Methods**:
- `save_qb_stats(stats: List[QBStats]) -> None`
- `save_qb_splits(splits: List[QBSplitStats]) -> None`
- `get_qb_stats(player_id: str, season: int) -> List[QBStats]`
- `get_qb_splits(player_id: str, season: int) -> List[QBSplitStats]`

### Data Models

#### `QBStats`
Main quarterback statistics model.

```python
@dataclass
class QBStats:
    player_id: str
    player_name: str
    team: str
    season: int
    games_played: int
    games_started: int
    completions: int
    attempts: int
    completion_pct: Decimal
    pass_yards: int
    pass_tds: int
    interceptions: int
    rating: Decimal
    qbr: Optional[Decimal]
    # ... additional fields
```

#### `QBSplitStats`
Quarterback splits statistics model.

```python
@dataclass
class QBSplitStats:
    player_id: str
    player_name: str
    team: str
    season: int
    split_type: str
    split_category: str
    games: int
    completions: int
    attempts: int
    completion_pct: Decimal
    pass_yards: int
    pass_tds: int
    interceptions: int
    rating: Decimal
    # ... additional fields
```

### Utility Functions

#### Data Validation
```python
from src.utils.data_utils import validate_qb_stats, validate_qb_splits

# Validate QB stats
errors = validate_qb_stats(stats)
if errors:
    print(f"Validation errors: {errors}")

# Validate QB splits
errors = validate_qb_splits(splits)
if errors:
    print(f"Validation errors: {errors}")
```

#### Data Processing
```python
from src.utils.data_utils import clean_player_name, normalize_team_name

# Clean player name
clean_name = clean_player_name("Patrick Mahomes II")

# Normalize team name
team_code = normalize_team_name("Kansas City Chiefs")
```

### Configuration

#### Environment Variables
All configuration is handled through environment variables. See the [Configuration](#configuration) section for details.

#### Configuration Classes
```python
from src.config.config import Config

config = Config()

# Access configuration values
db_url = config.database_url
rate_limit = config.rate_limit_delay
max_workers = config.max_workers
```

## Deployment

### Production Deployment

#### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "scripts/scrape_qb_data_2024.py"]
```

#### Environment Setup
```bash
# Production environment variables
DATABASE_URL=postgresql://user:pass@host:port/db
RATE_LIMIT_DELAY=3.0
MAX_WORKERS=4
LOG_LEVEL=INFO
DATA_VALIDATION_ENABLED=true
```

#### Monitoring
- Set up log aggregation (ELK stack, etc.)
- Monitor database performance
- Track scraping success rates
- Set up alerts for failures

### CI/CD Pipeline

#### GitHub Actions Example
```yaml
name: Scrape QB Data
on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM

jobs:
  scrape:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: python scripts/scrape_qb_data_2024.py
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

### Getting Help

1. **Check the documentation**:
   - This README
   - Documentation in `docs/` directory
   - Code comments and docstrings

2. **Use debug scripts**:
   - Run relevant scripts in `debug/` directory
   - Check logs in `logs/` directory

3. **Create an issue**:
   - Provide detailed error messages
   - Include configuration (without sensitive data)
   - Describe steps to reproduce
   - Attach relevant log files

### Contributing

We welcome contributions! Please see the [Contributing](#contributing) section for guidelines.

### Community

- **Issues**: Report bugs and request features
- **Discussions**: Ask questions and share ideas
- **Pull Requests**: Submit code improvements

### Acknowledgments

- **Pro Football Reference**: Data source
- **Supabase**: Database hosting and management
- **Open source community**: Libraries and tools used

---

**Note**: This project is for educational and research purposes. Please respect Pro Football Reference's terms of service and rate limits when using this scraper.
- Contact the maintainers

## Changelog

### Version 1.0.0
- Initial release
- Complete scraping system
- Database schema and models
- CLI interface
- Comprehensive documentation 