# NFL QB Scraper - Technical Documentation

Advanced commands, development guidelines, and architectural details for the NFL QB Scraper system.

## 🏗️ Architecture Overview

### Component Structure
```text
CLI Commands → Operations → Core Logic → Database
     ↓             ↓           ↓          ↓
 User Interface  Workflows   Scraping   Storage
```

### Core Components

#### CLI Layer (`src/cli/`)
- **BaseCommand**: Abstract base for all CLI commands with common functionality
- **Command Classes**: Individual command implementations with specific business logic
- **Argument Parsing**: Comprehensive validation and help text for all commands

#### Operations Layer (`src/operations/`)
- **ScrapingOperation**: Orchestrates complete scraping workflows
- **ValidationOps**: Data quality validation and integrity checks
- **BatchManager**: Handles multi-season and resumable batch operations
- **PerformanceMonitor**: Real-time performance tracking and alerting

#### Core Business Logic (`src/core/`)
- **CoreScraper**: Main orchestrator using dependency injection
- **RequestManager**: HTTP requests, rate limiting, retries, and anti-detection
- **HTMLParser**: Data extraction, table parsing, and type conversion

#### Data Layer (`src/database/`, `src/models/`)
- **DatabaseManager**: Connection pooling, transactions, and bulk operations
- **Data Models**: Type-safe data classes with validation
- **Schema Management**: PostgreSQL schema with proper constraints

## 🔧 Advanced CLI Commands

### Batch Operations

#### Session Management
```bash
# Create a new batch session
nfl-qb-scraper batch create --name "multi-season-scrape" --description "2020-2024 seasons"

# Add multiple seasons to batch
nfl-qb-scraper batch add-items --session-id <session-id> --seasons 2024 2023 2022 2021 2020

# Execute batch with automatic resumability
nfl-qb-scraper batch execute --session-id <session-id>

# Monitor batch progress
nfl-qb-scraper batch status --session-id <session-id>

# List all batch sessions
nfl-qb-scraper batch list

# Resume failed batch
nfl-qb-scraper batch resume --session-id <session-id>

# Cancel running batch
nfl-qb-scraper batch cancel --session-id <session-id>
```

#### Batch Configuration
```bash
# Create batch with custom settings
nfl-qb-scraper batch create \\
  --name "custom-batch" \\
  --min-delay 10.0 \\
  --max-delay 15.0 \\
  --max-retries 5 \\
  --parallel-players 3

# Execute with validation
nfl-qb-scraper batch execute --session-id <session-id> --validate-each-season
```

### Performance Monitoring

#### Real-Time Monitoring
```bash
# Live performance dashboard (60 seconds, 5-second updates)
nfl-qb-scraper performance live --duration 60 --interval 5

# Simple format for logging/automation
nfl-qb-scraper performance live --format simple --duration 300

# Monitor specific operations
nfl-qb-scraper performance live --filter scraping_operation
```

#### Baseline Management
```bash
# Create performance baseline from recent operations
nfl-qb-scraper performance baseline --operation scraping_operation --samples 15

# Create baseline for database operations
nfl-qb-scraper performance baseline --operation database_bulk_insert --samples 20

# List all existing baselines
nfl-qb-scraper performance baseline --list

# Create baseline with custom criteria
nfl-qb-scraper performance baseline \\
  --operation scraping_operation \\
  --samples 25 \\
  --percentile 95 \\
  --min-success-rate 0.98
```

#### Performance Validation
```bash
# Validate current performance against baseline
nfl-qb-scraper performance validate --operation scraping_operation --hours 1

# Validate with custom thresholds
nfl-qb-scraper performance validate \\
  --operation scraping_operation \\
  --max-duration 20.0 \\
  --min-success-rate 0.95

# Validate using custom baseline file
nfl-qb-scraper performance validate \\
  --operation test_operation \\
  --baseline-file custom_baseline.json
```

#### Performance Reporting
```bash
# Generate comprehensive performance report
nfl-qb-scraper performance report --hours 24 --save

# Export specific metrics
nfl-qb-scraper performance export --format json --hours 48 --output metrics.json
nfl-qb-scraper performance export --format csv --hours 168 --output weekly_metrics.csv

# HTML report with visualizations  
nfl-qb-scraper performance export --format html --hours 168 --output weekly_report.html
```

