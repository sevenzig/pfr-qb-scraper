# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### CLI Usage
The project provides a professional CLI interface accessible via:
```bash
nfl-qb-scraper --help
# OR run via module
python -m src.cli.cli_main --help
```

### Development Setup
```bash
# Install in development mode with all dependencies
pip install -e ".[dev]"

# Install from requirements
pip install -r requirements.txt
```

### Testing Commands
```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_specific_file.py

# Run with coverage
pytest tests/ --cov=src
```

### Code Quality Commands
```bash
# Type checking
mypy src/

# Code formatting
black src/ tests/

# Linting
flake8 src/ tests/
```

### Database Setup
```bash
# Initialize database with schema
psql -d your_database -f sql/schema.sql

# Or use setup script
python setup/deploy_schema.py
```

## Architecture Overview

### Core Components Architecture
The system follows a dependency injection pattern with clear separation of concerns:

**CLI Layer** (`src/cli/`) - Command handlers that delegate to operations
- Commands inherit from `BaseCommand` with standardized patterns
- CLI delegates business logic to operation classes
- Commands include: scrape, validate, monitor, health, batch, data, cleanup

**Operations Layer** (`src/operations/`) - High-level business operations
- `ScrapingOperation` - Orchestrates scraping workflows
- `ValidationOps` - Data validation and quality checks  
- `BatchManager` - Batch processing with resumability
- `PerformanceMonitor` - Metrics and monitoring

**Core Business Logic** (`src/core/`) - Core scraping components  
- `CoreScraper` - Main orchestrator using dependency injection
- `RequestManager` - HTTP requests, rate limiting, retries
- `HTMLParser` - Data extraction and table parsing
- `SeleniumManager` - Browser automation when needed

**Data Layer** (`src/database/`, `src/models/`)
- `DatabaseManager` - Connection pooling and transactions
- Type-safe data models with comprehensive validation
- PostgreSQL schema with Supabase support

### Key Architectural Patterns

**Dependency Injection**: All core components accept dependencies via constructor
```python
scraper = CoreScraper(
    request_manager=RequestManager(rate_limit_delay=2.0),
    html_parser=HTMLParser(),
    db_manager=DatabaseManager(),
    config=config
)
```

**Specific Exception Types**: Clear error handling with context
```python
try:
    result = scraper.scrape_season(2024)
except NetworkError as e:
    logger.error(f"Network issue: {e}")
except DataParsingError as e:
    logger.error(f"Data parsing failed: {e}")
```

**Type Safety**: Comprehensive type hints throughout
```python
def scrape_season_qbs(self, season: int) -> List[QBBasicStats]:
def parse_splits_tables(self, soup: BeautifulSoup) -> List[Dict[str, Union[str, int, float]]]:
```

## Scraping Requirements & Compliance

### Data Completeness
- ALL scrapers must extract every column defined in `sql/schema.sql`
- QB Basic Stats: 33 columns required
- QB Splits: 34 columns required  
- QB Splits Advanced: 20 columns required
- NEVER implement partial scraping - validate all required fields

### Rate Limiting (Critical)
- MINIMUM 7 seconds between all Pro Football Reference requests
- MAXIMUM 100 requests per hour to PFR
- 30-second timeout on all requests
- Exponential backoff for failed requests
- All scraping operations must be resumable

### Data Validation
- Validate all scraped data against schema before database insertion
- Log missing fields with player name, split type, and field details
- Maintain comprehensive validation logs for quality tracking

## Configuration & Environment

### Environment Setup
```bash
# Copy and configure environment
cp .env.example .env

# Required environment variables:
# DATABASE_URL="postgresql://user:password@host:port/database"
# SUPABASE_URL="https://your-project.supabase.co"  
# SUPABASE_KEY="your-supabase-anon-key"
```

### Configuration Management
All configuration is centralized in `src/config/config.py` with environment-specific overrides. Never hardcode configuration values.

## Testing Approach

### Test Structure
- Unit tests for individual components with mocking
- Integration tests for database operations  
- End-to-end tests for complete scraping workflows
- Minimum 85% test coverage required

### Test Database
Use separate test databases - never test against production data. Mock external API calls for unit tests.

## Migration Context

This project is currently migrating from scattered scripts to a unified CLI architecture. The migration follows strict phases:

**Phase 1-3**: Maintain backwards compatibility with existing scripts
**Phase 4**: Deprecate legacy scripts after CLI equivalence is proven

Always preserve existing functionality during migration and provide clear migration paths for users.

## Performance & Quality Standards

### Code Quality Requirements
- All functions must have complete type hints and docstrings
- Use structured logging with context (player names, seasons, operation details)
- Implement proper error handling with specific exception types
- Follow PEP 8 style guidelines strictly

### Performance Monitoring  
- Track request success/failure rates and timing
- Monitor memory usage during large operations
- Database query performance monitoring
- Data quality metrics and validation reporting

## Development Workflow

When making changes:
1. Ensure all scraped columns match `sql/schema.sql` requirements
2. Validate rate limiting compliance (7+ second delays)
3. Run type checking: `mypy src/`
4. Run tests: `pytest tests/`  
5. Check code formatting: `black src/ tests/`
6. Verify comprehensive error handling and logging