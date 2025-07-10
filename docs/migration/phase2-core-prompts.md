# Phase 2 Core: Prompt Templates

_Ready-to-use prompts for scraper consolidation and CLI command implementation_

## 🎯 Phase 2 Overview

**Goal:** Consolidate scrapers and implement core CLI commands with functional
equivalence  
**Standards:** 70% test coverage minimum, functional equivalence to
enhanced_qb_scraper.py  
**Success Criteria:** Core scraping workflows work through CLI, performance
within 10% of legacy

---

## 📋 Essential Context Template

## Always include this context in Phase 2 prompts:

````text
## Context Files:
@.cursorrules
@.cursor/rules/migration-process.mdc
@.cursor/rules/python-quality.mdc
@.cursor/rules/testing-standards.mdc

**Current Phase:** Phase 2 (Core)
**Standards:** 70% test coverage minimum, functional equivalence required
**Legacy Scripts:** @scripts/enhanced_qb_scraper.py @scripts/robust_qb_scraper.py @scripts/nfl_qb_scraper.py
**Constraints:** Maintain backwards compatibility, performance within 10% of legacy
```text
---

## 🔄 1. Scraper Consolidation

### Template A: Legacy Script Analysis and Consolidation

```text
[Legacy-Script-Analysis-Phase2] Analyze and consolidate specific legacy scripts into unified CoreScraper.

## Context Files:
@.cursorrules
@.cursor/rules/migration-process.mdc
@.cursor/rules/python-quality.mdc
@scripts/enhanced_qb_scraper.py
@scripts/robust_qb_scraper.py
@scripts/scrape_qb_data_2024.py
@src/scrapers/enhanced_scraper.py
@src/scrapers/nfl_qb_scraper.py
@src/scrapers/raw_data_scraper.py

**Current Phase:** Phase 2 (Core)
**Standards:** 70% test coverage minimum, functional equivalence required

## Objective:
Systematically analyze and consolidate all legacy scraping scripts into a unified CoreScraper class.

## Legacy Script Analysis:
1. **scripts/enhanced_qb_scraper.py** - PRIMARY REFERENCE
   - Most feature-complete production scraper
   - Best data extraction patterns
   - Comprehensive field mapping
   - Use as base implementation

2. **scripts/robust_qb_scraper.py** - ERROR HANDLING PATTERNS
   - Superior error handling and retry logic
   - Network failure recovery
   - Graceful degradation patterns
   - Integrate error handling approach

3. **scripts/scrape_qb_data_2024.py** - ALTERNATIVE APPROACHES
   - Different scraping strategies
   - Alternative data processing methods
   - Unique features to preserve
   - Evaluate for best practices

4. **src/scrapers/enhanced_scraper.py** - LIBRARY PATTERNS
   - Modular design patterns
   - Class-based architecture
   - Existing abstractions
   - Integrate structural patterns

5. **src/scrapers/nfl_qb_scraper.py** - BASE FUNCTIONALITY
   - Core scraping logic
   - Basic patterns and utilities
   - Foundational methods
   - Preserve essential functionality

6. **src/scrapers/raw_data_scraper.py** - RAW DATA FOCUS
   - Raw data extraction methods
   - Data cleaning patterns
   - Specialized processing
   - Integrate data handling

## Consolidation Strategy:
- Start with enhanced_qb_scraper.py as the foundation
- Layer in robust error handling from robust_qb_scraper.py
- Preserve unique features from scrape_qb_data_2024.py
- Adopt modular patterns from enhanced_scraper.py
- Maintain compatibility with nfl_qb_scraper.py interfaces
- Integrate specialized processing from raw_data_scraper.py

## Migration Mapping:
```text
scripts/enhanced_qb_scraper.py → pfr-scraper scrape season --profile enhanced
scripts/robust_qb_scraper.py → pfr-scraper scrape season --robust-mode
scripts/scrape_qb_data_2024.py → pfr-scraper scrape season --year 2024
src/scrapers/enhanced_scraper.py → CoreScraper class patterns
src/scrapers/nfl_qb_scraper.py → CoreScraper base methods
src/scrapers/raw_data_scraper.py → CoreScraper data processing

```text
## Validation Requirements:
- Functional equivalence testing against each legacy script
- Performance benchmarking (within 10% of best performer)
- Feature parity checklist for each script's unique capabilities
- Error handling improvement validation
- Integration testing with existing database schema
```text
### Template B: Core Scraper Architecture

````

[Core-Scraper-Architecture-Phase2] Create unified CoreScraper that consolidates
all existing scrapers.

## Context Files:

@.cursorrules @.cursor/rules/migration-process.mdc
@.cursor/rules/python-quality.mdc @scripts/enhanced_qb_scraper.py
@scripts/robust_qb_scraper.py @scripts/nfl_qb_scraper.py

**Current Phase:** Phase 2 (Core) **Standards:** 70% test coverage minimum,
functional equivalence required

## Objective:

Consolidate multiple scrapers into a unified CoreScraper class that combines the
best features of each.

## Analysis Required:

1. **enhanced_qb_scraper.py:** Most feature-complete, best data extraction
2. **robust_qb_scraper.py:** Superior error handling and retry logic
3. **nfl_qb_scraper.py:** Original implementation patterns

## Consolidation Strategy:

- Use enhanced_qb_scraper.py as the base implementation
- Integrate robust error handling from robust_qb_scraper.py
- Preserve any unique features from nfl_qb_scraper.py
- Modernize code to follow current project standards

## Implementation Requirements:

1. Create src/core/scraper.py with CoreScraper class
2. Implement proper rate limiting (2.0s production, 0.01s testing)
3. Add comprehensive error handling with user-friendly messages
4. Use new configuration system from Phase 1
5. Implement proper logging with structured context
6. Add progress tracking for long operations

## CoreScraper Interface:

```python
class CoreScraper:
    def __init__(self, config: ScrapingConfig):
        self.config = config
        self.session = self._create_session()
        self.rate_limiter = RateLimiter(config.rate_limit)

    def scrape_player_season(self, player_name: str, season: int) -> PlayerSeasonData:
        """Scrape complete season data for a player."""
        pass

    def scrape_season_qbs(self, season: int) -> List[PlayerSeasonData]:
        """Scrape all QBs for a given season."""
        pass

    def scrape_team_qbs(self, team_code: str, season: int) -> List[PlayerSeasonData]:
        """Scrape all QBs for a team in a season."""
        pass
