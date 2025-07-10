# Migration Rules & Guidelines

## Efficient, Effective, Quality-Focused Refactoring

### Core Principles

#### 1. **Incremental Progress Rule**

- **NEVER** break existing functionality during migration
- **ALWAYS** maintain backwards compatibility until deprecation
- **BUILD** new alongside old, then gradually transition
- **TEST** each increment before moving to next step

#### 2. **Single Responsibility Principle**

- **ONE MODULE = ONE PURPOSE** - No god classes or kitchen sink modules
- **CLEAR BOUNDARIES** - Each module should have obvious scope
- **MINIMAL COUPLING** - Modules should depend on interfaces, not
  implementations
- **MAXIMUM COHESION** - Related functionality should be grouped together

#### 3. **Quality Gates**

- **NO MERGE** without passing tests
- **NO COMMIT** without type hints and docstrings
- **NO RELEASE** without documentation updates
- **NO EXCEPTION** without explicit approval

---

## Migration Scope Rules

### ✅ **IN SCOPE - Must Migrate**

- **Core scraping logic** - All existing scraper functionality
- **Database operations** - Schema management, data operations
- **Configuration management** - Centralized config system
- **Error handling** - Consistent patterns across modules
- **Logging system** - Unified logging with proper levels
- **CLI interface** - User-friendly command structure

### ❌ **OUT OF SCOPE - Don't Touch**

- **Database schema changes** - Keep existing tables as-is
- **External API changes** - Don't modify Pro Football Reference scraping logic
- **Performance optimization** - Focus on structure, optimize later
- **New features** - Migration only, feature freeze during refactor
- **UI/Web interface** - CLI only for this migration

### ⚠️ **CONDITIONAL SCOPE - Case by Case**

- **Bug fixes** - Only if blocking migration or critical
- **Dependency updates** - Only if security critical
- **Code style changes** - Only if improving migration quality
- **Test data changes** - Only if needed for testing new structure

---

## Code Quality Standards

### **Type Safety Requirements**

````python
# ✅ REQUIRED - Full type hints
def scrape_player_stats(
    player_name: str,
    season: int,
    include_splits: bool = False
) -> PlayerStats:
    """Scrape player statistics with proper typing."""
    pass

# ❌ FORBIDDEN - No type hints
def scrape_player_stats(player_name, season, include_splits=False):
    pass
```text
### **Error Handling Standards**

```python
# ✅ REQUIRED - Specific exceptions with context
from src.utils.error_handling import ScrapingError, ValidationError

def process_player_data(data: Dict[str, Any]) -> PlayerStats:
    try:
        return PlayerStats.from_dict(data)
    except KeyError as e:
        raise ValidationError(f"Missing required field: {e}") from e
    except Exception as e:
        raise ScrapingError(f"Failed to process {data.get('name', 'unknown')}: {e}") from e

# ❌ FORBIDDEN - Bare except clauses
def process_player_data(data):
    try:
        return PlayerStats.from_dict(data)
    except:
        return None
```text
### **Logging Requirements**

```python
# ✅ REQUIRED - Structured logging with context
import logging
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)

def scrape_season_data(season: int) -> None:
    logger.info("Starting season scrape", extra={"season": season})
    try:
        # ... scraping logic
        logger.info("Season scrape completed", extra={
            "season": season,
            "players_scraped": count,
            "duration_seconds": duration
        })
    except Exception as e:
        logger.error("Season scrape failed", extra={
            "season": season,
            "error": str(e),
            "traceback": traceback.format_exc()
        })
        raise

# ❌ FORBIDDEN - Print statements or basic logging
def scrape_season_data(season):
    print(f"Scraping {season}")
    # ... logic
    print("Done")
```text
### **Documentation Standards**

```python
# ✅ REQUIRED - Comprehensive docstrings
def aggregate_multi_team_stats(
    player_stats: List[PlayerStats],
    prefer_combined: bool = True
) -> PlayerStats:
    """
    Aggregate statistics for players who played on multiple teams.

    Args:
        player_stats: List of PlayerStats objects for the same player
        prefer_combined: If True, prefer 2TM/3TM combined stats over individual team stats

    Returns:
        PlayerStats: Aggregated statistics for the player

    Raises:
        ValidationError: If player_stats is empty or contains incompatible data
        AggregationError: If aggregation logic fails

    Examples:
        >>> tim_boyle_stats = [boyle_mia, boyle_nyg, boyle_2tm]
        >>> aggregated = aggregate_multi_team_stats(tim_boyle_stats, prefer_combined=True)
        >>> assert aggregated.team == "2TM"
    """
    pass