#### Alert Management
```bash
# List recent alerts
nfl-qb-scraper performance alerts --list --hours 24

# Filter alerts by severity
nfl-qb-scraper performance alerts --list --severity critical
nfl-qb-scraper performance alerts --list --severity high

# Clear all alerts
nfl-qb-scraper performance alerts --clear

# Clear specific alert types
nfl-qb-scraper performance alerts --clear --type timeout
```

#### Session Tracking
```bash
# Start monitoring session for long operations
nfl-qb-scraper performance session --start "weekly_scraping" --operation batch_processing

# List active monitoring sessions
nfl-qb-scraper performance session --list

# Stop specific session
nfl-qb-scraper performance session --stop <session-id>

# Get session details
nfl-qb-scraper performance session --details <session-id>
```

### Advanced Scraping Options

#### Custom Rate Limiting
```bash
# Scrape with custom delays (10-15 seconds)
nfl-qb-scraper scrape --season 2024 --min-delay 10.0 --max-delay 15.0

# Conservative rate limiting for sensitive periods
nfl-qb-scraper scrape --season 2024 --min-delay 15.0 --max-delay 20.0 --jitter-range 5.0

# Fast scraping for development/testing (use carefully)
nfl-qb-scraper scrape --season 2024 --min-delay 3.0 --max-delay 5.0
```

#### Session and Request Management
```bash
# Force session rotation every N requests
nfl-qb-scraper scrape --season 2024 --rotate-session-every 10

# Custom retry configuration
nfl-qb-scraper scrape --season 2024 --max-retries 5 --retry-backoff 2.0

# Enable anti-detection features
nfl-qb-scraper scrape --season 2024 --anti-detection --behavioral-delays
```

#### Selective Scraping
```bash
# Scrape only players with missing data
nfl-qb-scraper scrape --season 2024 --only-missing

# Scrape specific player types
nfl-qb-scraper scrape --season 2024 --player-filter "starting_qbs"
nfl-qb-scraper scrape --season 2024 --player-filter "min_attempts:100"

# Resume interrupted scraping
nfl-qb-scraper scrape --season 2024 --resume --session-id <previous-session>
```

### Data Management & Analysis

#### Advanced Validation
```bash
# Deep validation with statistical analysis
nfl-qb-scraper validate --season 2024 --deep --statistical-analysis

# Validate specific data types
nfl-qb-scraper validate --season 2024 --tables qb_splits qb_splits_advanced

# Cross-season validation
nfl-qb-scraper validate --seasons 2024 2023 --compare --find-anomalies

# Validate with external data source
nfl-qb-scraper validate --season 2024 --external-source <path-to-reference-data>
```

#### Data Export & Import
```bash
# Export with advanced filtering
nfl-qb-scraper data export \\
  --season 2024 \\
  --format json \\
  --filter "attempts >= 100" \\
  --include-metadata \\
  --compress

# Export multiple seasons
nfl-qb-scraper data export \\
  --seasons 2024 2023 2022 \\
  --format parquet \\
  --output multi_season_data.parquet

# Import with validation
nfl-qb-scraper data import \\
  --file data.json \\
  --validate \\
  --skip-duplicates \\
  --batch-size 1000

# Import with transformation
nfl-qb-scraper data import \\
  --file legacy_data.csv \\
  --transform-schema \\
  --mapping-file field_mapping.json
```

#### Data Quality Analysis
```bash
# Comprehensive quality metrics
nfl-qb-scraper data quality --season 2024 --comprehensive --save-report

# Compare data quality across seasons
nfl-qb-scraper data quality --seasons 2024 2023 2022 --compare

# Field-level analysis
nfl-qb-scraper data quality --season 2024 --field-analysis --missing-data-report

# Data completeness matrix
nfl-qb-scraper data quality --season 2024 --completeness-matrix --export csv
```

### System Administration

