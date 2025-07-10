# Phase 1 Foundation: Prompt Templates

_Ready-to-use prompts for building CLI skeleton and architecture_

## 🎯 Phase 1 Overview

**Goal:** Create CLI skeleton and foundation without breaking existing scripts  
**Standards:** 60% test coverage minimum, maintain backwards compatibility  
**Success Criteria:** CLI help system functional, command routing extensible,
zero impact on existing workflows

---

## 📋 Essential Context Template

## Always include this context in Phase 1 prompts:

````text
## Context Files:
@.cursorrules
@.cursor/rules/migration-process.mdc
@.cursor/rules/cli-specific.mdc
@.cursor/rules/python-quality.mdc

**Current Phase:** Phase 1 (Foundation)
**Standards:** 60% test coverage minimum, backwards compatibility required
**Constraints:** DO NOT modify existing scripts, DO NOT break current functionality
```text
---

## 🏗️ 1. CLI Architecture Setup

### Template A: Initial CLI Structure

```text
[CLI-Architecture-Phase1] Create the foundational CLI architecture for NFL QB scraper migration.

## Context Files:
@.cursorrules
@.cursor/rules/migration-process.mdc
@.cursor/rules/cli-specific.mdc
@.cursor/rules/python-quality.mdc

**Current Phase:** Phase 1 (Foundation)
**Standards:** 60% test coverage minimum, backwards compatibility required

## Objective:
Set up the basic CLI structure with proper module organization and command routing.

## Architecture Requirements:
1. Create src/cli/main.py as single entry point
2. Implement BaseCommand abstract class that all commands inherit from
3. Set up command routing system for: scrape, setup, data, validate
4. Create help system with examples and usage documentation
5. Implement configuration loading with proper precedence

## Module Structure:
- src/cli/ - CLI handlers (no business logic)
- src/core/ - Core business logic
- src/operations/ - High-level operations
- src/config/ - Configuration management
- Proper dependency injection patterns

## CLI Requirements:
- Commands inherit from BaseCommand
- Help system shows available commands and examples
- Invalid commands handled gracefully with suggestions
- Tab completion support where possible
- Progress indication for long operations

## Success Criteria:
- `python -m pfr_scraper --help` works
- Shows available commands with clear descriptions
- Handles invalid commands with helpful error messages
- Command structure is extensible for future phases

## Testing:
- Unit tests for command parsing and routing
- Integration tests for help system
- Validation tests for invalid inputs
- 60% minimum test coverage