# ❌ FORBIDDEN - Missing or minimal docstrings
def aggregate_multi_team_stats(player_stats, prefer_combined=True):
    """Aggregate stats."""
    pass
```text
---

## Module Design Rules

### **CLI Module Guidelines**

- **Command classes** inherit from `BaseCommand`
- **Argument parsing** centralized in command class
- **Business logic** delegated to operations modules
- **No direct database access** from CLI modules
- **Rich help text** with examples for every command

### **Core Module Guidelines**

- **Pure business logic** - no CLI or database code
- **Testable functions** - easy to unit test
- **Immutable data** where possible
- **Clear interfaces** - well-defined inputs/outputs
- **No side effects** - functions should be predictable

### **Operations Module Guidelines**

- **Orchestrate workflows** - combine core modules
- **Handle database transactions** - manage data consistency
- **Progress reporting** - provide user feedback
- **Error recovery** - graceful handling of failures
- **Resource management** - proper cleanup

### **Configuration Guidelines**

- **Environment-specific configs** - dev/staging/prod
- **Type-safe configuration** - use Pydantic models
- **Validation on load** - fail fast with clear errors
- **Secret management** - never hardcode secrets
- **Default fallbacks** - sensible defaults for optional settings

---

## Testing Requirements

### **Unit Test Standards**

```python
# ✅ REQUIRED - Comprehensive unit tests
import pytest
from unittest.mock import Mock, patch
from src.core.scraper import CoreScraper
from src.models.qb_models import PlayerStats

class TestCoreScraper:
    """Test suite for CoreScraper class."""

    @pytest.fixture
    def scraper(self):
        """Create scraper instance for testing."""
        return CoreScraper(config=Mock())

    @pytest.fixture
    def mock_response(self):
        """Mock HTTP response with test data."""
        # ... fixture setup

    def test_scrape_player_stats_success(self, scraper, mock_response):
        """Test successful player stats scraping."""
        with patch('requests.get', return_value=mock_response):
            result = scraper.scrape_player_stats("Joe Burrow", 2024)

        assert isinstance(result, PlayerStats)
        assert result.player_name == "Joe Burrow"
        assert result.season == 2024

    def test_scrape_player_stats_network_error(self, scraper):
        """Test handling of network errors during scraping."""
        with patch('requests.get', side_effect=requests.ConnectionError):
            with pytest.raises(ScrapingError, match="Network error"):
                scraper.scrape_player_stats("Joe Burrow", 2024)

    @pytest.mark.parametrize("season,expected_error", [
        (1800, "Invalid season"),
        (2030, "Future season"),
        ("2024", "Season must be integer"),
    ])
    def test_scrape_player_stats_invalid_season(self, scraper, season, expected_error):
        """Test validation of season parameter."""
        with pytest.raises(ValidationError, match=expected_error):
            scraper.scrape_player_stats("Joe Burrow", season)
```text
### **Integration Test Standards**

- **Database tests** use test database, not production
- **Network tests** use mocked responses or test endpoints
- **CLI tests** use subprocess calls with known inputs
- **End-to-end tests** cover complete workflows
- **Performance tests** validate acceptable response times

### **Test Coverage Requirements**

- **Minimum 85%** overall coverage
- **95%+ coverage** for core business logic
- **100% coverage** for critical error paths
- **Branch coverage** not just line coverage
- **Tests must be fast** - under 1 second per test

---

## Refactoring Process Rules

### **Step-by-Step Migration Process**

#### **Phase 1: Foundation**

1. **Create new directory structure** - Don't modify existing files
2. **Implement CLI foundation** - Basic argument parsing and routing
3. **Create base classes** - Abstract base classes for consistency
4. **Add configuration system** - Centralized config management
5. **Implement logging system** - Structured logging framework

#### **Phase 2: Core Migration**

1. **Extract core scraping logic** - Create `CoreScraper` class
2. **Migrate data models** - Enhance existing models
3. **Create validation framework** - Data quality checks
4. **Implement error handling** - Consistent error patterns
5. **Add progress tracking** - User feedback during operations

#### **Phase 3: Operations Layer**

1. **Create setup operations** - Database and schema management
2. **Create data operations** - CRUD and maintenance operations
3. **Create scraping operations** - High-level scraping workflows
4. **Add session management** - Resume failed operations
5. **Implement aggregation logic** - Multi-team player handling

#### **Phase 4: Testing & Quality**

1. **Comprehensive test suite** - Unit and integration tests
2. **Performance benchmarking** - Ensure no regressions
3. **Documentation complete** - CLI usage and development docs
4. **User acceptance testing** - Test with real workflows
5. **Legacy deprecation** - Move old scripts to legacy folder

### **Code Review Requirements**

#### **Every Pull Request Must Have:**

- [ ] **Automated tests pass** - CI/CD pipeline green
- [ ] **Code coverage maintained** - No coverage regressions
- [ ] **Type checking passes** - mypy validation clean
- [ ] **Linting passes** - flake8/black formatting
- [ ] **Documentation updated** - Docstrings and user docs
- [ ] **Performance impact assessed** - No significant regressions
- [ ] **Security review** - No new vulnerabilities
- [ ] **Backwards compatibility verified** - Existing functionality works

#### **Review Focus Areas:**

1. **Architecture compliance** - Follows modular design
2. **Error handling completeness** - All edge cases covered
3. **Configuration correctness** - Settings properly managed
4. **Test quality** - Tests are comprehensive and maintainable
5. **Documentation clarity** - Easy to understand and use

---

## Common Anti-Patterns to Avoid

### **❌ God Classes**

```python
# DON'T - Massive class doing everything
class MegaScraper:
    def scrape_stats(self): pass
    def validate_data(self): pass
    def save_to_database(self): pass
    def send_notifications(self): pass
    def generate_reports(self): pass
    def manage_configurations(self): pass