#### Advanced Health Checks
```bash
# Comprehensive system diagnostics
nfl-qb-scraper health --comprehensive --performance-test

# Database performance analysis
nfl-qb-scraper health --database --query-performance --connection-pool-status

# Network connectivity tests
nfl-qb-scraper health --network --test-pfr-access --dns-resolution

# Storage and memory analysis
nfl-qb-scraper health --system --disk-usage --memory-usage --log-analysis
```

#### Advanced Monitoring
```bash
# Custom monitoring dashboard
nfl-qb-scraper monitor --dashboard --custom-metrics --real-time

# Historical trend analysis
nfl-qb-scraper monitor --trends --days 30 --show-patterns

# Performance regression detection
nfl-qb-scraper monitor --regression-analysis --baseline-comparison

# Resource utilization tracking
nfl-qb-scraper monitor --resources --cpu --memory --network --database
```

#### Advanced Cleanup
```bash
# Selective cleanup with criteria
nfl-qb-scraper cleanup \\
  --logs --days 30 \\
  --temp-files --size-limit 100MB \\
  --old-sessions --inactive-days 7

# Database maintenance
nfl-qb-scraper cleanup \\
  --database \\
  --vacuum \\
  --reindex \\
  --update-statistics

# Performance data cleanup
nfl-qb-scraper cleanup \\
  --performance-data --days 90 \\
  --keep-baselines \\
  --archive-old-data
```

## 🔌 Programmatic API

### Core Scraper Usage
```python
from src.core.scraper import CoreScraper
from src.core.request_manager import RequestManager
from src.core.html_parser import HTMLParser
from src.database.db_manager import DatabaseManager
from src.config.config import config

# Initialize with dependency injection
request_manager = RequestManager(
    rate_limit_delay=7.0,
    jitter_range=3.0,
    max_retries=3
)

html_parser = HTMLParser()
db_manager = DatabaseManager(config)

scraper = CoreScraper(
    request_manager=request_manager,
    html_parser=html_parser,
    db_manager=db_manager,
    config=config
)

# Scrape a season
try:
    results = scraper.scrape_season(2024)
    print(f"Scraped {len(results.players)} players")
except Exception as e:
    logger.error(f"Scraping failed: {e}")
```

### Operations Layer Usage
```python
from src.operations.scraping_operation import ScrapingOperation
from src.operations.performance_monitor import PerformanceMonitor

# High-level operation
operation = ScrapingOperation(config)
monitor = PerformanceMonitor(config)

# Execute with monitoring
with monitor.monitor_operation("season_scrape"):
    result = operation.execute(season=2024, validate=True)

# Check performance
metrics = monitor.get_operation_metrics("season_scrape")
print(f"Average duration: {metrics.avg_duration}s")
```

### Batch Operations
```python
from src.operations.batch_manager import BatchManager

batch_manager = BatchManager(config)

# Create and execute batch
batch_session = batch_manager.create_batch_session(
    name="multi_season_scrape",
    description="Scrape 2020-2024 seasons"
)

batch_manager.add_batch_items(
    session_id=batch_session.session_id,
    seasons=[2024, 2023, 2022, 2021, 2020]
)

# Execute with progress callback
def progress_callback(progress):
    print(f"Progress: {progress.completed}/{progress.total}")

batch_manager.execute_batch(
    session_id=batch_session.session_id,
    progress_callback=progress_callback
)
```

### Performance Monitoring Integration
```python
from src.operations.performance_monitor import PerformanceMonitor, Metric, MetricType

monitor = PerformanceMonitor(config)

# Create custom metrics
metric = Metric(
    name="custom_processing_time",
    value=15.2,
    metric_type=MetricType.DURATION,
    unit="seconds",
    labels={"operation": "data_validation", "season": "2024"}
)

# Record metric
session = monitor.start_monitoring_session("data_processing", "validation")
session.add_metric(metric)
monitor.end_monitoring_session(session.session_id)

# Create and validate baselines
baseline = monitor.create_performance_baseline(
    operation_type="data_validation",
    sample_size=20
)

# Validate current performance
current_metrics = monitor.get_operation_summaries()["data_validation"]
validation = monitor.validate_performance_against_baseline(current_metrics, baseline)

if not validation.passed:
    for violation in validation.violations:
        print(f"Performance violation: {violation}")
```

## 🧪 Development & Testing