## Implementation Notes:
- Use Click or argparse for command parsing
- Implement proper error handling with user-friendly messages
- Add logging with structured format
- Follow project coding standards from .cursorrules
```text
### Template B: Command Registration System

````

[Command-Registration-Phase1] Implement extensible command registration system.

## Context Files:

@.cursorrules @.cursor/rules/cli-specific.mdc @.cursor/rules/python-quality.mdc

**Current Phase:** Phase 1 (Foundation)

## Objective:

Create a system for registering and discovering CLI commands that can be
extended in future phases.

## Requirements:

1. CommandRegistry class for managing available commands
2. Auto-discovery of commands in src/cli/commands/
3. Command metadata (name, description, examples)
4. Plugin-style architecture for easy extension
5. Proper error handling for command loading

## Implementation:

- Create src/cli/registry.py with CommandRegistry class
- Implement command discovery using importlib
- Add command validation and error handling
- Create base command interface with required methods
- Add command metadata and help generation

## Command Structure:

```python
class BaseCommand(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass

    @abstractmethod
    def add_arguments(self, parser) -> None:
        pass

    @abstractmethod
    def execute(self, args) -> int:
        pass
```

## Testing:

- Unit tests for command registration
- Tests for command discovery
- Error handling tests for invalid commands
- Integration tests for command loading

````text
### Template C: Command Structure Validation
```text
[Command-Structure-Validation-Phase1] Validate CLI command structure against
MIGRATION_PLAN.md requirements.

**Context Files:** @.cursorrules @.cursor/rules/cli-specific.mdc
@docs/MIGRATION_PLAN.md

**Current Phase:** Phase 1 (Foundation)

**Objective:** Ensure the CLI command structure exactly matches the requirements
specified in MIGRATION_PLAN.md.

## Required Commands from MIGRATION_PLAN.md:

## Scrape Commands:

- `python -m pfr_scraper scrape season 2024 --profile full`
- `python -m pfr_scraper scrape players --names "Joe Burrow,Josh Allen" --season 2024`
- `python -m pfr_scraper scrape splits --season 2024 --split-types basic,advanced`
- `python -m pfr_scraper scrape resume --session-id abc123`

## Setup Commands:

- `python -m pfr_scraper setup all`
- `python -m pfr_scraper setup schema --deploy`
- `python -m pfr_scraper setup teams --include-multi-team`
- `python -m pfr_scraper setup status`

## Data Commands:

- `python -m pfr_scraper data clear --season 2024 --confirm`
- `python -m pfr_scraper data validate --season 2024 --fix-errors`
- `python -m pfr_scraper data aggregate --season 2024 --prefer-combined`
- `python -m pfr_scraper data export --format csv --season 2024`

## Debug Commands:

- `python -m pfr_scraper debug connection`
- `python -m pfr_scraper debug player "Joe Burrow" --season 2024`
- `python -m pfr_scraper debug fields --url "https://pro-football-reference.com/..."`

## Implementation Requirements:

1. Create argument parsing structure that supports all required commands
2. Implement proper subcommand handling for each category
3. Add validation for all argument combinations
4. Ensure consistent argument naming across commands
5. Implement help text that matches the migration plan examples

## Validation Criteria:

- All commands parse correctly with expected arguments
- Help text is intuitive and matches examples
- Command structure is consistent across categories
- Arguments follow consistent naming patterns
- Error messages are helpful and actionable
- Tab completion works where implemented

## Command Structure Implementation:

```python
class ScrapeCommand(BaseCommand):
    name = "scrape"
    description = "Scrape QB data from Pro Football Reference"

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest='scrape_type', required=True)

        # Season scraping: scrape season 2024 --profile full
        season_parser = subparsers.add_parser('season', help='Scrape full season')
        season_parser.add_argument('year', type=int, help='Season year')
        season_parser.add_argument('--profile', choices=['full', 'basic'], default='full')

        # Player scraping: scrape players --names "Joe Burrow,Josh Allen" --season 2024
        players_parser = subparsers.add_parser('players', help='Scrape specific players')
        players_parser.add_argument('--names', required=True, help='Comma-separated player names')
        players_parser.add_argument('--season', type=int, required=True, help='Season year')

        # Splits scraping: scrape splits --season 2024 --split-types basic,advanced
        splits_parser = subparsers.add_parser('splits', help='Scrape splits data')
        splits_parser.add_argument('--season', type=int, required=True, help='Season year')
        splits_parser.add_argument('--split-types', required=True, help='Comma-separated split types')

        # Resume scraping: scrape resume --session-id abc123
        resume_parser = subparsers.add_parser('resume', help='Resume failed scraping')
        resume_parser.add_argument('--session-id', required=True, help='Session ID to resume')
```text
## Testing Requirements:

- Unit tests for each command's argument parsing
- Integration tests with actual command execution
- Validation tests for all argument combinations
- Help text validation against migration plan examples
- Error handling tests for invalid arguments

```text
---

## ⚙️ 2. Configuration System

### Template A: Configuration Architecture
```text
[Config-System-Phase1] Implement centralized configuration system with proper
precedence.

**Context Files:** @.cursorrules @.cursor/rules/migration-process.mdc
@.cursor/rules/python-quality.mdc

**Current Phase:** Phase 1 (Foundation)

**Objective:** Create a robust configuration system that supports multiple
sources with proper precedence hierarchy.

## Configuration Sources (in precedence order):

1. Command-line arguments (highest priority)
2. Environment variables (PFR\_\*)
3. Configuration files (.pfr-scraper.yaml, pfr-scraper.toml)
4. Default values (lowest priority)

## Requirements:

1. Support YAML and TOML configuration files
2. Environment variable overrides with PFR\_ prefix
3. Command-line argument overrides
4. Configuration validation with clear error messages
5. --show-config option to display current configuration
6. Type safety with proper dataclass definitions

## Implementation:

- Create src/config/settings.py with configuration dataclasses
- Implement ConfigLoader class for loading and merging configs
- Add configuration validation with specific error messages
- Support development and production configuration profiles
- Create configuration file templates

## Configuration Structure:

```python
@dataclass
class DatabaseConfig:
    url: str
    pool_size: int = 10
    timeout: int = 30

@dataclass
class ScrapingConfig:
    rate_limit: float = 2.0
    timeout: int = 30
    retries: int = 3
    user_agent: str = "NFL-QB-Scraper/1.0"

@dataclass
class AppConfig:
    database: DatabaseConfig
    scraping: ScrapingConfig
    log_level: str = "INFO"
    debug: bool = False
```text
## Backwards Compatibility:

- Create adapter for legacy script configurations
- Don't break existing .env files during Phase 1
- Document migration path for users

## Testing:

- Unit tests for configuration loading and precedence
- Integration tests for CLI configuration options
- Validation tests for invalid configurations
- Environment variable override tests

```text
### Template B: Configuration Validation
```text
[Config-Validation-Phase1] Add comprehensive validation for configuration
system.

**Context Files:** @.cursorrules @.cursor/rules/python-quality.mdc

**Current Phase:** Phase 1 (Foundation)

**Objective:** Implement robust configuration validation with clear, actionable
error messages.

## Validation Categories:

1. **Type Validation:** Ensure correct data types for all fields
2. **Range Validation:** Check numeric values are within valid ranges
3. **Format Validation:** Validate URLs, file paths, etc.
4. **Dependency Validation:** Check for required combinations
5. **Environment Validation:** Verify external dependencies

## Validation Rules:

- Database URL format validation
- Rate limit between 0.1 and 10.0 seconds
- Pool size between 1 and 100 connections
- Timeout values > 0
- Log level in [DEBUG, INFO, WARNING, ERROR]
- File paths exist and are accessible

## Error Message Format:

```text
Configuration Error: Invalid rate_limit value

Value: -1.0
Expected: Number between 0.1 and 10.0 seconds
Source: .pfr-scraper.yaml line 15
Fix: Set rate_limit to a positive number (recommended: 2.0)
```text
## Implementation:

- Create src/config/validation.py with validation functions
- Add ValidationError class with detailed error information
- Implement validation rules for each configuration section
- Add suggestions for fixing common configuration errors
- Create validation result reporting

## Testing:

- Unit tests for each validation rule
- Integration tests for configuration loading with validation
- Error message format tests
- Edge case tests for boundary conditions

```text
---

## 🔍 3. Testing and Validation

### Template A: Foundation Testing Setup
```text
[Foundation-Testing-Phase1] Set up comprehensive testing framework for Phase 1
components.

**Context Files:** @.cursorrules @.cursor/rules/testing-standards.mdc
@.cursor/rules/python-quality.mdc

**Current Phase:** Phase 1 (Foundation) **Coverage Requirement:** 60% minimum

**Objective:** Create testing infrastructure and comprehensive tests for CLI
foundation components.

## Testing Framework Setup:

1. Configure pytest with appropriate plugins
2. Set up test fixtures for common scenarios
3. Create mock objects for external dependencies
4. Implement test utilities for CLI testing
5. Add coverage reporting with coverage.py

## Test Categories:

1. **Unit Tests:** Individual functions and classes
2. **Integration Tests:** Component interactions
3. **CLI Tests:** Command-line interface behavior
4. **Configuration Tests:** Configuration loading and validation

## Test Structure:

```text
tests/
├── unit/
│   ├── test_cli_registry.py
│   ├── test_config_loading.py
│   └── test_command_parsing.py
├── integration/
│   ├── test_cli_workflow.py
│   └── test_config_integration.py
├── fixtures/
│   ├── config_files.py
│   └── sample_data.py
└── utils/
    ├── cli_testing.py
    └── mock_helpers.py
```text
## Testing Requirements:

- All public methods must have unit tests
- CLI commands must have integration tests
- Configuration system must have validation tests
- Error scenarios must be tested
- Mock external dependencies appropriately

## CLI Testing Utilities:

- Command-line invocation helpers
- Output capture and assertion utilities
- Configuration file creation helpers
- Mock HTTP response generators

## Coverage Targets:

- Overall coverage: 60% minimum
- Core modules: 70% minimum
- CLI commands: 80% minimum
- Configuration system: 90% minimum

```text
### Template B: Phase 1 Validation Tests
```text
[Phase1-Validation-Tests] Create validation tests to ensure Phase 1 success
criteria are met.

**Context Files:** @.cursorrules @.cursor/rules/migration-process.mdc
@.cursor/rules/testing-standards.mdc

**Current Phase:** Phase 1 (Foundation)

**Objective:** Create comprehensive validation tests that verify Phase 1
deliverables meet all requirements.

## Success Criteria Tests:

1. **CLI Functionality:**
   - Help system is intuitive and comprehensive
   - Command routing is extensible
   - Error handling is user-friendly
   - Configuration loading works correctly

2. **Backwards Compatibility:**
   - All existing scripts continue to work
   - No breaking changes to current workflows
   - Legacy configurations are respected

3. **Architecture Quality:**
   - Proper module separation
   - Clean interfaces between components
   - Extensible design for future phases

## Test Implementation:

```python
def test_cli_help_system():
    """Test that CLI help system is intuitive and comprehensive."""
    result = run_cli(['--help'])
    assert result.exit_code == 0
    assert 'scrape' in result.output
    assert 'setup' in result.output
    assert 'data' in result.output
    assert 'validate' in result.output
    assert 'Examples:' in result.output

def test_command_routing_extensible():
    """Test that command routing can be extended."""
    # Test that new commands can be added easily
    registry = CommandRegistry()
    initial_count = len(registry.commands)

    # Add a mock command
    registry.register_command(MockCommand())
    assert len(registry.commands) == initial_count + 1

def test_backwards_compatibility():
    """Test that existing scripts continue to work."""
    # Test that legacy scripts can still be imported and executed
    from scripts.enhanced_qb_scraper import main
    # Should not raise any import errors
    assert callable(main)
```text
## Validation Categories:

- Functional validation: Features work as designed
- Performance validation: Response times are acceptable
- Usability validation: CLI is intuitive to use
- Architecture validation: Code structure is sound
- Compatibility validation: No breaking changes

## Automated Validation:

- Run validation tests as part of CI/CD pipeline
- Generate validation reports with pass/fail status
- Create benchmark comparisons for performance
- Validate against Phase 1 requirements checklist

```text
---

## 📚 4. Documentation and User Experience

### Template A: CLI Help System
```text
[CLI-Help-System-Phase1] Create comprehensive help system for CLI commands.

**Context Files:** @.cursorrules @.cursor/rules/cli-specific.mdc

**Current Phase:** Phase 1 (Foundation)

**Objective:** Implement an intuitive help system that guides users through CLI
usage with clear examples.

## Help System Requirements:

1. **Global Help:** Overview of all available commands
2. **Command Help:** Detailed help for specific commands
3. **Examples:** Real-world usage examples for each command
4. **Error Guidance:** Helpful suggestions for common mistakes
5. **Context-Aware:** Show relevant options based on current state

## Help Content Structure:

```text
pfr-scraper - NFL QB Data Scraper

USAGE:
    pfr-scraper <command> [options]

COMMANDS:
    scrape      Scrape QB data from Pro Football Reference
    setup       Configure database and environment
    data        Manage and validate scraped data
    validate    Check data quality and integrity

EXAMPLES:
    pfr-scraper scrape --help
    pfr-scraper setup --database-url postgresql://...
    pfr-scraper data validate --season 2024

For detailed help on any command, use:
    pfr-scraper <command> --help
```text
## Implementation:

- Create src/cli/help.py with help formatting utilities
- Implement context-aware help generation
- Add examples and usage patterns for each command
- Create help content templates
- Add colorized output for better readability

## User Experience:

- Clear command descriptions with examples
- Helpful error messages with suggestions
- Progressive disclosure of advanced options
- Quick-start guide for common workflows

```text
### Template B: Error Handling and Messages
```text
[Error-Handling-Phase1] Implement comprehensive error handling with
user-friendly messages.

**Context Files:** @.cursorrules @.cursor/rules/python-quality.mdc
@.cursor/rules/cli-specific.mdc

**Current Phase:** Phase 1 (Foundation)

**Objective:** Create consistent, helpful error handling that guides users to
solutions.

## Error Categories:

1. **Configuration Errors:** Invalid or missing configuration
2. **Command Errors:** Invalid command usage or arguments
3. **System Errors:** Database connectivity, file permissions
4. **User Errors:** Invalid input or missing requirements

## Error Message Format:

```text
Error: Invalid configuration

Problem: Database URL is malformed
Value: "postgresql://invalid-url"
Expected: Valid PostgreSQL connection string
Example: "postgresql://user:pass@host:5432/db"

Fix: Update your configuration file or set PFR_DATABASE_URL environment variable
```text
## Implementation:

- Create src/cli/errors.py with error classes
- Implement error formatting utilities
- Add error context and suggestions
- Create error recovery mechanisms where possible
- Add logging for debugging support

## Error Handling Standards:

- Never show technical stack traces to users
- Always provide actionable suggestions
- Include context about what the user was trying to do
- Log detailed error information for debugging
- Support --debug flag for verbose error output

## Testing:

- Unit tests for error formatting
- Integration tests for error scenarios
- User experience tests for error messages
- Recovery mechanism tests

```text
---

## 🚀 Phase 1 Completion Validation

### Final Phase 1 Validation Prompt
```text
[Phase1-Completion-Validation] Validate that Phase 1 Foundation is complete and
ready for Phase 2.

**Context Files:** @.cursorrules @.cursor/rules/migration-process.mdc
@.cursor/rules/testing-standards.mdc

**Current Phase:** Phase 1 (Foundation) - Completion Validation

**Objective:** Comprehensive validation that all Phase 1 requirements are met
and the foundation is solid for Phase 2.

## Validation Checklist:

- [ ] CLI help system is intuitive and comprehensive
- [ ] Command routing is extensible for future phases
- [ ] Configuration system works with proper precedence
- [ ] All existing scripts continue to work unchanged
- [ ] Test coverage meets 60% minimum requirement
- [ ] Error handling is user-friendly and helpful
- [ ] Documentation covers all Phase 1 features
- [ ] Code quality meets project standards

## Technical Validation:

1. **Functionality Tests:**
   - CLI commands parse correctly
   - Help system shows appropriate information
   - Configuration loading works from all sources
   - Error handling provides helpful messages

2. **Quality Tests:**
   - Code passes all linting and type checking
   - Test coverage meets minimum requirements
   - Documentation is complete and accurate
   - Performance is acceptable for user interactions

3. **Compatibility Tests:**
   - All existing scripts work without modification
   - No breaking changes to current workflows
   - Legacy configurations are respected
   - Migration path is clear for users

## Success Criteria:

- All validation tests pass
- User acceptance testing is positive
- Performance meets baseline requirements
- Architecture is ready for Phase 2 expansion
- Documentation is complete and helpful

## Phase 2 Readiness:

- Foundation is stable and well-tested
- Architecture supports scraper consolidation
- Configuration system can handle scraper settings
- CLI framework can accommodate new commands
- Team is confident in foundation quality

## Sign-off Requirements:

- Technical validation: All tests pass
- User validation: Help system is intuitive
- Architecture validation: Code structure is sound
- Performance validation: Response times acceptable
- Documentation validation: Complete and accurate

````

---

## 💡 Quick Reference

### Common Phase 1 Commands

```bash
# Test CLI help system
python -m pfr_scraper --help

# Test configuration loading
python -m pfr_scraper --show-config

# Test command routing
python -m pfr_scraper scrape --help

# Run Phase 1 validation tests
pytest tests/phase1/ -v

# Check test coverage
pytest --cov=src --cov-report=html
```

### Phase 1 File Structure

````text
src/
├── cli/
│   ├── __init__.py
│   ├── main.py           # CLI entry point
│   ├── registry.py       # Command registration
│   ├── help.py          # Help system
│   └── errors.py        # Error handling
├── config/
│   ├── __init__.py
│   ├── settings.py      # Configuration dataclasses
│   ├── loader.py        # Configuration loading
│   └── validation.py    # Configuration validation
└── core/
    ├── __init__.py
    └── base.py          # Base classes and interfaces
```text
### Next Steps

Once Phase 1 is complete, move to [Phase 2 Core Prompts](phase2-core-prompts.md)
for scraper consolidation and CLI command implementation.
````
