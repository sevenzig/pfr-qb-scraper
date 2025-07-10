# Phase 4 Production: Prompt Templates

_Ready-to-use prompts for production polish and deployment_

## 🎯 Phase 4 Overview

**Goal:** Achieve production-ready quality and complete the migration  
**Standards:** 85% test coverage minimum, full compliance with all quality
standards  
**Success Criteria:** Production deployment ready, legacy scripts deprecated,
documentation complete

---

## 📋 Essential Context Template

````text
## Context Files:
@.cursorrules
@.cursor/rules/migration-process.mdc
@.cursor/rules/enforcement.mdc
ALL .cursor/rules/*.mdc files

**Current Phase:** Phase 4 (Production)
**Standards:** 85% test coverage minimum, full compliance required
**Focus:** Production readiness, legacy deprecation, complete documentation
```text
---

## 🔧 1. Production Quality Gates

### Template A: Comprehensive Quality Validation

````

[Production-Quality-Validation-Phase4] Achieve full production quality
compliance across all components.

## Context Files:

@.cursorrules @.cursor/rules/enforcement.mdc @.cursor/rules/python-quality.mdc
@.cursor/rules/sql-standards.mdc

**Current Phase:** Phase 4 (Production) **Standards:** 85% test coverage
minimum, full compliance required

## Objective:

Ensure all code meets the highest quality standards for production deployment.

## Quality Gates Checklist:

- [ ] All code passes mypy --strict type checking
- [ ] 85%+ test coverage with meaningful tests
- [ ] All functions have comprehensive docstrings
- [ ] Security scan passes (bandit, safety)
- [ ] Performance benchmarks meet targets
- [ ] All linting issues resolved (flake8, pylint)
- [ ] Documentation is complete and accurate
- [ ] Migration guides are tested and verified

## Implementation:

```python
class ProductionQualityGates:
    def run_comprehensive_validation(self) -> ValidationReport:
        """Run all quality gates and generate comprehensive report."""
        results = []

        # Type checking
        results.append(self.run_type_checking())

        # Test coverage
        results.append(self.check_test_coverage())

        # Security scanning
        results.append(self.run_security_scan())

        # Performance benchmarks
        results.append(self.run_performance_benchmarks())

        # Documentation validation
        results.append(self.validate_documentation())

        # Code quality checks
        results.append(self.run_code_quality_checks())

        return ValidationReport(
            passed=all(r.passed for r in results),
            results=results,
            production_ready=self.assess_production_readiness(results)
        )

    def check_test_coverage(self) -> ValidationResult:
        """Validate test coverage meets production standards."""
        coverage_report = self.generate_coverage_report()

        return ValidationResult(
            name="Test Coverage",
            passed=coverage_report.total_coverage >= 0.85,
            details=coverage_report,
            recommendations=self.get_coverage_recommendations(coverage_report)
        )
```

## CLI Commands:

````bash
pfr-scraper validate production-readiness
pfr-scraper validate security-scan
pfr-scraper validate performance-benchmarks
pfr-scraper validate documentation
```text
## Success Criteria:

- All quality gates pass
- Test coverage exceeds 85%
- Security vulnerabilities resolved
- Performance meets production requirements
- Documentation is comprehensive and accurate

```text
### Template B: Performance Optimization and Monitoring
```text
[Performance-Optimization-Monitoring-Phase4] Implement production-grade
performance optimization and monitoring.

**Context Files:** @.cursorrules @.cursor/rules/testing-standards.mdc
@.cursor/rules/python-quality.mdc

**Current Phase:** Phase 4 (Production)

**Objective:** Optimize performance for production workloads and implement
comprehensive monitoring.

## Performance Optimization Areas:

1. **Database Queries:** Optimize with proper indexing and query plans
2. **Memory Usage:** Profile and optimize memory consumption
3. **Network Requests:** Implement efficient HTTP request patterns
4. **Caching:** Strategic caching for frequently accessed data
5. **Concurrency:** Safe parallel processing where appropriate

## Monitoring Implementation:

```python
class PerformanceMonitor:
    def __init__(self):
        self.metrics = MetricsCollector()
        self.alerts = AlertManager()

    def track_operation(self, operation_name: str):
        """Decorator to track operation performance."""
        def decorator(func):
            def wrapper(*args, **kwargs):
                start_time = time.time()
                start_memory = self.get_memory_usage()

                try:
                    result = func(*args, **kwargs)
                    status = 'success'
                    return result
                except Exception as e:
                    status = 'error'
                    raise
                finally:
                    elapsed = time.time() - start_time
                    memory_used = self.get_memory_usage() - start_memory

                    self.metrics.record_operation(
                        name=operation_name,
                        duration=elapsed,
                        memory_used=memory_used,
                        status=status
                    )

                    # Check for performance alerts
                    if elapsed > self.get_threshold(operation_name):
                        self.alerts.send_performance_alert(
                            operation=operation_name,
                            duration=elapsed,
                            threshold=self.get_threshold(operation_name)
                        )

            return wrapper
        return decorator

    def generate_performance_report(self) -> PerformanceReport:
        """Generate comprehensive performance report."""
        return PerformanceReport(
            operations=self.metrics.get_operation_summaries(),
            trends=self.metrics.get_performance_trends(),
            alerts=self.alerts.get_recent_alerts(),
            recommendations=self.generate_optimization_recommendations()
        )
```text
## CLI Commands:

```bash
pfr-scraper monitor performance-report
pfr-scraper monitor health-check
pfr-scraper optimize database-queries
pfr-scraper optimize memory-usage
```text
## Success Criteria:

- All operations complete within acceptable time limits
- Memory usage is optimized for production workloads
- Database queries are fully optimized
- Monitoring provides actionable insights
- Performance alerts work correctly

```text
### Template C: Risk Mitigation Implementation
```text
[Risk-Mitigation-Phase4] Implement comprehensive risk mitigation strategies from
MIGRATION_PLAN.md.

**Context Files:** @.cursorrules @.cursor/rules/migration-process.mdc
@docs/MIGRATION_PLAN.md

**Current Phase:** Phase 4 (Production)

**Objective:** Implement all risk mitigation strategies identified in
MIGRATION_PLAN.md to ensure safe, successful migration.

## Risk Categories from MIGRATION_PLAN.md:

## Technical Risks:

1. **Data loss during migration**
   - Risk: Database corruption or data deletion during schema changes
   - Mitigation: Implement backup/restore procedures before major changes
   - Implementation: Create automated backup system with restore validation

2. **Performance regression**
   - Risk: New CLI performs worse than legacy scripts
   - Mitigation: Continuous benchmarking system with alerts
   - Implementation: Performance monitoring with regression detection

3. **Integration failures**
   - Risk: New system doesn't work with existing tools/workflows
   - Mitigation: Comprehensive integration testing
   - Implementation: Test all integration points thoroughly

## User Adoption Risks:

1. **Learning curve**
   - Risk: Users struggle to adopt new CLI interface
   - Mitigation: Interactive tutorials and comprehensive examples
   - Implementation: Built-in help system with guided workflows

2. **Workflow disruption**
   - Risk: Migration breaks existing user workflows
   - Mitigation: Backwards compatibility during transition period
   - Implementation: Wrapper scripts and migration tools

3. **Feature gaps**
   - Risk: New CLI missing functionality from legacy scripts
   - Mitigation: Comprehensive functionality audit
   - Implementation: Feature parity validation and gap analysis

## Timeline Risks:

1. **Scope creep**
   - Risk: Migration expands beyond planned scope
   - Mitigation: Strict phase boundaries and deliverables
   - Implementation: Phase gate reviews and scope validation

2. **Technical debt**
   - Risk: Accumulated technical debt slows migration
   - Mitigation: Incremental improvement strategy
   - Implementation: Continuous refactoring and code quality monitoring

3. **Resource constraints**
   - Risk: Limited time/resources for complete migration
   - Mitigation: Focus on core functionality first
   - Implementation: Priority-based feature implementation

## Risk Mitigation Implementation:

```python
class RiskMitigationManager:
    def __init__(self):
        self.backup_manager = BackupManager()
        self.performance_monitor = PerformanceMonitor()
        self.integration_tester = IntegrationTester()
        self.user_adoption_tracker = UserAdoptionTracker()

    def implement_data_protection(self):
        """Implement data loss prevention measures."""
        # Automated backup before major operations
        self.backup_manager.create_backup_schedule()

        # Validation of all data changes
        self.backup_manager.implement_change_validation()

        # Rollback procedures for failed operations
        self.backup_manager.create_rollback_procedures()

    def implement_performance_protection(self):
        """Implement performance regression prevention."""
        # Continuous performance monitoring
        self.performance_monitor.setup_continuous_monitoring()

        # Performance regression alerts
        self.performance_monitor.setup_regression_alerts()

        # Automated benchmarking
        self.performance_monitor.setup_automated_benchmarks()

    def implement_user_adoption_support(self):
        """Implement user adoption support measures."""
        # Interactive help system
        self.create_interactive_help_system()

        # Migration guides and examples
        self.create_migration_guides()

        # Backwards compatibility layer
        self.create_compatibility_layer()

    def validate_risk_mitigation(self) -> RiskAssessmentReport:
        """Validate that all risk mitigation measures are working."""
        return RiskAssessmentReport(
            data_protection=self.test_data_protection(),
            performance_protection=self.test_performance_protection(),
            user_adoption=self.test_user_adoption_support(),
            integration_safety=self.test_integration_safety()
        )
```text
## Risk Mitigation Checklist:

- [ ] **Data Backup System** - Automated backups before major operations
- [ ] **Rollback Procedures** - Tested rollback for all major changes
- [ ] **Performance Monitoring** - Continuous performance tracking
- [ ] **Regression Detection** - Automated alerts for performance regression
- [ ] **Integration Testing** - All integration points tested
- [ ] **User Migration Tools** - Tools to help users transition
- [ ] **Backwards Compatibility** - Legacy scripts work during transition
- [ ] **Feature Parity** - All legacy functionality preserved
- [ ] **Documentation** - Comprehensive migration guides
- [ ] **Support System** - Help system for migration issues

## CLI Commands:

```bash
pfr-scraper risk-mitigation status
pfr-scraper risk-mitigation backup-test
pfr-scraper risk-mitigation performance-baseline
pfr-scraper risk-mitigation integration-test
pfr-scraper risk-mitigation user-adoption-report
```text
## Success Criteria:

- All risk mitigation measures are implemented and tested
- Backup and rollback procedures work correctly
- Performance monitoring detects regressions
- Integration tests pass completely
- User adoption metrics show positive trends
- Migration can be safely rolled back if needed

```text
---

## 🗂️ 2. Legacy Migration and Deprecation

### Template A: Legacy Script Deprecation
```text
[Legacy-Script-Deprecation-Phase4] Safely deprecate legacy scripts and provide
migration path.

**Context Files:** @.cursorrules @.cursor/rules/migration-process.mdc @scripts/

**Current Phase:** Phase 4 (Production)

**Objective:** Safely deprecate all legacy scripts while providing clear
migration paths for users.

## Deprecation Strategy:

1. **Move to Legacy Directory:** Move old scripts to legacy/ directory
2. **Add Deprecation Warnings:** Clear warnings with migration instructions
3. **Create Wrapper Scripts:** Temporary bridges for smooth transition
4. **Update Documentation:** All references point to new CLI
5. **Provide Migration Tools:** Automated migration where possible

## Implementation:

```python
class LegacyDeprecationManager:
    def create_deprecation_wrapper(self, old_script: str, new_command: str):
        """Create wrapper script with deprecation warning."""
        wrapper_content = f'''#!/usr/bin/env python3
"""
DEPRECATED: This script is deprecated and will be removed in v2.0.0

This script has been replaced by the new pfr-scraper CLI tool.

OLD: python {old_script}
NEW: pfr-scraper {new_command}

For migration help, run: pfr-scraper migrate --help
"""

import warnings
import subprocess
import sys

def main():
    warnings.warn(
        f"{{old_script}} is deprecated. Use 'pfr-scraper {{new_command}}' instead.",
        DeprecationWarning,
        stacklevel=2
    )

    # Show migration instructions
    print("\\n" + "="*60)
    print("MIGRATION NOTICE")
    print("="*60)
    print(f"This script ({{old_script}}) is deprecated.")
    print(f"Please use: pfr-scraper {{new_command}}")
    print("\\nFor help with migration:")
    print("  pfr-scraper migrate --from {{old_script}}")
    print("  pfr-scraper --help")
    print("="*60 + "\\n")

    # Ask for confirmation
    response = input("Continue with deprecated script? (y/N): ")
    if response.lower() != 'y':
        print("Migration guide: https://docs.pfr-scraper.com/migration")
        sys.exit(1)

    # Execute new CLI command
    try:
        subprocess.run(['pfr-scraper'] + {{new_command}}.split(), check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing new command: {{e}}")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''

        return wrapper_content

    def generate_migration_guide(self) -> str:
        """Generate comprehensive migration guide."""
        mappings = self.get_script_mappings()

        guide = []
        guide.append("# Migration Guide: Scripts to CLI")
        guide.append("## Command Mappings")

        for old_script, new_command in mappings.items():
            guide.append(f"### {old_script}")
            guide.append(f"**OLD:** `python {old_script}`")
            guide.append(f"**NEW:** `pfr-scraper {new_command}`")
            guide.append("")

        return "\\n".join(guide)
```text
## Migration Mappings:

```text
scripts/enhanced_qb_scraper.py → pfr-scraper scrape season --year 2024
scripts/scrape_qb_data_2024.py → pfr-scraper scrape season --year 2024
scripts/populate_teams.py → pfr-scraper setup teams
scripts/robust_qb_scraper.py → pfr-scraper scrape season --year 2024 --robust
```text
## Success Criteria:

- All legacy scripts have clear deprecation warnings
- Migration path is documented and tested
- Users can easily transition to new CLI
- No breaking changes for existing workflows
- All functionality is preserved in new CLI

```text
### Template B: Migration Validation and User Acceptance
```text
[Migration-Validation-User-Acceptance-Phase4] Validate complete migration and
ensure user acceptance.

**Context Files:** @.cursorrules @.cursor/rules/migration-process.mdc
@.cursor/rules/testing-standards.mdc

**Current Phase:** Phase 4 (Production)

**Objective:** Validate that the migration is complete and users can
successfully transition to the new CLI.

## Validation Categories:

1. **Functional Equivalence:** New CLI provides all legacy functionality
2. **Performance Equivalence:** Performance meets or exceeds legacy
3. **User Experience:** CLI is intuitive and well-documented
4. **Migration Path:** Users can easily transition from old to new
5. **Data Integrity:** All data remains intact throughout migration

## User Acceptance Testing:

```python
class MigrationAcceptanceTests:
    def test_complete_user_workflows(self):
        """Test complete user workflows from start to finish."""
        workflows = [
            self.test_new_user_workflow,
            self.test_existing_user_migration,
            self.test_power_user_workflow,
            self.test_automated_workflow
        ]

        results = []
        for workflow in workflows:
            try:
                result = workflow()
                results.append(result)
            except Exception as e:
                results.append(WorkflowResult(
                    name=workflow.__name__,
                    success=False,
                    error=str(e)
                ))

        return AcceptanceTestResult(
            passed=all(r.success for r in results),
            workflow_results=results,
            user_feedback=self.collect_user_feedback()
        )

    def test_new_user_workflow(self) -> WorkflowResult:
        """Test workflow for completely new users."""
        # New user discovers CLI
        help_result = run_cli(['--help'])
        assert help_result.exit_code == 0
        assert 'scrape' in help_result.output

        # New user runs first scrape
        scrape_result = run_cli(['scrape', 'player', '--name', 'Joe Burrow', '--season', '2024'])
        assert scrape_result.exit_code == 0
        assert 'Joe Burrow' in scrape_result.output

        # New user explores other features
        validate_result = run_cli(['data', 'validate', '--season', '2024'])
        assert validate_result.exit_code == 0

        return WorkflowResult(
            name="new_user_workflow",
            success=True,
            message="New user can successfully use CLI"
        )

    def test_existing_user_migration(self) -> WorkflowResult:
        """Test migration path for existing script users."""
        # User tries to run old script
        old_script_result = run_command(['python', 'scripts/enhanced_qb_scraper.py'])

        # Should show deprecation warning
        assert 'deprecated' in old_script_result.output.lower()
        assert 'pfr-scraper' in old_script_result.output

        # User follows migration instructions
        migration_help = run_cli(['migrate', '--from', 'enhanced_qb_scraper.py'])
        assert migration_help.exit_code == 0
        assert 'scrape season' in migration_help.output

        return WorkflowResult(
            name="existing_user_migration",
            success=True,
            message="Existing users can successfully migrate"
        )
```text
## Success Criteria:

- All user workflows complete successfully
- Migration path is clear and well-documented
- Performance meets or exceeds legacy systems
- User feedback is positive
- Data integrity is maintained
- No critical issues found in acceptance testing

```text
---

## 📚 3. Documentation and Release

### Template A: Complete Documentation System
```text
[Complete-Documentation-System-Phase4] Create comprehensive documentation for
production release.

**Context Files:** @.cursorrules @.cursor/rules/cli-specific.mdc @docs/

**Current Phase:** Phase 4 (Production)

**Objective:** Create comprehensive, user-friendly documentation that covers all
aspects of the system.

## Documentation Structure:

1. **User Guide:** Complete guide for end users
2. **API Documentation:** Comprehensive API reference
3. **Migration Guide:** Step-by-step migration instructions
4. **Developer Guide:** Guide for contributing developers
5. **Troubleshooting:** Common issues and solutions

## Implementation:

```python
class DocumentationGenerator:
    def generate_user_guide(self) -> str:
        """Generate comprehensive user guide."""
        sections = [
            self.generate_getting_started(),
            self.generate_basic_usage(),
            self.generate_advanced_features(),
            self.generate_configuration_guide(),
            self.generate_troubleshooting()
        ]

        return self.compile_sections(sections)

    def generate_api_reference(self) -> str:
        """Generate complete API reference from docstrings."""
        modules = [
            'src.cli',
            'src.core',
            'src.operations',
            'src.database',
            'src.models'
        ]

        api_docs = []
        for module in modules:
            module_doc = self.extract_module_documentation(module)
            api_docs.append(module_doc)

        return self.compile_api_docs(api_docs)

    def generate_migration_guide(self) -> str:
        """Generate detailed migration guide."""
        return f"""
# Migration Guide: From Scripts to CLI

## Overview
This guide helps you migrate from the legacy scripts to the new pfr-scraper CLI tool.

## Quick Migration
For most users, the migration is straightforward:

### Common Migrations
{self.generate_migration_table()}

### Step-by-Step Migration
{self.generate_migration_steps()}

### Troubleshooting
{self.generate_migration_troubleshooting()}
"""
```text
## Documentation Requirements:

- All CLI commands documented with examples
- All configuration options explained
- All error messages documented with solutions
- Performance characteristics documented
- Security considerations documented
- Deployment instructions provided

## Success Criteria:

- Documentation covers all features comprehensively
- Examples work as written
- Migration guides are tested and accurate
- Troubleshooting covers common issues
- Documentation is easily navigable

```text
### Template B: Release Preparation and Deployment
```text
[Release-Preparation-Deployment-Phase4] Prepare for production release and
deployment.

**Context Files:** @.cursorrules @.cursor/rules/enforcement.mdc

**Current Phase:** Phase 4 (Production)

**Objective:** Prepare all components for production release and deployment.

## Release Preparation Checklist:

- [ ] All quality gates pass
- [ ] Documentation is complete and accurate
- [ ] Migration guides are tested
- [ ] Performance benchmarks meet targets
- [ ] Security scans pass
- [ ] Deployment procedures are documented
- [ ] Rollback procedures are tested
- [ ] Monitoring is configured

## Deployment Strategy:

```python
class ReleaseManager:
    def prepare_release(self, version: str) -> ReleaseResult:
        """Prepare complete release package."""
        # Run all quality gates
        quality_result = self.run_quality_gates()
        if not quality_result.passed:
            return ReleaseResult(
                success=False,
                message="Quality gates failed",
                details=quality_result
            )

        # Generate release package
        package = self.create_release_package(version)

        # Validate deployment
        deployment_result = self.validate_deployment(package)
        if not deployment_result.success:
            return ReleaseResult(
                success=False,
                message="Deployment validation failed",
                details=deployment_result
            )

        return ReleaseResult(
            success=True,
            message=f"Release {version} ready for deployment",
            package=package
        )

    def create_release_package(self, version: str) -> ReleasePackage:
        """Create complete release package."""
        return ReleasePackage(
            version=version,
            source_code=self.package_source_code(),
            documentation=self.package_documentation(),
            tests=self.package_tests(),
            configuration=self.package_configuration(),
            deployment_scripts=self.package_deployment_scripts()
        )

    def validate_deployment(self, package: ReleasePackage) -> DeploymentResult:
        """Validate deployment package."""
        # Test installation
        install_result = self.test_installation(package)
        if not install_result.success:
            return install_result

        # Test functionality
        function_result = self.test_functionality(package)
        if not function_result.success:
            return function_result

        # Test performance
        performance_result = self.test_performance(package)
        if not performance_result.success:
            return performance_result

        return DeploymentResult(
            success=True,
            message="Deployment package validated successfully"
        )
```text
## CLI Commands:

```bash
pfr-scraper release prepare --version 1.0.0
pfr-scraper release validate --package release-1.0.0.tar.gz
pfr-scraper release deploy --environment production
```text
## Success Criteria:

- All quality gates pass
- Release package is complete and tested
- Deployment procedures are documented and tested
- Rollback procedures are available
- Monitoring is configured and working
- Team is confident in production readiness

```text
---

## 🚀 Final Migration Completion

### Migration Completion Validation
```text
[Migration-Completion-Validation-Phase4] Final validation that migration is
complete and successful.

**Context Files:** @.cursorrules ALL .cursor/rules/\*.mdc files

**Current Phase:** Phase 4 (Production) - Final Validation

**Objective:** Comprehensive validation that the migration from scripts to CLI
is complete and successful.

## Final Validation Checklist:

- [ ] All legacy scripts are deprecated with clear migration paths
- [ ] New CLI provides all functionality of legacy scripts
- [ ] Performance meets or exceeds legacy systems
- [ ] Data integrity is maintained throughout migration
- [ ] User acceptance testing is positive
- [ ] Documentation is complete and accurate
- [ ] Deployment is successful
- [ ] Monitoring is operational

## Success Criteria:

- Users can successfully complete all workflows using new CLI
- Performance meets production requirements
- All data remains intact and accessible
- Documentation covers all use cases
- Team is confident in system stability
- Legacy scripts can be safely removed

## Post-Migration Tasks:

- Monitor system performance in production
- Gather user feedback and address issues
- Continue iterative improvements
- Plan for future enhancements
- Maintain documentation and support materials

````

---

## 💡 Quick Reference

### Phase 4 Quality Commands

```bash
# Production quality validation
pfr-scraper validate production-readiness
pfr-scraper validate security-scan
pfr-scraper validate performance-benchmarks

# Legacy migration
pfr-scraper migrate --from enhanced_qb_scraper.py
pfr-scraper migrate validate-all

# Release preparation
pfr-scraper release prepare --version 1.0.0
pfr-scraper release validate --package release-1.0.0.tar.gz
```

### Migration Success Metrics

- **Quality:** 85%+ test coverage, all quality gates pass
- **Performance:** Within 10% of legacy performance
- **User Satisfaction:** Positive feedback from user acceptance testing
- **Documentation:** Complete and accurate documentation
- **Deployment:** Successful production deployment

## 🎉 Migration Complete!

Once Phase 4 is complete, the migration from scattered scripts to a unified CLI
architecture is finished. The system is production-ready with:

✅ **Unified CLI** - Single entry point for all operations  
✅ **High Quality** - 85%+ test coverage, comprehensive validation  
✅ **Great UX** - Intuitive commands, helpful error messages  
✅ **Production Ready** - Monitoring, documentation, deployment  
✅ **Backwards Compatible** - Clear migration path from legacy scripts

**Congratulations on completing the migration!** 🚀