### Development Setup
```bash
# Install in development mode with all dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run development checks
make dev-check  # or run manually:
mypy src/
flake8 src/ tests/
black --check src/ tests/
pytest tests/
```

### Testing Framework
```bash
# Run specific test categories
pytest tests/unit/           # Unit tests only
pytest tests/integration/    # Integration tests only
pytest tests/e2e/           # End-to-end tests only

# Run tests with coverage
pytest tests/ --cov=src --cov-report=html

# Run performance tests
pytest tests/performance/ --benchmark-only

# Run tests with different configurations
pytest tests/ --env=staging
pytest tests/ --database=memory
```

### Code Quality Tools
```bash
# Type checking with detailed output
mypy src/ --show-error-codes --show-error-context

# Linting with custom rules
flake8 src/ --config=.flake8 --show-source

# Code formatting
black src/ tests/
isort src/ tests/

# Security scanning
bandit -r src/

# Complexity analysis
radon cc src/ --min B
```

### Configuration Management
```python
# Environment-specific configuration
from src.config.config import Config, get_config

# Development config
dev_config = get_config("development")

# Production config with overrides
prod_config = get_config("production", overrides={
    "rate_limiting": {"min_delay": 10.0},
    "monitoring": {"enabled": True}
})

# Custom configuration
custom_config = Config(
    database=DatabaseConfig(url="postgresql://..."),
    scraping=ScrapingConfig(min_delay=5.0, max_retries=5),
    monitoring=MonitoringConfig(enabled=True, retention_days=90)
)
```

## 🔍 Debugging & Troubleshooting

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
nfl-qb-scraper --verbose scrape --season 2024

# Debug specific components
export DEBUG_COMPONENTS="request_manager,html_parser"
nfl-qb-scraper scrape --season 2024

# Save debug output
nfl-qb-scraper --verbose scrape --season 2024 2>&1 | tee debug_output.log
```

### Performance Debugging
```bash
# Profile scraping operation
nfl-qb-scraper scrape --season 2024 --profile --profile-output scraping_profile.prof

# Memory usage tracking
nfl-qb-scraper scrape --season 2024 --track-memory --memory-report memory_usage.json

# Database query analysis
nfl-qb-scraper scrape --season 2024 --log-sql-queries --sql-timing
```

### Error Analysis
```bash
# Analyze recent errors
nfl-qb-scraper analyze-errors --hours 24 --categorize

# Export error patterns
nfl-qb-scraper analyze-errors --export errors_analysis.json --include-stack-traces

# Generate error report
nfl-qb-scraper analyze-errors --report --send-email admin@example.com
```

## 📊 Monitoring & Alerting

### Custom Alerts
```python
from src.operations.performance_monitor import AlertManager, AlertThreshold

alert_manager = AlertManager(config)

# Set custom thresholds
alert_manager.set_threshold(AlertThreshold(
    metric="request_duration",
    operation="scraping_operation",
    warning_threshold=15.0,
    critical_threshold=30.0,
    severity_levels=["low", "medium", "high", "critical"]
))

# Custom alert handler
def custom_alert_handler(alert):
    if alert.severity == "critical":
        send_email_notification(alert)
    log_alert_to_monitoring_system(alert)

alert_manager.add_alert_handler(custom_alert_handler)
```

### Integration with External Monitoring
```python
# Prometheus metrics export
from src.operations.monitoring.prometheus_exporter import PrometheusExporter

exporter = PrometheusExporter(config)
exporter.start_metrics_server(port=8000)

# DataDog integration
from src.operations.monitoring.datadog_integration import DataDogMetrics

datadog = DataDogMetrics(api_key="your-api-key")
datadog.send_metrics(monitor.get_real_time_metrics())

# Custom webhook alerts
from src.operations.monitoring.webhook_alerts import WebhookAlerter

webhook_alerter = WebhookAlerter(webhook_url="https://your-webhook.com/alerts")
alert_manager.add_alert_handler(webhook_alerter.send_alert)
```

---

For basic usage and installation instructions, see the main [README.md](../README.md) in the root directory.

For detailed development rules and guidelines, reference the modular rules system in `.cursor/rules/`.