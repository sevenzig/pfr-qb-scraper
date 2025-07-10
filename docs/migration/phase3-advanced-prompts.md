# Phase 3 Advanced: Prompt Templates

_Ready-to-use prompts for advanced data management and validation_

## 🎯 Phase 3 Overview

**Goal:** Implement advanced data management, validation, and multi-team
operations  
**Standards:** 80% test coverage minimum, production-ready features  
**Success Criteria:** Complex data scenarios handled, validation comprehensive,
performance optimized

---

## 📋 Essential Context Template

````text
## Context Files:
@.cursorrules
@.cursor/rules/migration-process.mdc
@.cursor/rules/python-quality.mdc
@.cursor/rules/testing-standards.mdc

**Current Phase:** Phase 3 (Advanced)
**Standards:** 80% test coverage minimum, production-ready features
**Focus:** Advanced data operations, multi-team handling, comprehensive validation
```text
---

## 🔍 1. Data Validation and Quality

### Template A: Advanced Data Validation System

````

[Advanced-Data-Validation-Phase3] Implement comprehensive data validation and
quality assurance system.

## Context Files:

@.cursorrules @.cursor/rules/python-quality.mdc @src/models/qb_models.py

**Current Phase:** Phase 3 (Advanced) **Standards:** 80% test coverage minimum

## Objective:

Create a sophisticated data validation system that catches all quality issues
and provides actionable feedback.

## Validation Categories:

1. **NFL Business Rules:** QB-specific constraints and logic
2. **Statistical Consistency:** Cross-field validation and relationships
3. **Multi-Team Scenarios:** Handle 2TM/3TM players correctly
4. **Historical Context:** Season-appropriate validation rules
5. **Data Completeness:** Missing field detection and impact assessment

## Implementation Requirements:

- Create src/operations/validation_ops.py
- Implement ValidationEngine with configurable rules
- Add ValidationReport class for detailed reporting
- Support batch validation with progress tracking
- Include data quality scoring and recommendations

## CLI Commands:

```bash
pfr-scraper data validate --season 2024 --fix-issues
pfr-scraper data quality-report --season 2024 --format detailed
pfr-scraper data validate --player "Joe Burrow" --all-seasons
```

## Success Criteria:

- Catches all known data quality issues
- Provides actionable fix recommendations
- Handles edge cases (multi-team players, missing data)
- Performance suitable for large datasets
- Comprehensive reporting with severity levels

````text
### Template B: Multi-Team Player Handling
```text
[Multi-Team-Player-Handling-Phase3] Implement sophisticated handling of
multi-team player scenarios.

**Context Files:** @.cursorrules @.cursor/rules/python-quality.mdc
@debug/debug_name_matching.py

**Current Phase:** Phase 3 (Advanced)

**Objective:** Handle complex multi-team player scenarios (2TM/3TM) with
intelligent aggregation and conflict resolution.

## Multi-Team Scenarios:

1. **2TM Players:** Players who played for 2 teams in a season
2. **3TM Players:** Players who played for 3 teams in a season
3. **Trade Scenarios:** Mid-season team changes
4. **Aggregation Logic:** Prefer 2TM/3TM over individual team stats

## Implementation:

```python
class MultiTeamHandler:
    def aggregate_multi_team_data(self, player_name: str, season: int) -> PlayerSeasonData:
        """Aggregate multi-team player data intelligently."""
        # Get all team records for the player
        team_records = self.get_all_team_records(player_name, season)

        # Find the aggregated record (2TM/3TM)
        aggregated_record = self.find_aggregated_record(team_records)

        if aggregated_record:
            return aggregated_record
        else:
            # Create aggregated record from individual team stats
            return self.create_aggregated_record(team_records)

    def resolve_data_conflicts(self, records: List[PlayerSeasonData]) -> PlayerSeasonData:
        """Resolve conflicts between different team records."""
        # Priority: 2TM/3TM > most recent > most complete
        pass
```text
## CLI Commands:

```bash
pfr-scraper data aggregate --player "Tim Boyle" --season 2024
pfr-scraper data multi-team-report --season 2024
pfr-scraper data fix-multi-team --season 2024 --dry-run
```text
## Success Criteria:

- Correctly identifies and aggregates multi-team players
- Handles conflicts between team records intelligently
- Provides clear reporting on multi-team scenarios
- Maintains data integrity throughout aggregation

```text
---

## 🛠️ 2. Advanced Operations

### Template A: Batch Operations and Session Management
```text
[Batch-Operations-Session-Management-Phase3] Implement advanced batch operations
with session management.

**Context Files:** @.cursorrules @.cursor/rules/python-quality.mdc
@.cursor/rules/testing-standards.mdc

**Current Phase:** Phase 3 (Advanced)

**Objective:** Create robust batch operations that can handle large datasets
with proper session management and resumability.

## Batch Operation Features:

1. **Resumable Operations:** Continue from where stopped
2. **Progress Tracking:** Detailed progress with ETAs
3. **Error Recovery:** Skip failed items and continue
4. **Resource Management:** Proper cleanup and connection handling
5. **Parallel Processing:** Safe concurrent operations where appropriate