```

## Quality Requirements:

- All methods must have comprehensive docstrings
- Type hints for all parameters and return values
- Proper error handling with specific exception types
- Logging at appropriate levels with context
- Performance monitoring and metrics collection

## Testing Strategy:

- Unit tests for each scraping method
- Integration tests with mock HTTP responses
- Performance benchmarks against legacy scrapers
- Equivalence tests using known good data (Joe Burrow 2024)
- Error handling tests for network failures and invalid data

## Backwards Compatibility:

- Keep all existing scrapers functional during Phase 2
- Create facade interfaces if needed for legacy compatibility
- Document mapping from old methods to new CoreScraper methods

````text
### Template C: Scraper Equivalence Testing
```text
[Scraper-Equivalence-Testing-Phase2] Create comprehensive equivalence tests
between new CoreScraper and legacy scrapers.

**Context Files:** @.cursorrules @.cursor/rules/testing-standards.mdc
@scripts/enhanced_qb_scraper.py @src/core/scraper.py

**Current Phase:** Phase 2 (Core) **Standards:** 70% test coverage minimum,
functional equivalence required

**Objective:** Validate that the new CoreScraper produces identical results to
the legacy enhanced_qb_scraper.py.

## Test Data Strategy:

- Use known good data: Joe Burrow 2024 season
- Include edge cases: multi-team players (Tim Boyle 2024)
- Test various scenarios: different teams, seasons, data completeness
- Include error scenarios: invalid players, missing data

## Equivalence Test Categories:

1. **Data Completeness:** All expected fields are present
2. **Data Accuracy:** Values match exactly between implementations
3. **Data Format:** Consistent data types and formats
4. **Error Handling:** Same error responses for invalid inputs
5. **Performance:** Response times within 10% of legacy

## Implementation:

```python
def test_player_season_equivalence():
    """Test that CoreScraper produces identical results to legacy scraper."""
    # Test data
    player_name = "Joe Burrow"
    season = 2024

    # Legacy scraper
    legacy_data = enhanced_qb_scraper.scrape_player_season(player_name, season)

    # New CoreScraper
    core_scraper = CoreScraper(config)
    new_data = core_scraper.scrape_player_season(player_name, season)

    # Equivalence assertions
    assert_data_equivalent(legacy_data, new_data)
    assert_performance_equivalent(legacy_time, new_time)
    assert_error_handling_equivalent(legacy_errors, new_errors)

def assert_data_equivalent(legacy_data, new_data):
    """Assert that data from both scrapers is equivalent."""
    # Compare all fields
    assert legacy_data.player_name == new_data.player_name
    assert legacy_data.season == new_data.season
    assert legacy_data.games_played == new_data.games_played
    # ... compare all fields

    # Compare computed fields
    assert abs(legacy_data.passer_rating - new_data.passer_rating) < 0.01
    assert abs(legacy_data.completion_pct - new_data.completion_pct) < 0.01
```text
## Test Scenarios:

- **Happy Path:** Standard player data scraping
- **Edge Cases:** Multi-team players, missing data, unusual names
- **Error Cases:** Invalid players, network failures, malformed data
- **Performance:** Large datasets, concurrent requests
- **Boundary Conditions:** First/last games, season boundaries

## Validation Reports:

- Generate detailed comparison reports
- Highlight any differences found
- Performance benchmark comparisons
- Coverage analysis of test scenarios
- Automated pass/fail criteria

## Success Criteria:

- 100% data equivalence for test scenarios
- Performance within 10% of legacy scraper
- All error scenarios handled consistently
- No regressions in functionality
- All edge cases covered

```text
### Template C: Rate Limiting and Error Handling
```text
[Rate-Limiting-Error-Handling-Phase2] Implement production-grade rate limiting
and error handling.

**Context Files:** @.cursorrules @.cursor/rules/python-quality.mdc
@scripts/robust_qb_scraper.py

**Current Phase:** Phase 2 (Core) **Standards:** 70% test coverage minimum,
robust error handling required

**Objective:** Implement sophisticated rate limiting and error handling that
respects PFR's servers and provides excellent user experience.

## Rate Limiting Requirements:

1. **Production:** 2.0 seconds between requests minimum
2. **Testing:** 0.01 seconds for fast test execution
3. **Adaptive:** Increase delays if rate limiting detected
4. **Respectful:** Honor robots.txt and HTTP response codes

## Error Handling Categories:

1. **Network Errors:** Connection timeouts, DNS failures
2. **HTTP Errors:** 4xx client errors, 5xx server errors
3. **Data Errors:** Missing elements, malformed HTML
4. **Rate Limiting:** 429 responses, temporary blocks
5. **System Errors:** Database connection failures, file system errors

## Implementation:

```python
class RateLimiter:
    def __init__(self, base_delay: float = 2.0):
        self.base_delay = base_delay
        self.last_request_time = 0
        self.adaptive_delay = base_delay
        self.consecutive_errors = 0

    def wait_if_needed(self):
        """Wait if necessary to respect rate limits."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.adaptive_delay:
            time.sleep(self.adaptive_delay - elapsed)
        self.last_request_time = time.time()

    def handle_rate_limit_response(self, response):
        """Adjust delays based on rate limiting signals."""
        if response.status_code == 429:
            self.adaptive_delay = min(self.adaptive_delay * 2, 30.0)
            self.consecutive_errors += 1
        else:
            self.consecutive_errors = 0
            self.adaptive_delay = max(self.adaptive_delay * 0.9, self.base_delay)

class ErrorHandler:
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self.retry_delays = [1, 2, 4]  # Exponential backoff

    def handle_request_error(self, error: Exception, attempt: int) -> bool:
        """Handle request errors with appropriate retry logic."""
        if attempt >= self.max_retries:
            return False

        if isinstance(error, requests.exceptions.ConnectionError):
            # Network issues - retry with exponential backoff
            time.sleep(self.retry_delays[attempt])
            return True
        elif isinstance(error, requests.exceptions.Timeout):
            # Timeout - retry with longer delay
            time.sleep(self.retry_delays[attempt] * 2)
            return True
        elif isinstance(error, requests.exceptions.HTTPError):
            # HTTP errors - check status code
            if error.response.status_code >= 500:
                # Server errors - retry
                time.sleep(self.retry_delays[attempt])
                return True
            else:
                # Client errors - don't retry
                return False
        else:
            # Unknown error - don't retry
            return False
```text
## User-Friendly Error Messages:

- Never show technical stack traces
- Provide actionable suggestions
- Include context about what was being attempted
- Suggest fixes for common issues
- Log detailed information for debugging

## Testing:

- Unit tests for rate limiting logic
- Integration tests with mock HTTP responses
- Error scenario tests with various failure modes
- Performance tests for rate limiting overhead
- User experience tests for error messages

```text
### Template D: Setup Scripts Migration
```text
[Setup-Scripts-Migration-Phase2] Migrate setup and maintenance scripts to
unified setup operations.

**Context Files:** @.cursorrules @.cursor/rules/migration-process.mdc
@scripts/populate_teams.py @scripts/add_multi_team_codes.py
@scripts/modify_teams_schema_for_multi_team.py
@setup/deploy_schema_to_supabase.py

**Current Phase:** Phase 2 (Core)

**Objective:** Consolidate all setup and maintenance scripts into a unified
setup command structure.

## Setup Scripts Analysis:

1. **scripts/populate_teams.py** - TEAM DATA SETUP
   - Team reference data initialization
   - Official NFL team codes
   - Multi-team code support
   - Migrate to: `pfr-scraper setup teams`

2. **scripts/add_multi_team_codes.py** - MULTI-TEAM SUPPORT
   - 2TM/3TM team code handling
   - Multi-team player support
   - Database schema updates
   - Migrate to: `pfr-scraper setup teams --include-multi-team`

3. **scripts/modify_teams_schema_for_multi_team.py** - SCHEMA UPDATES
   - Database schema modifications
   - Multi-team table updates
   - Data migration procedures
   - Migrate to: `pfr-scraper setup schema --multi-team`

4. **setup/deploy_schema_to_supabase.py** - SCHEMA DEPLOYMENT
   - Database schema deployment
   - Supabase-specific operations
   - Schema validation
   - Migrate to: `pfr-scraper setup schema --deploy`

## Setup Command Structure:

```bash
# Consolidated setup commands
pfr-scraper setup all                     # Full setup process
pfr-scraper setup schema --deploy         # Deploy database schema
pfr-scraper setup teams --include-multi-team  # Setup team data
pfr-scraper setup status                  # Check setup status
pfr-scraper setup validate                # Validate setup
```text
## Implementation Requirements:

- Create src/operations/setup_ops.py with SetupOperations class
- Implement each setup operation as a method
- Add proper error handling and validation
- Include progress tracking for long operations
- Support dry-run mode for all operations

## Migration Mapping:

```text
scripts/populate_teams.py → SetupOperations.setup_teams()
scripts/add_multi_team_codes.py → SetupOperations.setup_multi_team_codes()
scripts/modify_teams_schema_for_multi_team.py → SetupOperations.update_schema_multi_team()
setup/deploy_schema_to_supabase.py → SetupOperations.deploy_schema()
```text
## Testing Requirements:

- Unit tests for each setup operation
- Integration tests with test database
- Schema validation tests
- Error handling tests for setup failures
- Rollback testing for failed operations

```text
### Template E: Data Management Scripts Migration
```text
[Data-Management-Scripts-Migration-Phase2] Migrate data management scripts to
unified data operations.

**Context Files:** @.cursorrules @.cursor/rules/migration-process.mdc
@scripts/clear_qb_data.py @scripts/update_qb_stats_team_codes.py
@scripts/update_teams_to_pfr_codes.py

**Current Phase:** Phase 2 (Core)

**Objective:** Consolidate all data management and maintenance scripts into
unified data command structure.

## Data Management Scripts Analysis:

1. **scripts/clear_qb_data.py** - DATA CLEANUP
   - QB data deletion by season
   - Selective data clearing
   - Confirmation prompts
   - Migrate to: `pfr-scraper data clear --season 2024 --confirm`

2. **scripts/update_qb_stats_team_codes.py** - DATA FIXES
   - Team code corrections
   - Data integrity repairs
   - Batch updates
   - Migrate to: `pfr-scraper data fix team-codes --season 2024`

3. **scripts/update_teams_to_pfr_codes.py** - CODE UPDATES
   - Team code standardization
   - PFR code mapping
   - Data migration
   - Migrate to: `pfr-scraper data update team-codes --to-pfr`

## Data Command Structure:

