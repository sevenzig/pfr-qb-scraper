# NFL QB Scraper Migration Plan

## From Script Sprawl to Modular CLI Architecture

### Current State Analysis

#### Existing Scripts Audit

## Core Scrapers (3 different approaches - CONSOLIDATE)

- `scripts/enhanced_qb_scraper.py` - Main production scraper
- `scripts/scrape_qb_data_2024.py` - Alternative scraper
- `scripts/robust_qb_scraper.py` - Another alternative
- `src/scrapers/enhanced_scraper.py` - Library version
- `src/scrapers/nfl_qb_scraper.py` - Base scraper
- `src/scrapers/raw_data_scraper.py` - Raw data focus

## Setup/Maintenance Scripts (ORGANIZE INTO SETUP MODULE)

- `scripts/populate_teams.py` - Team data setup
- `scripts/add_multi_team_codes.py` - Multi-team support
- `scripts/modify_teams_schema_for_multi_team.py` - Schema updates
- `setup/deploy_schema_to_supabase.py` - Schema deployment

## Data Management Scripts (CONSOLIDATE INTO DATA MODULE)

- `scripts/clear_qb_data.py` - Data cleanup
- `scripts/update_qb_stats_team_codes.py` - Data fixes
- `scripts/update_teams_to_pfr_codes.py` - Code updates

## Debug Scripts (MOVE TO DEBUG MODULE)

- `debug/` directory with 8+ scripts - Various debugging tools

#### Problems Identified

1. **No single entry point** - Users don't know which script to run
2. **Duplicate functionality** - 3+ scrapers doing similar things
3. **Scattered setup** - Setup operations spread across multiple scripts
4. **No workflow orchestration** - Manual execution of multiple steps
5. **Inconsistent error handling** - Each script has different patterns
6. **Hard to test** - No modular structure for unit testing

---

## Migration Strategy Overview

### Phase 1: Foundation (Week 1)

**Goal**: Create new CLI structure without breaking existing functionality

1. **Create CLI Foundation**
   - New entry point: `src/cli/main.py`
   - Command structure: `python -m pfr_scraper [command] [subcommand] [options]`
   - Help system and argument parsing

2. **Modular Core Architecture**
   - `src/core/` - Core business logic (scraping, validation, aggregation)
   - `src/operations/` - High-level operations (setup, data management)
   - `src/cli/commands/` - CLI command handlers

### Phase 2: Core Migration (Week 2)

**Goal**: Migrate and consolidate core scraping functionality

1. **Consolidate Scrapers**
   - Single `CoreScraper` class combining best features
   - Unified configuration system
   - Standardized error handling and logging

2. **Setup Operations**
   - Migrate all setup scripts to `setup` command
   - Database schema management
   - Team data initialization

### Phase 3: Data Management (Week 3)

**Goal**: Unified data operations and validation

1. **Data Operations**
   - Consolidate data management scripts
   - Add data validation and quality checks
   - Implement aggregation logic for multi-team players

2. **Testing Infrastructure**
   - Unit tests for core modules
   - Integration tests for CLI commands
   - Test data fixtures

### Phase 4: Polish & Deprecation (Week 4)

**Goal**: Production-ready CLI and deprecate old scripts

1. **Production Features**
   - Comprehensive logging and monitoring
   - Configuration management
   - Performance optimization

2. **Migration Completion**
   - Move old scripts to `legacy/` directory
   - Update documentation
   - User migration guide

---

## New Project Structure

````text
pfr-qb-scraper/
├── src/
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── main.py                    # Main CLI entry point
│   │   ├── commands/
│   │   │   ├── __init__.py
│   │   │   ├── scrape.py              # python -m pfr_scraper scrape
│   │   │   ├── setup.py               # python -m pfr_scraper setup
│   │   │   ├── data.py                # python -m pfr_scraper data
│   │   │   └── debug.py               # python -m pfr_scraper debug
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── cli_utils.py           # CLI utilities
│   │       └── validation.py          # Input validation
│   ├── core/
│   │   ├── __init__.py
│   │   ├── scraper.py                 # Unified scraper class
│   │   ├── aggregator.py              # Multi-team aggregation
│   │   ├── validator.py               # Data validation
│   │   └── processor.py               # Data processing pipeline
│   ├── operations/
│   │   ├── __init__.py
│   │   ├── setup_ops.py               # Database/schema setup
│   │   ├── data_ops.py                # Data management operations
│   │   ├── scraping_ops.py            # High-level scraping operations
│   │   └── maintenance_ops.py         # Cleanup and maintenance
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py                # Configuration management
│   │   └── defaults.py                # Default configurations
│   ├── database/
│   │   ├── __init__.py
│   │   ├── db_manager.py              # Keep existing
│   │   ├── schema_manager.py          # Schema operations
│   │   └── migrations.py              # Database migrations
│   ├── models/
│   │   ├── __init__.py
│   │   ├── qb_models.py               # Keep existing, enhance
│   │   └── config_models.py           # Configuration models
│   └── utils/
│       ├── __init__.py
│       ├── data_utils.py              # Keep existing
│       ├── logging_utils.py           # Standardized logging
│       └── error_handling.py          # Common error patterns
├── tests/
│   ├── __init__.py
│   ├── unit/
│   │   ├── test_core/
│   │   ├── test_operations/
│   │   └── test_utils/
│   ├── integration/
│   │   ├── test_cli/
│   │   └── test_database/
│   └── fixtures/
│       ├── test_data/
│       └── mock_responses/
├── legacy/
│   └── scripts/                       # Move old scripts here
├── config/
│   ├── cli_config.yaml               # CLI configuration
│   └── scraping_profiles.yaml        # Different scraping profiles
└── docs/
    ├── CLI_USAGE.md                  # New CLI documentation
    ├── MIGRATION_GUIDE.md            # User migration guide
    └── DEVELOPMENT.md                # Development guidelines