## Implementation:

```python
class BatchOperationManager:
    def __init__(self, config: BatchConfig):
        self.config = config
        self.session = BatchSession()
        self.progress_tracker = ProgressTracker()

    def batch_scrape_season(self, season: int, resume: bool = False) -> BatchResult:
        """Scrape all QBs for a season with resumability."""
        # Load or create session
        if resume:
            session = self.load_session(f"season_{season}")
        else:
            session = self.create_session(f"season_{season}")

        # Get player list
        players = self.get_season_players(season)
        remaining_players = session.get_remaining_players(players)

        # Process with progress tracking
        results = []
        for player in remaining_players:
            try:
                result = self.scrape_player_with_retry(player, season)
                results.append(result)
                session.mark_completed(player)
            except Exception as e:
                session.mark_failed(player, str(e))
                continue

        return BatchResult(
            total=len(players),
            completed=len(results),
            failed=len(session.failed_items),
            results=results
        )
```text
## CLI Commands:

```bash
pfr-scraper batch scrape-season --year 2024 --resume
pfr-scraper batch scrape-players --file players.txt --parallel 3
pfr-scraper batch status --session season_2024
```text
## Success Criteria:

- Handles large datasets efficiently
- Provides detailed progress tracking
- Supports resumable operations
- Manages resources properly
- Handles failures gracefully

```text
### Template B: Data Export and Reporting
```text
[Data-Export-Reporting-Phase3] Implement comprehensive data export and reporting
capabilities.

**Context Files:** @.cursorrules @.cursor/rules/cli-specific.mdc

**Current Phase:** Phase 3 (Advanced)

**Objective:** Create flexible data export and reporting system that supports
multiple formats and use cases.

## Export Features:

1. **Multiple Formats:** CSV, JSON, Excel, SQL dumps
2. **Flexible Filtering:** By season, team, player, performance metrics
3. **Aggregation Options:** Team totals, season summaries, career stats
4. **Custom Reports:** User-defined report templates
5. **Scheduling:** Automated report generation

## Implementation:

```python
class DataExportManager:
    def export_season_data(self, season: int, format: str = 'csv',
                          filters: Dict = None) -> ExportResult:
        """Export season data with flexible filtering."""
        # Apply filters
        data = self.apply_filters(
            self.get_season_data(season),
            filters or {}
        )

        # Export in requested format
        if format == 'csv':
            return self.export_to_csv(data)
        elif format == 'json':
            return self.export_to_json(data)
        elif format == 'excel':
            return self.export_to_excel(data)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def generate_report(self, report_type: str, **kwargs) -> ReportResult:
        """Generate predefined or custom reports."""
        report_generators = {
            'season_summary': self.generate_season_summary,
            'team_analysis': self.generate_team_analysis,
            'player_comparison': self.generate_player_comparison,
            'quality_report': self.generate_quality_report
        }

        generator = report_generators.get(report_type)
        if not generator:
            raise ValueError(f"Unknown report type: {report_type}")

        return generator(**kwargs)
```text
## CLI Commands:

```bash
pfr-scraper data export --season 2024 --format csv --output season_2024.csv
pfr-scraper data report season-summary --season 2024
pfr-scraper data report team-analysis --team CIN --seasons 2020-2024
```text
## Success Criteria:

- Supports multiple export formats
- Provides flexible filtering options
- Generates useful reports
- Handles large datasets efficiently
- Maintains data integrity during export

```text
---

## 🧪 3. Testing and Quality

### Template A: Performance Testing and Optimization
```text
[Performance-Testing-Optimization-Phase3] Implement comprehensive performance
testing and optimization.

**Context Files:** @.cursorrules @.cursor/rules/testing-standards.mdc

**Current Phase:** Phase 3 (Advanced) **Coverage Requirement:** 80% minimum

**Objective:** Ensure all Phase 3 features perform well under realistic load
conditions.

## Performance Testing Categories:

1. **Load Testing:** Large dataset processing
2. **Stress Testing:** System limits and breaking points
3. **Memory Profiling:** Memory usage optimization
4. **Database Performance:** Query optimization and indexing
5. **Network Efficiency:** HTTP request optimization

## Implementation:

```python
class PerformanceTestSuite:
    def test_batch_operation_performance(self):
        """Test batch operations with realistic data volumes."""
        # Test with 100, 500, 1000 players
        for batch_size in [100, 500, 1000]:
            start_time = time.time()

            result = self.batch_manager.batch_scrape_players(
                self.generate_test_players(batch_size)
            )

            elapsed = time.time() - start_time

            # Performance assertions
            assert elapsed < batch_size * 0.1  # Max 0.1s per player
            assert result.success_rate > 0.95  # 95% success rate
            assert self.get_memory_usage() < 500 * 1024 * 1024  # Max 500MB

    def test_database_query_performance(self):
        """Test database query performance with large datasets."""
        # Test various query patterns
        query_tests = [
            ('season_players', {'season': 2024}),
            ('team_players', {'team': 'CIN', 'season': 2024}),
            ('player_seasons', {'player': 'Joe Burrow'}),
            ('performance_range', {'min_rating': 100, 'season': 2024})
        ]

        for query_name, params in query_tests:
            with self.performance_monitor(query_name):
                result = self.db_manager.execute_query(query_name, params)

                # Performance assertions
                assert self.last_query_time < 1.0  # Max 1 second
                assert len(result) > 0  # Returns data
```text
## Optimization Strategies:

- Database query optimization with proper indexing
- Memory usage optimization for large datasets
- HTTP request batching and connection pooling
- Caching strategies for frequently accessed data
- Asynchronous processing for I/O-bound operations

## Success Criteria:

- All operations complete within acceptable time limits
- Memory usage stays within reasonable bounds
- Database queries are optimized
- Network requests are efficient
- System scales well with data volume

```text
### Template B: Edge Case and Error Handling Testing
```text
[Edge-Case-Error-Handling-Testing-Phase3] Comprehensive testing of edge cases
and error scenarios.

**Context Files:** @.cursorrules @.cursor/rules/testing-standards.mdc
@.cursor/rules/python-quality.mdc

**Current Phase:** Phase 3 (Advanced)

**Objective:** Ensure robust handling of all edge cases and error scenarios in
production.

## Edge Case Categories:

1. **Data Edge Cases:** Unusual player names, missing data, invalid formats
2. **Network Edge Cases:** Timeouts, rate limiting, connection failures
3. **Database Edge Cases:** Connection failures, constraint violations
4. **System Edge Cases:** Resource exhaustion, concurrent access
5. **User Edge Cases:** Invalid inputs, edge case parameters

## Implementation:

```python
class EdgeCaseTestSuite:
    def test_unusual_player_names(self):
        """Test handling of unusual player names."""
        edge_case_names = [
            "D'Brickashaw Ferguson",  # Apostrophe
            "Haha Clinton-Dix",       # Hyphen
            "BenJarvus Green-Ellis",  # Mixed case
            "T.J. Watt",              # Periods
            "Robert Griffin III",      # Roman numerals
            "神田川",                  # Unicode characters
        ]

        for name in edge_case_names:
            with self.subTest(name=name):
                result = self.scraper.scrape_player_season(name, 2024)
                # Should handle gracefully without crashing
                assert result is not None or self.is_valid_not_found(result)

    def test_network_failure_recovery(self):
        """Test recovery from various network failure scenarios."""
        failure_scenarios = [
            'connection_timeout',
            'read_timeout',
            'connection_refused',
            'dns_failure',
            'rate_limit_exceeded',
            'server_error_500',
            'server_error_503'
        ]

        for scenario in failure_scenarios:
            with self.mock_network_failure(scenario):
                result = self.scraper.scrape_player_season("Joe Burrow", 2024)

                # Should handle gracefully with appropriate error
                assert result.success == False
                assert scenario in result.error_type
                assert result.retry_after is not None
```text
## Error Recovery Testing:

- Retry logic with exponential backoff
- Circuit breaker pattern implementation
- Graceful degradation strategies
- Resource cleanup on failures
- User-friendly error reporting

## Success Criteria:

- All edge cases handled gracefully
- Error messages are informative and actionable
- System recovers properly from failures
- No data corruption in error scenarios
- Performance remains acceptable with errors

```text
---

## 🚀 Phase 3 Completion Validation

### Final Phase 3 Validation Prompt
```text
[Phase3-Completion-Validation] Validate that Phase 3 Advanced features are
complete and ready for Phase 4.

**Context Files:** @.cursorrules @.cursor/rules/migration-process.mdc
@.cursor/rules/testing-standards.mdc

**Current Phase:** Phase 3 (Advanced) - Completion Validation

## Validation Checklist:

- [ ] Advanced data validation catches all quality issues
- [ ] Multi-team player scenarios handled correctly
- [ ] Batch operations are robust and resumable
- [ ] Export and reporting features are comprehensive
- [ ] Performance meets production requirements
- [ ] Test coverage meets 80% minimum requirement
- [ ] Edge cases and errors handled gracefully
- [ ] User experience is excellent for complex operations

## Success Criteria:

- All validation tests pass
- Performance benchmarks meet targets
- Complex data scenarios work correctly
- Error handling is comprehensive
- Documentation covers all features
- Code quality exceeds standards

## Phase 4 Readiness:

- All features are production-ready
- Performance is optimized
- Error handling is bulletproof
- Documentation is comprehensive
- Team is confident in system stability

````

---

## 💡 Quick Reference

### Phase 3 CLI Commands

```bash
# Data validation
pfr-scraper data validate --season 2024 --fix-issues
pfr-scraper data quality-report --season 2024

# Multi-team handling
pfr-scraper data aggregate --player "Tim Boyle" --season 2024
pfr-scraper data multi-team-report --season 2024

# Batch operations
pfr-scraper batch scrape-season --year 2024 --resume
pfr-scraper batch status --session season_2024

# Export and reporting
pfr-scraper data export --season 2024 --format csv
pfr-scraper data report season-summary --season 2024
```

### Next Steps

Once Phase 3 is complete, move to
[Phase 4 Production Prompts](phase4-production-prompts.md) for final production
polish and deployment.