```bash
# Consolidated data commands
pfr-scraper data clear --season 2024 --confirm
pfr-scraper data fix team-codes --season 2024
pfr-scraper data update team-codes --to-pfr
pfr-scraper data validate --season 2024 --fix-errors
pfr-scraper data export --format csv --season 2024
```text
## Implementation Requirements:

- Create src/operations/data_ops.py with DataOperations class
- Implement each data operation as a method
- Add comprehensive validation before destructive operations
- Include progress tracking and confirmation prompts
- Support dry-run mode for all operations

## Migration Mapping:

```text
scripts/clear_qb_data.py → DataOperations.clear_qb_data()
scripts/update_qb_stats_team_codes.py → DataOperations.fix_team_codes()
scripts/update_teams_to_pfr_codes.py → DataOperations.update_team_codes()
```text
## Safety Requirements:

- Confirmation prompts for destructive operations
- Backup creation before major changes
- Rollback capabilities for failed operations
- Comprehensive logging of all changes
- Validation of changes before and after operations

```text
### Template F: Debug Scripts Migration
```text
[Debug-Scripts-Migration-Phase2] Migrate debug scripts to unified debug
operations.

**Context Files:** @.cursorrules @.cursor/rules/migration-process.mdc @debug/

**Current Phase:** Phase 2 (Core)

**Objective:** Consolidate debug scripts into unified debug command structure
for troubleshooting and validation.

## Debug Scripts Analysis:

```text
debug/ directory contains 8+ scripts:
- check_2024_tables.py → pfr-scraper debug tables --season 2024
- debug_splits_page.py → pfr-scraper debug splits --url URL
- debug_joe_burrow_2024.py → pfr-scraper debug player "Joe Burrow" --season 2024
- debug_name_matching.py → pfr-scraper debug names --validate
- test_single_player_data.py → pfr-scraper debug player-data --player NAME
- Various other debugging utilities
```text
## Debug Command Structure:

```bash
# Consolidated debug commands
pfr-scraper debug connection                    # Test database connection
pfr-scraper debug player "Joe Burrow" --season 2024  # Debug specific player
pfr-scraper debug fields --url "https://..."   # Debug field mappings
pfr-scraper debug tables --season 2024         # Debug table structure
pfr-scraper debug splits --url URL             # Debug splits page
pfr-scraper debug names --validate             # Debug name matching
```text
## Implementation Requirements:

- Create src/operations/debug_ops.py with DebugOperations class
- Implement each debug operation as a method
- Add detailed diagnostic output
- Include performance timing information
- Support verbose mode for detailed debugging

## Migration Mapping:

```text
debug/check_2024_tables.py → DebugOperations.check_tables()
debug/debug_joe_burrow_2024.py → DebugOperations.debug_player()
debug/debug_name_matching.py → DebugOperations.debug_names()
debug/test_single_player_data.py → DebugOperations.test_player_data()
# ... additional debug scripts
```text
## Testing Requirements:

- Unit tests for each debug operation
- Integration tests with real data
- Performance timing validation
- Error handling tests for debug scenarios
- Output format validation

```text
---

## 🛠️ 2. CLI Command Implementation

### Template A: Core CLI Commands
```text
[Core-CLI-Commands-Phase2] Implement core CLI commands using the new
CoreScraper.

**Context Files:** @.cursorrules @.cursor/rules/cli-specific.mdc
@.cursor/rules/python-quality.mdc @src/core/scraper.py

**Current Phase:** Phase 2 (Core) **Standards:** 70% test coverage minimum,
excellent user experience

**Objective:** Implement the core CLI commands that provide the main scraping
functionality through an intuitive interface.

## Commands to Implement:

1. `pfr-scraper scrape player --name "Joe Burrow" --season 2024`
2. `pfr-scraper scrape season --year 2024 --position QB`
3. `pfr-scraper scrape team --team CIN --season 2024`
4. `pfr-scraper scrape url --url "https://www.pro-football-reference.com/players/..."`

## CLI Command Structure:

```python
class ScrapeCommand(BaseCommand):
    name = "scrape"
    description = "Scrape QB data from Pro Football Reference"

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest='scrape_type', required=True)

        # Player scraping
        player_parser = subparsers.add_parser('player', help='Scrape specific player')
        player_parser.add_argument('--name', required=True, help='Player name')
        player_parser.add_argument('--season', type=int, required=True, help='Season year')

        # Season scraping
        season_parser = subparsers.add_parser('season', help='Scrape all QBs for season')
        season_parser.add_argument('--year', type=int, required=True, help='Season year')
        season_parser.add_argument('--position', default='QB', help='Position to scrape')

        # Team scraping
        team_parser = subparsers.add_parser('team', help='Scrape team QBs')
        team_parser.add_argument('--team', required=True, help='Team code (e.g., CIN)')
        team_parser.add_argument('--season', type=int, required=True, help='Season year')

        # Common options
        for p in [player_parser, season_parser, team_parser]:
            p.add_argument('--output', choices=['table', 'json', 'csv'], default='table')
            p.add_argument('--save-to', help='Save results to file')
            p.add_argument('--dry-run', action='store_true', help='Show what would be scraped')

    def execute(self, args):
        """Execute the scrape command."""
        try:
            if args.scrape_type == 'player':
                return self._scrape_player(args)
            elif args.scrape_type == 'season':
                return self._scrape_season(args)
            elif args.scrape_type == 'team':
                return self._scrape_team(args)
        except Exception as e:
            self._handle_error(e)
            return 1
```text
## User Experience Features:

- Progress bars for long operations
- Graceful cancellation with Ctrl+C
- Multiple output formats (table, JSON, CSV)
- Dry-run mode to preview operations
- Tab completion for player names (if possible)
- Helpful error messages with suggestions

