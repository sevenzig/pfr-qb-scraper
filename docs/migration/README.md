# Migration Prompt Templates

This directory contains comprehensive prompt templates for migrating the NFL QB
scraper from scattered scripts to a unified CLI architecture.

## 📁 Directory Structure

````text
docs/migration/
├── README.md                    # This file - overview and usage guide
├── phase1-foundation-prompts.md # Phase 1: CLI skeleton and architecture
├── phase2-core-prompts.md       # Phase 2: Scraper consolidation
├── phase3-advanced-prompts.md   # Phase 3: Advanced data management
└── phase4-production-prompts.md # Phase 4: Production polish
```text
## 🎯 How to Use These Templates

### 1. **Choose Your Phase**

Identify which migration phase you're working on:

- **Phase 1:** Building CLI foundation and architecture
- **Phase 2:** Consolidating scrapers and implementing core commands
- **Phase 3:** Adding advanced features and data management
- **Phase 4:** Production polish and deployment

### 2. **Find the Right Template**

Each phase file contains specific templates for common tasks:

- **Architecture templates** for setting up systems
- **Implementation templates** for building features
- **Testing templates** for validation
- **Documentation templates** for user guides

### 3. **Customize the Context**

Always include the essential context template from each phase:

```text
## Context Files:
@.cursorrules
@.cursor/rules/migration-process.mdc
@.cursor/rules/[relevant-specific].mdc

**Current Phase:** Phase [X] ([Name])
**Standards:** [X]% test coverage minimum
```text
### 4. **Use the Templates**

- **Copy** the template you need
- **Customize** it for your specific task
- **Paste** into Cursor AI
- **Execute** the resulting implementation

## 🚀 Quick Start Guide

### Starting Phase 1: Foundation

```bash
# Copy this template to begin Phase 1
[CLI-Architecture-Phase1] Create the foundational CLI architecture for NFL QB scraper migration.

## Context Files:
@.cursorrules
@.cursor/rules/migration-process.mdc
@.cursor/rules/cli-specific.mdc

**Current Phase:** Phase 1 (Foundation)
**Standards:** 60% test coverage minimum, backwards compatibility required

## Objective:
Set up the basic CLI structure with proper module organization and command routing.

# [Continue with specific requirements...]
```text
### Moving to Phase 2: Core

```bash
# Use this template when Phase 1 is complete
[Core-Scraper-Architecture-Phase2] Create unified CoreScraper that consolidates all existing scrapers.

## Context Files:
@.cursorrules
@.cursor/rules/migration-process.mdc
@.cursor/rules/python-quality.mdc

**Current Phase:** Phase 2 (Core)
**Standards:** 70% test coverage minimum, functional equivalence required