```text
### **❌ Circular Dependencies**

```python
# DON'T - Modules importing each other
# scraper.py
from .validator import DataValidator

# validator.py
from .scraper import CoreScraper  # CIRCULAR!
```text
### **❌ Configuration Hardcoding**

```python
# DON'T - Hardcoded values
DATABASE_URL = "postgresql://user:pass@localhost/db"
TIMEOUT = 30
MAX_RETRIES = 3

# DO - Configuration management
from src.config.settings import settings
DATABASE_URL = settings.database.url
TIMEOUT = settings.scraping.timeout
MAX_RETRIES = settings.scraping.max_retries
```text
### **❌ Silent Failures**

```python
# DON'T - Swallow errors silently
try:
    result = scrape_player_data(player)
except Exception:
    result = None  # Silent failure!

# DO - Handle errors explicitly
try:
    result = scrape_player_data(player)
except ScrapingError as e:
    logger.error(f"Failed to scrape {player}: {e}")
    raise
except ValidationError as e:
    logger.warning(f"Invalid data for {player}: {e}")
    return default_player_stats(player)
```text
---

## Quality Assurance Checklist

### **Before Starting Each Phase**

- [ ] **Requirements clearly defined** - What exactly will be built
- [ ] **Success criteria established** - How to know when phase is complete
- [ ] **Test strategy planned** - How functionality will be validated
- [ ] **Risk assessment completed** - What could go wrong and mitigation plans
- [ ] **Resource allocation confirmed** - Time and effort estimates

### **Before Completing Each Phase**

- [ ] **All functionality implemented** - No missing features
- [ ] **Tests passing** - Unit, integration, and performance tests
- [ ] **Documentation updated** - Code comments, docstrings, user docs
- [ ] **Code review completed** - Peer review and approval
- [ ] **Performance validated** - No significant regressions
- [ ] **Backwards compatibility verified** - Existing workflows still work
- [ ] **User acceptance confirmed** - Stakeholder approval

### **Before Final Migration**

- [ ] **Full test suite passing** - All tests green
- [ ] **Performance benchmarks met** - System performs as well or better
- [ ] **Documentation complete** - Users can successfully migrate
- [ ] **Migration tooling tested** - Automated migration works
- [ ] **Rollback plan ready** - Can revert if issues discovered
- [ ] **Monitoring in place** - Can detect issues after migration
- [ ] **Support plan ready** - Help users with migration issues

---

## Success Metrics & KPIs

### **Technical Quality Metrics**

- **Test Coverage**: 85%+ overall, 95%+ core modules
- **Type Coverage**: 100% type hints
- **Documentation Coverage**: 100% public APIs documented
- **Code Complexity**: Maximum cyclomatic complexity of 10
- **Performance**: No more than 5% regression in scraping speed
- **Error Rate**: Less than 1% unhandled exceptions

### **User Experience Metrics**

- **Setup Time**: New users productive in under 5 minutes
- **Command Discoverability**: All major functions accessible via help
- **Error Recovery**: 95% of errors provide actionable guidance
- **Learning Curve**: Experienced users can migrate in under 30 minutes

### **Maintainability Metrics**

- **Module Coupling**: Low coupling between modules
- **Code Duplication**: Less than 5% duplicate code
- **Dependency Health**: All dependencies current and secure
- **Build Time**: Full test suite completes in under 5 minutes
- **Deployment Simplicity**: Single command deployment
````