## Business Logic Separation:

- CLI handlers only parse arguments and format output
- All scraping logic delegated to src/operations/scraping_ops.py
- Error handling provides user-friendly messages
- Logging includes operation context

## Testing:

- Integration tests with mock HTTP responses
- CLI argument parsing tests
- Error handling and validation tests
- Output format tests
- User experience tests

```text
### Template B: Output Formatting and User Experience
```text
[Output-Formatting-UX-Phase2] Implement beautiful output formatting and
excellent user experience.

**Context Files:** @.cursorrules @.cursor/rules/cli-specific.mdc

**Current Phase:** Phase 2 (Core)

**Objective:** Create beautiful, informative output that makes the CLI a joy to
use.

## Output Formats:

1. **Table:** Pretty-printed tables for terminal viewing
2. **JSON:** Structured data for programmatic use
3. **CSV:** Spreadsheet-compatible format

## Table Format Example:

```text
┌─────────────────┬────────┬──────┬───────┬────────┬─────────────┐
│ Player          │ Season │ Team │ Games │ Comp % │ Pass Rating │
├─────────────────┼────────┼──────┼───────┼────────┼─────────────┤
│ Joe Burrow      │ 2024   │ CIN  │ 17    │ 70.5   │ 107.8       │
│ Josh Allen      │ 2024   │ BUF  │ 17    │ 63.6   │ 101.4       │
│ Lamar Jackson   │ 2024   │ BAL  │ 17    │ 66.7   │ 112.7       │
└─────────────────┴────────┴──────┴───────┴────────┴─────────────┘
```text
## Progress Indication:

```python
class ProgressTracker:
    def __init__(self, total_items: int, description: str):
        self.total_items = total_items
        self.description = description
        self.current_item = 0
        self.start_time = time.time()

    def update(self, increment: int = 1):
        """Update progress and display current status."""
        self.current_item += increment
        elapsed = time.time() - self.start_time

        if self.current_item > 0:
            eta = (elapsed / self.current_item) * (self.total_items - self.current_item)
            eta_str = self._format_time(eta)
        else:
            eta_str = "calculating..."

        progress = self.current_item / self.total_items
        bar = self._create_progress_bar(progress)

        print(f"\r{self.description}: {bar} {self.current_item}/{self.total_items} ETA: {eta_str}", end='')

    def _create_progress_bar(self, progress: float, width: int = 30) -> str:
        """Create ASCII progress bar."""
        filled = int(width * progress)
        return f"[{'█' * filled}{'░' * (width - filled)}] {progress:.1%}"
```text
## User Experience Features:

- Colorized output for better readability
- Progress bars for operations > 5 seconds
- Estimated time remaining for long operations
- Graceful handling of Ctrl+C interruption
- Helpful error messages with suggestions
- Confirmation prompts for destructive operations

## Error Message Examples:

```text
Error: Player not found

Player: "Joe Burrows" (note the extra 's')
Season: 2024

Did you mean:
  • Joe Burrow (CIN)
  • Joe Flacco (IND)

Try: pfr-scraper scrape player --name "Joe Burrow" --season 2024
```text
## Implementation:

- Use rich library for beautiful terminal output
- Implement colorized output with proper fallbacks
- Add progress tracking for all long operations
- Create consistent error message formatting
- Add confirmation prompts for destructive operations

## Testing:

- Output format tests for all supported formats
- Progress bar tests with mock long operations
- Error message tests for common scenarios
- User experience tests for different terminal sizes
- Color output tests with various terminal settings

```text
### Template C: Operations Layer
```text
[Operations-Layer-Phase2] Create operations layer that bridges CLI and core
scraping logic.

**Context Files:** @.cursorrules @.cursor/rules/python-quality.mdc
@src/core/scraper.py

**Current Phase:** Phase 2 (Core)

**Objective:** Create a clean operations layer that handles high-level scraping
workflows and business logic.

## Operations Architecture:

```python
# src/operations/scraping_ops.py
class ScrapingOperations:
    def __init__(self, scraper: CoreScraper, db_manager: DatabaseManager):
        self.scraper = scraper
        self.db_manager = db_manager
        self.progress_callback = None

    def scrape_player_season(self, player_name: str, season: int,
                           save_to_db: bool = True) -> PlayerSeasonData:
        """High-level operation to scrape a player's season data."""
        # Validate inputs
        self._validate_player_name(player_name)
        self._validate_season(season)

        # Check if data already exists
        if save_to_db and self._data_exists(player_name, season):
            return self._load_from_db(player_name, season)

        # Scrape data
        data = self.scraper.scrape_player_season(player_name, season)

        # Save to database if requested
        if save_to_db:
            self.db_manager.save_player_season(data)

        return data

    def scrape_season_qbs(self, season: int, save_to_db: bool = True) -> List[PlayerSeasonData]:
        """High-level operation to scrape all QBs for a season."""
        # Get list of QBs for the season
        qb_list = self.scraper.get_season_qb_list(season)

        results = []
        for i, qb_name in enumerate(qb_list):
            if self.progress_callback:
                self.progress_callback(i + 1, len(qb_list), f"Scraping {qb_name}")

            try:
                data = self.scrape_player_season(qb_name, season, save_to_db)
                results.append(data)
            except Exception as e:
                logger.error(f"Failed to scrape {qb_name}: {e}")
                continue

        return results
```text
## Workflow Management:

- Handle multi-step operations with proper error recovery
- Implement resumable operations for long-running tasks
- Add transaction management for database operations
- Create rollback mechanisms for failed operations
- Support dry-run mode for all operations

## Data Management:

- Check for existing data before scraping
- Handle data conflicts and duplicates
- Implement data validation and quality checks
- Add data transformation and normalization
- Support batch operations for efficiency