# [Continue with scraper consolidation...]
```text
## 📋 Template Categories

### 🏗️ **Architecture Templates**

- CLI structure and command routing
- Module organization and dependency injection
- Configuration system design
- Database architecture

### 🔧 **Implementation Templates**

- Scraper consolidation and optimization
- CLI command implementation
- Data validation and quality assurance
- Batch operations and session management

### 🧪 **Testing Templates**

- Unit and integration testing
- Performance benchmarking
- Equivalence testing
- Edge case and error handling

### 📚 **Documentation Templates**

- User guides and API documentation
- Migration guides and troubleshooting
- Help systems and error messages
- Release notes and deployment guides

## 🎨 Template Customization

### Essential Elements

Every template includes:

- **Context Files:** Relevant rule files to reference
- **Current Phase:** Which migration phase you're in
- **Standards:** Quality requirements for the phase
- **Objective:** Clear goal for the task
- **Success Criteria:** How to validate completion

### Customization Points

Modify these sections for your specific needs:

- **Objective:** Adjust for your specific task
- **Requirements:** Add or modify technical requirements
- **Implementation:** Customize the approach
- **Testing:** Adjust testing strategy
- **Success Criteria:** Define what success looks like

## 🔄 Phase Progression

### Phase 1: Foundation (60% coverage)

- ✅ CLI skeleton and command routing
- ✅ Configuration system
- ✅ Help system and error handling
- ✅ Testing framework setup

### Phase 2: Core (70% coverage)

- ✅ Scraper consolidation
- ✅ Core CLI commands
- ✅ Data validation
- ✅ Database integration

### Phase 3: Advanced (80% coverage)

- ✅ Advanced data management
- ✅ Multi-team player handling
- ✅ Batch operations
- ✅ Export and reporting

### Phase 4: Production (85% coverage)

- ✅ Production quality gates
- ✅ Performance optimization
- ✅ Legacy deprecation
- ✅ Complete documentation

## 📊 Success Metrics

### Phase Completion Indicators

- **Quality:** Test coverage meets phase requirements
- **Functionality:** All features work as specified
- **Performance:** Meets or exceeds legacy performance
- **Documentation:** Complete and accurate documentation
- **User Experience:** Positive feedback from testing

### Migration Success Metrics

- **Unified Interface:** Single CLI entry point
- **Feature Parity:** All legacy functionality preserved
- **Performance:** Within 10% of legacy performance
- **Quality:** 85%+ test coverage in production
- **User Adoption:** Smooth transition from legacy scripts

## 💡 Tips for Success

### 🎯 **Be Specific**

- Use specific player names and seasons in examples
- Reference actual file names and paths
- Include concrete success criteria

### 📋 **Follow the Process**

- Complete each phase before moving to the next
- Use the validation templates to verify completion
- Maintain backwards compatibility until Phase 4

### 🔧 **Customize for Your Context**

- Adjust templates for your specific codebase
- Include relevant error scenarios you've encountered
- Add project-specific requirements

### 🧪 **Test Thoroughly**

- Use the testing templates for comprehensive coverage
- Include edge cases and error scenarios
- Validate equivalence with legacy systems

### 📚 **Document Everything**

- Use documentation templates for consistency
- Include examples and troubleshooting guides
- Keep migration guides up to date

## 🚨 Common Pitfalls

### ❌ **Avoid These Mistakes**

- **Skipping phases** - Each phase builds on the previous
- **Ignoring backwards compatibility** - Critical until Phase 4
- **Insufficient testing** - Use phase-appropriate coverage requirements
- **Poor error handling** - Always include user-friendly error messages
- **Incomplete documentation** - Document as you build

### ✅ **Best Practices**

- **Start with analysis** - Understand existing systems first
- **Use equivalence testing** - Validate against known good data
- **Implement gradually** - Small, incremental changes
- **Get user feedback** - Test with actual users throughout
- **Monitor performance** - Track metrics at each phase

## 🔗 Related Resources

### Project Documentation

- [Migration Plan](../MIGRATION_PLAN.md) - Overall migration strategy
- [Migration Summary](../MIGRATION_SUMMARY.md) - Phase descriptions
- [Project Rules](.cursorrules) - Coding standards and practices

### Cursor Rules

- [Migration Process](.cursor/rules/migration-process.mdc) - Phase compliance
- [Python Quality](.cursor/rules/python-quality.mdc) - Code standards
- [CLI Specific](.cursor/rules/cli-specific.mdc) - CLI best practices
- [Testing Standards](.cursor/rules/testing-standards.mdc) - Testing
  requirements

### Development Tools

- [Prompt Strategy Guide](.cursor/rules/prompt-strategy-guide.mdc) -
  Comprehensive prompting guide
- [Anti-Patterns](.cursor/rules/anti-patterns.mdc) - Common mistakes to avoid
- [Conflict Resolution](.cursor/rules/conflict-resolution.mdc) - Handling rule
  conflicts

---

## 📊 Success Metrics Validation Template

### Universal Success Metrics Template

_Use this template in any phase to validate deliverables against
MIGRATION_PLAN.md success metrics_

````

[Success-Metrics-Validation] Validate phase deliverables against success metrics
from MIGRATION_PLAN.md.

## Context Files:

@.cursorrules @docs/MIGRATION_PLAN.md @docs/MIGRATION_SUMMARY.md

**Current Phase:** [Phase 1/2/3/4] ([Phase Name])

## Objective:

Validate that phase deliverables meet the success metrics defined in
MIGRATION_PLAN.md.

## Success Metrics from MIGRATION_PLAN.md:

## Quality Improvements:

- [ ] **Single entry point** → One command to rule them all
  - Validation: `python -m pfr_scraper --help` shows unified interface
  - Test: All functionality accessible through single entry point

- [ ] **90% test coverage** → Core modules fully tested
  - Validation: Coverage report shows 85%+ (Phase 4) or phase-appropriate
    coverage
  - Test: All critical paths have comprehensive test coverage

- [ ] **Consistent error handling** → Standardized across all operations
  - Validation: All errors follow same pattern with user-friendly messages
  - Test: Error scenarios produce consistent, helpful output

- [ ] **Comprehensive logging** → Clear operational visibility
  - Validation: All operations log with structured format and context
  - Test: Logs provide actionable debugging information

## User Experience:

- [ ] **5-minute setup** → New users can get started quickly
  - Validation: New user can complete setup in under 5 minutes
  - Test: Time setup process with fresh environment

- [ ] **Self-documenting** → Built-in help and examples
  - Validation: Help system provides clear guidance with examples
  - Test: Users can discover functionality through help system

- [ ] **Robust error recovery** → Graceful handling of failures
  - Validation: System recovers from failures without data loss
  - Test: Failure scenarios handled gracefully with recovery options

- [ ] **Progress tracking** → Users know what's happening
  - Validation: Long operations show progress with time estimates
  - Test: All operations >30 seconds have progress indication

## Developer Experience:

- [ ] **Modular architecture** → Easy to extend and modify
  - Validation: New features can be added without major refactoring
  - Test: Add sample feature to validate extensibility

- [ ] **Type safety** → Full type hints throughout
  - Validation: All code passes mypy --strict type checking
  - Test: Type checker validates all function signatures

- [ ] **Automated testing** → CI/CD pipeline with tests
  - Validation: All tests run automatically on code changes
  - Test: CI/CD pipeline catches regressions

- [ ] **Code quality** → Linting, formatting, complexity checks
  - Validation: All code passes quality gates (flake8, black, etc.)
  - Test: Code quality metrics meet project standards

## Phase-Specific Success Metrics:

## Phase 1 (Foundation):

- [ ] **CLI help system is intuitive** → Users understand available commands
- [ ] **Command routing is extensible** → New commands can be added easily
- [ ] **Configuration system works** → All settings load from multiple sources
- [ ] **Zero impact on existing workflows** → All legacy scripts still work

## Phase 2 (Core):

- [ ] **Scraper consolidation complete** → Single CoreScraper replaces all
      legacy scrapers
- [ ] **Functional equivalence proven** → New scraper produces same results as
      best legacy scraper
- [ ] **Performance within 10%** → No significant performance regression
- [ ] **CLI commands work intuitively** → Users can accomplish tasks through CLI

## Phase 3 (Advanced):

- [ ] **Multi-team handling works** → Tim Boyle scenario handled correctly
- [ ] **Data validation comprehensive** → All data quality issues caught
- [ ] **Batch operations robust** → Large datasets processed efficiently
- [ ] **Advanced features complete** → Export, aggregation, validation work

## Phase 4 (Production):

- [ ] **Production quality achieved** → All quality gates pass
- [ ] **Legacy deprecation complete** → Old scripts moved to legacy/ with
      warnings
- [ ] **Documentation complete** → Users can migrate successfully
- [ ] **Deployment ready** → System ready for production use

## Validation Implementation:

```python
class SuccessMetricsValidator:
    def __init__(self, phase: str):
        self.phase = phase
        self.metrics = self.get_phase_metrics(phase)

    def validate_quality_improvements(self) -> Dict[str, bool]:
        """Validate quality improvement metrics."""
        return {
            'single_entry_point': self.test_single_entry_point(),
            'test_coverage': self.test_coverage_target(),
            'error_handling': self.test_error_handling_consistency(),
            'logging': self.test_logging_comprehensiveness()
        }

    def validate_user_experience(self) -> Dict[str, bool]:
        """Validate user experience metrics."""
        return {
            'quick_setup': self.test_setup_time(),
            'self_documenting': self.test_help_system_quality(),
            'error_recovery': self.test_error_recovery(),
            'progress_tracking': self.test_progress_indication()
        }

    def validate_developer_experience(self) -> Dict[str, bool]:
        """Validate developer experience metrics."""
        return {
            'modular_architecture': self.test_extensibility(),
            'type_safety': self.test_type_checking(),
            'automated_testing': self.test_ci_cd_pipeline(),
            'code_quality': self.test_code_quality_gates()
        }

    def generate_success_report(self) -> SuccessReport:
        """Generate comprehensive success metrics report."""
        quality_results = self.validate_quality_improvements()
        ux_results = self.validate_user_experience()
        dx_results = self.validate_developer_experience()

        return SuccessReport(
            phase=self.phase,
            quality_improvements=quality_results,
            user_experience=ux_results,
            developer_experience=dx_results,
            overall_success=self.calculate_overall_success(
                quality_results, ux_results, dx_results
            ),
            recommendations=self.generate_recommendations()
        )
```

## CLI Commands:

````bash
pfr-scraper validate success-metrics --phase [1/2/3/4]
pfr-scraper validate success-metrics --all
pfr-scraper validate success-metrics --report
```text
## Success Criteria:

- All applicable success metrics pass for the current phase
- Overall success rate >95% for phase completion
- User experience metrics show positive trends
- Developer experience metrics meet project standards
- Any failures have clear remediation plans

```text
---

## 🎉 Getting Started

1. **Read the Migration Plan** - Understand the overall strategy
2. **Choose your starting phase** - Usually Phase 1 unless continuing
3. **Select the appropriate template** - Match your current task
4. **Customize the template** - Add your specific requirements
5. **Execute with Cursor AI** - Use the customized prompt
6. **Validate the results** - Use the validation templates
7. **Move to the next task** - Continue systematically

Remember: The goal is to transform scattered scripts into a professional, maintainable CLI tool while preserving all existing functionality and maintaining the highest code quality standards.

**Good luck with your migration!** 🚀
````