```text
---

## Command Structure Design

### `python -m pfr_scraper scrape`

```bash
# Full season scraping
python -m pfr_scraper scrape season 2024 --profile full

# Specific players
python -m pfr_scraper scrape players --names "Joe Burrow,Josh Allen" --season 2024

# Splits only
python -m pfr_scraper scrape splits --season 2024 --split-types basic,advanced

# Resume failed scraping
python -m pfr_scraper scrape resume --session-id abc123
```text
### `python -m pfr_scraper setup`

```bash
# Full setup
python -m pfr_scraper setup all

# Database schema only
python -m pfr_scraper setup schema --deploy

# Teams data
python -m pfr_scraper setup teams --include-multi-team

# Check setup status
python -m pfr_scraper setup status
```text
### `python -m pfr_scraper data`

```bash
# Clear data
python -m pfr_scraper data clear --season 2024 --confirm

# Validate data quality
python -m pfr_scraper data validate --season 2024 --fix-errors

# Aggregate multi-team players
python -m pfr_scraper data aggregate --season 2024 --prefer-combined

# Export data
python -m pfr_scraper data export --format csv --season 2024
```text
### `python -m pfr_scraper debug`

```bash
# Test connection
python -m pfr_scraper debug connection

# Validate specific player data
python -m pfr_scraper debug player "Joe Burrow" --season 2024

# Check field mappings
python -m pfr_scraper debug fields --url "https://pro-football-reference.com/..."
```text
---

## Migration Implementation Steps

### Step 1: CLI Foundation Setup

1. Create `src/cli/main.py` with argument parsing
2. Implement basic command routing
3. Add help system and version info
4. Create command base classes

### Step 2: Core Module Migration

1. Create `CoreScraper` class combining best features from existing scrapers
2. Migrate configuration management to `src/config/`
3. Standardize logging across all modules
4. Create unified error handling

### Step 3: Operations Layer

1. Migrate setup scripts to `SetupOperations` class
2. Migrate data management to `DataOperations` class
3. Create `ScrapingOperations` for high-level workflows
4. Add progress tracking and session management

### Step 4: Testing & Quality Assurance

1. Create test fixtures from existing debug scripts
2. Implement unit tests for core modules
3. Create integration tests for CLI commands
4. Performance testing and optimization

### Step 5: Documentation & Migration

1. Create comprehensive CLI documentation
2. Write user migration guide
3. Update README with new usage patterns
4. Create development guidelines

---

## Backwards Compatibility Strategy

### Transition Period (Phases 1-3)

- **Keep old scripts functional** - Don't break existing workflows
- **Add deprecation warnings** - Warn users about upcoming changes
- **Provide migration commands** - Help users transition

### Deprecation Phase (Phase 4)

- **Move scripts to `legacy/`** - Still available but clearly deprecated
- **Update all documentation** - Point to new CLI
- **Provide wrapper scripts** - For critical legacy workflows

### Post-Migration

- **Remove legacy code** - After 1-2 months of stable new CLI
- **Archive old documentation** - Keep for reference

---

## Success Metrics

### Quality Improvements

- [ ] **Single entry point** - One command to rule them all
- [ ] **90% test coverage** - Core modules fully tested
- [ ] **Consistent error handling** - Standardized across all operations
- [ ] **Comprehensive logging** - Clear operational visibility

### User Experience

- [ ] **5-minute setup** - New users can get started quickly
- [ ] **Self-documenting** - Built-in help and examples
- [ ] **Robust error recovery** - Graceful handling of failures
- [ ] **Progress tracking** - Users know what's happening

### Developer Experience

- [ ] **Modular architecture** - Easy to extend and modify
- [ ] **Type safety** - Full type hints throughout
- [ ] **Automated testing** - CI/CD pipeline with tests
- [ ] **Code quality** - Linting, formatting, complexity checks

---

## Risk Mitigation

### Technical Risks

- **Data loss during migration** → Backup database before major changes
- **Performance regression** → Benchmark before/after migration
- **Integration failures** → Comprehensive integration testing

### User Adoption Risks

- **Learning curve** → Comprehensive documentation and examples
- **Workflow disruption** → Maintain backwards compatibility during transition
- **Feature gaps** → Audit current functionality thoroughly

### Timeline Risks

- **Scope creep** → Strict phase boundaries and deliverables
- **Technical debt** → Address incrementally, don't boil the ocean
- **Resource constraints** → Focus on core functionality first
````