## Error Handling:

- Translate technical errors to user-friendly messages
- Implement retry logic for transient failures
- Add context to error messages
- Support graceful degradation for partial failures
- Log detailed error information for debugging

## Testing:

- Unit tests for each operation method
- Integration tests with mock scrapers and databases
- Workflow tests for complex multi-step operations
- Error handling tests for various failure scenarios
- Performance tests for batch operations

```text
---

## 🧪 3. Testing and Validation

### Template A: Integration Testing
```text
[Integration-Testing-Phase2] Create comprehensive integration tests for Phase 2
components.

**Context Files:** @.cursorrules @.cursor/rules/testing-standards.mdc
@.cursor/rules/python-quality.mdc

**Current Phase:** Phase 2 (Core) **Coverage Requirement:** 70% minimum

**Objective:** Create integration tests that validate the complete workflow from
CLI commands through to data storage.

## Integration Test Categories:

1. **CLI to Operations:** Command parsing and execution
2. **Operations to Core:** High-level to low-level scraping
3. **Core to External:** HTTP requests and response handling
4. **End-to-End:** Complete user workflows

## Test Structure:

```python
class TestScrapingIntegration:
    def test_cli_player_scraping_workflow(self):
        """Test complete workflow from CLI command to data storage."""
        # Mock HTTP responses
        with mock_pfr_responses():
            # Execute CLI command
            result = run_cli(['scrape', 'player', '--name', 'Joe Burrow', '--season', '2024'])

            # Verify command executed successfully
            assert result.exit_code == 0
            assert 'Joe Burrow' in result.output
            assert '2024' in result.output

            # Verify data was saved to database
            db_data = db_manager.get_player_season('Joe Burrow', 2024)
            assert db_data is not None
            assert db_data.player_name == 'Joe Burrow'

    def test_error_handling_integration(self):
        """Test error handling across all layers."""
        # Mock network error
        with mock_network_error():
            result = run_cli(['scrape', 'player', '--name', 'Joe Burrow', '--season', '2024'])

            # Verify error was handled gracefully
            assert result.exit_code == 1
            assert 'network error' in result.output.lower()
            assert 'try again' in result.output.lower()

    def test_rate_limiting_integration(self):
        """Test rate limiting works across multiple requests."""
        start_time = time.time()

        # Make multiple requests
        for i in range(3):
            run_cli(['scrape', 'player', '--name', f'Player{i}', '--season', '2024'])

        # Verify rate limiting was applied
        elapsed = time.time() - start_time
        assert elapsed >= 4.0  # 2 seconds between requests
```text
## Mock Strategy:

- Mock HTTP requests at the session level
- Create realistic PFR response fixtures
- Mock database operations for isolation
- Use dependency injection for easy mocking
- Create reusable mock utilities

## Test Data Management:

- Create comprehensive test fixtures
- Use realistic but anonymized data
- Include edge cases and error scenarios
- Maintain test data consistency
- Support test data evolution

## Performance Testing:

- Measure response times for typical operations
- Test with realistic data volumes
- Validate rate limiting effectiveness
- Monitor memory usage during operations
- Benchmark against legacy performance

```text
### Template B: Performance and Benchmarking
```text
[Performance-Benchmarking-Phase2] Create performance tests and benchmarks for
Phase 2 components.

**Context Files:** @.cursorrules @.cursor/rules/testing-standards.mdc
@scripts/enhanced_qb_scraper.py

**Current Phase:** Phase 2 (Core) **Performance Target:** Within 10% of legacy
scraper performance

**Objective:** Validate that the new CoreScraper and CLI meet performance
requirements and don't introduce regressions.

## Performance Test Categories:

1. **Single Player Scraping:** Response time for individual player
2. **Batch Operations:** Performance with multiple players
3. **Season Scraping:** Time to scrape all QBs for a season
4. **Database Operations:** Data storage and retrieval speed
5. **Memory Usage:** Memory consumption during operations

## Benchmarking Implementation:

```python
class PerformanceBenchmarks:
    def __init__(self):
        self.legacy_scraper = enhanced_qb_scraper
        self.core_scraper = CoreScraper(config)
        self.benchmark_data = []

    def benchmark_single_player(self, player_name: str, season: int):
        """Benchmark single player scraping performance."""
        # Legacy scraper benchmark
        legacy_time = self._time_operation(
            lambda: self.legacy_scraper.scrape_player_season(player_name, season)
        )

        # New scraper benchmark
        new_time = self._time_operation(
            lambda: self.core_scraper.scrape_player_season(player_name, season)
        )

        # Calculate performance ratio
        ratio = new_time / legacy_time

        self.benchmark_data.append({
            'operation': 'single_player',
            'player': player_name,
            'season': season,
            'legacy_time': legacy_time,
            'new_time': new_time,
            'ratio': ratio,
            'acceptable': ratio <= 1.1  # Within 10%
        })

        return ratio

    def benchmark_batch_operations(self, player_list: List[str], season: int):
        """Benchmark batch scraping performance."""
        # Test with various batch sizes
        batch_sizes = [1, 5, 10, 20]

        for batch_size in batch_sizes:
            batch = player_list[:batch_size]

            # Legacy approach
            legacy_time = self._time_operation(
                lambda: [self.legacy_scraper.scrape_player_season(p, season) for p in batch]
            )

            # New approach
            new_time = self._time_operation(
                lambda: self.core_scraper.scrape_multiple_players(batch, season)
            )

            self.benchmark_data.append({
                'operation': 'batch_operation',
                'batch_size': batch_size,
                'legacy_time': legacy_time,
                'new_time': new_time,
                'ratio': new_time / legacy_time
            })

    def generate_performance_report(self) -> str:
        """Generate comprehensive performance report."""
        report = []
        report.append("Performance Benchmark Report")
        report.append("=" * 50)

        for data in self.benchmark_data:
            report.append(f"Operation: {data['operation']}")
            report.append(f"Legacy Time: {data['legacy_time']:.2f}s")
            report.append(f"New Time: {data['new_time']:.2f}s")
            report.append(f"Performance Ratio: {data['ratio']:.2f}")
            report.append(f"Acceptable: {'✓' if data['ratio'] <= 1.1 else '✗'}")
            report.append("")

        return "\n".join(report)
```text
## Memory Profiling:

- Monitor memory usage during operations
- Detect memory leaks in long-running operations
- Profile memory usage patterns
- Compare memory usage with legacy scrapers
- Optimize memory-intensive operations

## Load Testing:

- Test with realistic data volumes
- Simulate concurrent usage patterns
- Validate rate limiting under load
- Test database performance under load
- Monitor system resource usage

## Continuous Monitoring:

- Set up automated performance regression testing
- Track performance metrics over time
- Alert on performance degradation
- Maintain performance baselines
- Create performance dashboards

```text
---

## 📊 4. Data Management and Validation

### Template A: Data Quality Validation
```text
[Data-Quality-Validation-Phase2] Implement data quality validation for scraped
data.

**Context Files:** @.cursorrules @.cursor/rules/python-quality.mdc
@src/models/qb_models.py

**Current Phase:** Phase 2 (Core)

**Objective:** Ensure all scraped data meets quality standards before storage
and processing.

## Data Quality Categories:

1. **Completeness:** Required fields are present and populated
2. **Accuracy:** Data values are within expected ranges
3. **Consistency:** Data follows consistent formats and patterns
4. **Integrity:** Referential integrity is maintained
5. **Timeliness:** Data is current and relevant

## Validation Rules:

```python
class DataQualityValidator:
    def __init__(self):
        self.validation_rules = {
            'player_name': self._validate_player_name,
            'season': self._validate_season,
            'games_played': self._validate_games_played,
            'completion_percentage': self._validate_completion_percentage,
            'passer_rating': self._validate_passer_rating,
            'passing_yards': self._validate_passing_yards,
            'touchdowns': self._validate_touchdowns,
            'interceptions': self._validate_interceptions,
        }

    def validate_player_data(self, data: PlayerSeasonData) -> ValidationResult:
        """Validate a complete player season data record."""
        errors = []
        warnings = []

        for field, validator in self.validation_rules.items():
            try:
                result = validator(getattr(data, field))
                if result.level == 'error':
                    errors.append(result)
                elif result.level == 'warning':
                    warnings.append(result)
            except Exception as e:
                errors.append(ValidationError(
                    field=field,
                    message=f"Validation failed: {e}",
                    level='error'
                ))

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )

    def _validate_passer_rating(self, rating: Optional[float]) -> ValidationResult:
        """Validate passer rating is within NFL bounds."""
        if rating is None:
            return ValidationResult(level='warning', message="Passer rating is missing")

        if rating < 0.0 or rating > 158.3:
            return ValidationResult(
                level='error',
                message=f"Passer rating {rating} is outside valid range (0.0-158.3)"
            )

        return ValidationResult(level='ok')

    def _validate_completion_percentage(self, comp_pct: Optional[float]) -> ValidationResult:
        """Validate completion percentage is reasonable."""
        if comp_pct is None:
            return ValidationResult(level='warning', message="Completion percentage is missing")

        if comp_pct < 0.0 or comp_pct > 100.0:
            return ValidationResult(
                level='error',
                message=f"Completion percentage {comp_pct} is outside valid range (0.0-100.0)"
            )

        if comp_pct < 30.0:
            return ValidationResult(
                level='warning',
                message=f"Completion percentage {comp_pct} is unusually low"
            )

        return ValidationResult(level='ok')
```text
## Business Rule Validation:

- Completions cannot exceed attempts
- Games started cannot exceed games played
- Passing yards should be reasonable for games played
- Team codes must match official NFL codes
- Season years must be within valid range

## Data Cleaning:

- Normalize player names consistently
- Convert team codes to standard format
- Handle missing data appropriately
- Remove duplicate records
- Fix common data entry errors

## Validation Reporting:

- Generate detailed validation reports
- Show validation errors and warnings
- Provide suggestions for fixing issues
- Track validation metrics over time
- Create validation dashboards

```text
### Template B: Database Integration
```text
[Database-Integration-Phase2] Implement robust database integration for scraped
data.

**Context Files:** @.cursorrules @.cursor/rules/sql-standards.mdc
@src/database/db_manager.py

**Current Phase:** Phase 2 (Core)

**Objective:** Create robust database operations that handle data storage,
retrieval, and conflict resolution.

## Database Operations:

```python
class DatabaseOperations:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.validator = DataQualityValidator()

    def save_player_season(self, data: PlayerSeasonData,
                          validate: bool = True) -> SaveResult:
        """Save player season data with validation and conflict resolution."""
        # Validate data if requested
        if validate:
            validation_result = self.validator.validate_player_data(data)
            if not validation_result.valid:
                return SaveResult(
                    success=False,
                    errors=validation_result.errors,
                    message="Data validation failed"
                )

        # Check for existing data
        existing_data = self.db_manager.get_player_season(data.player_name, data.season)

        if existing_data:
            # Handle conflict resolution
            return self._handle_data_conflict(existing_data, data)
        else:
            # Insert new data
            return self._insert_new_data(data)

    def _handle_data_conflict(self, existing: PlayerSeasonData,
                             new: PlayerSeasonData) -> SaveResult:
        """Handle conflicts when data already exists."""
        # Compare data quality
        if self._is_data_better(new, existing):
            # Update with better data
            self.db_manager.update_player_season(new)
            return SaveResult(
                success=True,
                message="Updated with better data",
                action="update"
            )
        else:
            # Keep existing data
            return SaveResult(
                success=True,
                message="Kept existing data (better quality)",
                action="skip"
            )

    def _is_data_better(self, new_data: PlayerSeasonData,
                       existing_data: PlayerSeasonData) -> bool:
        """Determine if new data is better than existing data."""
        # Compare completeness
        new_completeness = self._calculate_completeness(new_data)
        existing_completeness = self._calculate_completeness(existing_data)

        if new_completeness > existing_completeness:
            return True
        elif new_completeness < existing_completeness:
            return False

        # Compare recency (newer scraping usually better)
        if new_data.last_updated > existing_data.last_updated:
            return True

        return False

    def batch_save_players(self, player_data_list: List[PlayerSeasonData]) -> BatchSaveResult:
        """Save multiple player records efficiently."""
        results = []

        # Use database transaction for batch operation
        with self.db_manager.transaction():
            for data in player_data_list:
                result = self.save_player_season(data)
                results.append(result)

                # Stop on critical errors
                if result.has_critical_error:
                    raise DatabaseError(f"Critical error saving {data.player_name}: {result.message}")

        return BatchSaveResult(
            total_records=len(player_data_list),
            successful_saves=len([r for r in results if r.success]),
            failed_saves=len([r for r in results if not r.success]),
            results=results
        )
```text
## Transaction Management:

- Use database transactions for multi-step operations
- Implement rollback on errors
- Handle concurrent access properly
- Use connection pooling for performance
- Clean up resources automatically

## Performance Optimization:

- Use bulk operations for multiple records
- Implement proper indexing strategy
- Use parameterized queries for security
- Cache frequently accessed data
- Monitor query performance

## Error Handling:

- Handle database connection failures
- Retry transient errors with exponential backoff
- Log detailed error information
- Provide user-friendly error messages
- Implement circuit breaker patterns

## Testing:

- Unit tests for database operations
- Integration tests with real database
- Transaction tests for error scenarios
- Performance tests for bulk operations
- Data integrity tests

```text
---

## 🚀 Phase 2 Completion Validation

### Final Phase 2 Validation Prompt
```text
[Phase2-Completion-Validation] Validate that Phase 2 Core is complete and ready
for Phase 3.

**Context Files:** @.cursorrules @.cursor/rules/migration-process.mdc
@.cursor/rules/testing-standards.mdc

**Current Phase:** Phase 2 (Core) - Completion Validation

**Objective:** Comprehensive validation that all Phase 2 requirements are met
and core functionality is solid for Phase 3.

## Validation Checklist:

- [ ] CoreScraper consolidates all legacy scraper functionality
- [ ] CLI commands provide intuitive interface for core operations
- [ ] Performance is within 10% of legacy scrapers
- [ ] Data quality validation is comprehensive
- [ ] Database integration is robust and efficient
- [ ] Test coverage meets 70% minimum requirement
- [ ] All backwards compatibility is maintained
- [ ] User experience is excellent

## Functional Validation:

1. **Scraping Equivalence:**
   - CoreScraper produces identical results to enhanced_qb_scraper.py
   - All edge cases handled properly (multi-team players, missing data)
   - Error handling is robust and user-friendly
   - Rate limiting respects PFR servers

2. **CLI Functionality:**
   - All core commands work intuitively
   - Help system is comprehensive and helpful
   - Output formatting is beautiful and informative
   - Error messages are actionable and clear

3. **Data Management:**
   - Data validation catches all quality issues
   - Database operations are efficient and safe
   - Conflict resolution works properly
   - Batch operations perform well

## Performance Validation:

- Single player scraping within 10% of legacy performance
- Batch operations scale properly
- Memory usage is reasonable for large datasets
- Database operations are optimized
- Rate limiting doesn't significantly impact performance

## Quality Validation:

- Test coverage meets 70% minimum requirement
- All code passes linting and type checking
- Error handling is comprehensive
- Documentation is complete and accurate
- Code quality meets project standards

## User Experience Validation:

- CLI is intuitive for existing users
- Help system guides new users effectively
- Error messages are helpful and actionable
- Progress indication works for long operations
- Output formatting is clear and informative

## Phase 3 Readiness:

- Foundation supports advanced data operations
- Architecture can handle complex multi-team scenarios
- Performance is adequate for large-scale operations
- Code quality supports advanced features
- Team is confident in core functionality

## Sign-off Requirements:

- All validation tests pass
- Performance benchmarks meet targets
- User acceptance testing is positive
- Code review approves architecture
- Documentation is complete and tested

````

---

## 💡 Quick Reference

### Phase 2 Testing Commands

```bash
# Run Phase 2 tests
pytest tests/phase2/ -v

# Run equivalence tests
pytest tests/equivalence/ -v

# Run performance benchmarks
pytest tests/performance/ --benchmark-only

# Check test coverage
pytest --cov=src --cov-report=html tests/

# Run CLI integration tests
pytest tests/cli/ -v
```

### Phase 2 CLI Commands

````bash
# Test core scraping commands
python -m pfr_scraper scrape player --name "Joe Burrow" --season 2024
python -m pfr_scraper scrape season --year 2024
python -m pfr_scraper scrape team --team CIN --season 2024

# Test output formats
python -m pfr_scraper scrape player --name "Joe Burrow" --season 2024 --output json
python -m pfr_scraper scrape player --name "Joe Burrow" --season 2024 --output csv
```text
### Next Steps

Once Phase 2 is complete, move to
[Phase 3 Advanced Prompts](phase3-advanced-prompts.md) for advanced data
management and validation features.
````
