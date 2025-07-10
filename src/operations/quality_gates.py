#!/usr/bin/env python3
"""
Production Quality Gates for NFL QB Data Scraping System
Comprehensive validation system for production readiness
"""

import subprocess
import sys
import os
import time
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Union, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import json
import importlib.util

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from config.config import config
except ImportError:
    config = None

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of a single validation check"""
    name: str
    passed: bool
    details: Dict[str, Any]
    recommendations: List[str]
    execution_time: float
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'name': self.name,
            'passed': self.passed,
            'details': self.details,
            'recommendations': self.recommendations,
            'execution_time': self.execution_time,
            'error_message': self.error_message
        }


@dataclass
class QualityReport:
    """Comprehensive quality validation report"""
    timestamp: datetime
    overall_passed: bool
    total_checks: int
    passed_checks: int
    failed_checks: int
    results: List[ValidationResult]
    production_ready: bool
    summary: str
    
    def get_pass_rate(self) -> float:
        """Calculate overall pass rate"""
        if self.total_checks == 0:
            return 0.0
        return self.passed_checks / self.total_checks * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'overall_passed': self.overall_passed,
            'total_checks': self.total_checks,
            'passed_checks': self.passed_checks,
            'failed_checks': self.failed_checks,
            'pass_rate': self.get_pass_rate(),
            'production_ready': self.production_ready,
            'summary': self.summary,
            'results': [result.to_dict() for result in self.results]
        }


class ProductionQualityGates:
    """Production quality gates validation system"""
    
    def __init__(self):
        """Initialize quality gates system"""
        self.project_root = Path(__file__).parent.parent.parent
        self.src_dir = self.project_root / "src"
        self.tests_dir = self.project_root / "tests"
        self.logs_dir = self.project_root / "logs"
        
        # Create logs directory if it doesn't exist
        self.logs_dir.mkdir(exist_ok=True)
    
    def run_comprehensive_validation(self) -> QualityReport:
        """Run all quality gates and generate comprehensive report"""
        logger.info("Starting comprehensive production quality validation")
        
        start_time = time.time()
        results = []
        
        # Run all validation checks
        validation_checks = [
            self._check_test_coverage,
            self._check_type_safety,
            self._check_code_quality,
            self._check_security,
            self._check_documentation,
            self._check_performance,
            self._check_cli_functionality,
            self._check_data_integrity,
            self._check_error_handling,
            self._check_configuration
        ]
        
        for check_func in validation_checks:
            try:
                result = check_func()
                results.append(result)
                logger.info(f"✓ {result.name}: {'PASSED' if result.passed else 'FAILED'}")
            except Exception as e:
                logger.error(f"✗ {check_func.__name__} failed: {e}")
                results.append(ValidationResult(
                    name=check_func.__name__.replace('_', ' ').title(),
                    passed=False,
                    details={'error': str(e)},
                    recommendations=['Fix the validation check implementation'],
                    execution_time=0.0,
                    error_message=str(e)
                ))
        
        # Calculate overall results
        total_checks = len(results)
        passed_checks = sum(1 for r in results if r.passed)
        failed_checks = total_checks - passed_checks
        overall_passed = failed_checks == 0
        
        # Assess production readiness
        production_ready = self._assess_production_readiness(results)
        
        # Generate summary
        summary = self._generate_summary(results, overall_passed, production_ready)
        
        execution_time = time.time() - start_time
        
        report = QualityReport(
            timestamp=datetime.now(),
            overall_passed=overall_passed,
            total_checks=total_checks,
            passed_checks=passed_checks,
            failed_checks=failed_checks,
            results=results,
            production_ready=production_ready,
            summary=summary
        )
        
        logger.info(f"Quality validation completed in {execution_time:.2f}s")
        logger.info(f"Overall result: {'PASSED' if overall_passed else 'FAILED'}")
        logger.info(f"Production ready: {'YES' if production_ready else 'NO'}")
        
        return report
    
    def _check_test_coverage(self) -> ValidationResult:
        """Validate test coverage meets production standards"""
        start_time = time.time()
        
        try:
            # Run pytest with coverage
            result = subprocess.run([
                sys.executable, '-m', 'pytest', 'tests/', 
                '--cov=src', '--cov-report=json', '--cov-report=term-missing',
                '--quiet'
            ], capture_output=True, text=True, cwd=self.project_root)
            
            # Parse coverage report
            coverage_data = json.loads(result.stdout.split('JSON report written to')[0])
            total_coverage = coverage_data['totals']['percent_covered']
            
            passed = total_coverage >= 85.0
            recommendations = []
            
            if not passed:
                recommendations.append(f"Increase test coverage from {total_coverage:.1f}% to at least 85%")
                recommendations.append("Add tests for uncovered modules and functions")
            
            return ValidationResult(
                name="Test Coverage",
                passed=passed,
                details={
                    'total_coverage': total_coverage,
                    'target_coverage': 85.0,
                    'missing_lines': coverage_data.get('missing_lines', []),
                    'pytest_output': result.stdout
                },
                recommendations=recommendations,
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            return ValidationResult(
                name="Test Coverage",
                passed=False,
                details={'error': str(e)},
                recommendations=['Install pytest and pytest-cov', 'Ensure tests directory exists'],
                execution_time=time.time() - start_time,
                error_message=str(e)
            )
    
    def _check_type_safety(self) -> ValidationResult:
        """Check type safety with mypy"""
        start_time = time.time()
        
        try:
            # Run mypy type checking
            result = subprocess.run([
                sys.executable, '-m', 'mypy', 'src/', 
                '--ignore-missing-imports', '--no-strict-optional'
            ], capture_output=True, text=True, cwd=self.project_root)
            
            passed = result.returncode == 0
            recommendations = []
            
            if not passed:
                recommendations.append("Fix type annotation issues")
                recommendations.append("Add proper type hints to all functions")
                recommendations.append("Install missing type stubs")
            
            return ValidationResult(
                name="Type Safety",
                passed=passed,
                details={
                    'mypy_output': result.stdout,
                    'mypy_errors': result.stderr,
                    'return_code': result.returncode
                },
                recommendations=recommendations,
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            return ValidationResult(
                name="Type Safety",
                passed=False,
                details={'error': str(e)},
                recommendations=['Install mypy', 'Configure mypy properly'],
                execution_time=time.time() - start_time,
                error_message=str(e)
            )
    
    def _check_code_quality(self) -> ValidationResult:
        """Check code quality with linting tools"""
        start_time = time.time()
        
        try:
            # Run flake8
            result = subprocess.run([
                sys.executable, '-m', 'flake8', 'src/', 
                '--max-line-length=88', '--ignore=E203,W503'
            ], capture_output=True, text=True, cwd=self.project_root)
            
            passed = result.returncode == 0
            recommendations = []
            
            if not passed:
                recommendations.append("Fix flake8 linting issues")
                recommendations.append("Follow PEP 8 style guidelines")
                recommendations.append("Use black for code formatting")
            
            return ValidationResult(
                name="Code Quality",
                passed=passed,
                details={
                    'flake8_output': result.stdout,
                    'flake8_errors': result.stderr,
                    'return_code': result.returncode
                },
                recommendations=recommendations,
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            return ValidationResult(
                name="Code Quality",
                passed=False,
                details={'error': str(e)},
                recommendations=['Install flake8', 'Configure linting properly'],
                execution_time=time.time() - start_time,
                error_message=str(e)
            )
    
    def _check_security(self) -> ValidationResult:
        """Check for security vulnerabilities"""
        start_time = time.time()
        
        try:
            # Run bandit security scan
            result = subprocess.run([
                sys.executable, '-m', 'bandit', '-r', 'src/', 
                '-f', 'json', '-ll'
            ], capture_output=True, text=True, cwd=self.project_root)
            
            # Parse bandit results
            if result.stdout.strip():
                security_issues = json.loads(result.stdout)
                high_issues = [i for i in security_issues if i['issue_severity'] == 'HIGH']
                medium_issues = [i for i in security_issues if i['issue_severity'] == 'MEDIUM']
            else:
                high_issues = []
                medium_issues = []
            
            passed = len(high_issues) == 0
            recommendations = []
            
            if high_issues:
                recommendations.append("Fix high severity security issues")
                for issue in high_issues:
                    recommendations.append(f"  - {issue['issue_text']} in {issue['filename']}")
            
            if medium_issues:
                recommendations.append("Review medium severity security issues")
            
            return ValidationResult(
                name="Security Scan",
                passed=passed,
                details={
                    'high_issues': len(high_issues),
                    'medium_issues': len(medium_issues),
                    'total_issues': len(high_issues) + len(medium_issues),
                    'bandit_output': result.stdout
                },
                recommendations=recommendations,
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            return ValidationResult(
                name="Security Scan",
                passed=False,
                details={'error': str(e)},
                recommendations=['Install bandit', 'Configure security scanning'],
                execution_time=time.time() - start_time,
                error_message=str(e)
            )
    
    def _check_documentation(self) -> ValidationResult:
        """Check documentation completeness"""
        start_time = time.time()
        
        try:
            # Check for docstrings in Python files
            python_files = list(self.src_dir.rglob("*.py"))
            files_with_docstrings = 0
            total_functions = 0
            functions_with_docstrings = 0
            
            for py_file in python_files:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Check if file has docstring
                    if '"""' in content or "'''" in content:
                        files_with_docstrings += 1
                    
                    # Count functions and their docstrings
                    lines = content.split('\n')
                    for line in lines:
                        if line.strip().startswith('def '):
                            total_functions += 1
                            # Simple check for docstring after function definition
                            func_index = lines.index(line)
                            for next_line in lines[func_index + 1:]:
                                if next_line.strip().startswith('"""') or next_line.strip().startswith("'''"):
                                    functions_with_docstrings += 1
                                    break
                                elif next_line.strip() and not next_line.strip().startswith('#'):
                                    break
            
            file_doc_coverage = files_with_docstrings / len(python_files) if python_files else 0
            function_doc_coverage = functions_with_docstrings / total_functions if total_functions else 0
            
            passed = file_doc_coverage >= 0.8 and function_doc_coverage >= 0.7
            recommendations = []
            
            if file_doc_coverage < 0.8:
                recommendations.append(f"Increase file documentation coverage from {file_doc_coverage:.1%} to 80%")
            
            if function_doc_coverage < 0.7:
                recommendations.append(f"Increase function documentation coverage from {function_doc_coverage:.1%} to 70%")
            
            return ValidationResult(
                name="Documentation",
                passed=passed,
                details={
                    'files_checked': len(python_files),
                    'files_with_docstrings': files_with_docstrings,
                    'file_doc_coverage': file_doc_coverage,
                    'total_functions': total_functions,
                    'functions_with_docstrings': functions_with_docstrings,
                    'function_doc_coverage': function_doc_coverage
                },
                recommendations=recommendations,
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            return ValidationResult(
                name="Documentation",
                passed=False,
                details={'error': str(e)},
                recommendations=['Fix documentation validation'],
                execution_time=time.time() - start_time,
                error_message=str(e)
            )
    
    def _check_performance(self) -> ValidationResult:
        """Check performance benchmarks"""
        start_time = time.time()
        
        try:
            # Import and test core components
            from core.scraper import CoreScraper
            from operations.data_manager import DataManager
            from operations.validation_ops import ValidationEngine
            
            # Performance benchmarks
            benchmarks = {}
            
            # Test CoreScraper initialization
            scraper_start = time.time()
            scraper = CoreScraper(rate_limit_delay=0.1)
            benchmarks['scraper_init'] = time.time() - scraper_start
            
            # Test DataManager initialization
            dm_start = time.time()
            data_manager = DataManager()
            benchmarks['data_manager_init'] = time.time() - dm_start
            
            # Test ValidationEngine initialization
            ve_start = time.time()
            validation_engine = ValidationEngine()
            benchmarks['validation_engine_init'] = time.time() - ve_start
            
            # Performance thresholds
            thresholds = {
                'scraper_init': 1.0,
                'data_manager_init': 0.5,
                'validation_engine_init': 0.5
            }
            
            passed = all(benchmarks[k] <= thresholds[k] for k in benchmarks)
            recommendations = []
            
            for benchmark, time_taken in benchmarks.items():
                if time_taken > thresholds[benchmark]:
                    recommendations.append(f"Optimize {benchmark} (took {time_taken:.3f}s, threshold: {thresholds[benchmark]}s)")
            
            return ValidationResult(
                name="Performance",
                passed=passed,
                details={
                    'benchmarks': benchmarks,
                    'thresholds': thresholds
                },
                recommendations=recommendations,
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            return ValidationResult(
                name="Performance",
                passed=False,
                details={'error': str(e)},
                recommendations=['Fix performance validation', 'Ensure core components are available'],
                execution_time=time.time() - start_time,
                error_message=str(e)
            )
    
    def _check_cli_functionality(self) -> ValidationResult:
        """Check CLI functionality"""
        start_time = time.time()
        
        try:
            # Test CLI help
            result = subprocess.run([
                sys.executable, 'src/cli/cli_main.py', '--help'
            ], capture_output=True, text=True, cwd=self.project_root)
            
            passed = result.returncode == 0
            recommendations = []
            
            if not passed:
                recommendations.append("Fix CLI help command")
                recommendations.append("Ensure CLI entry point is working")
            
            # Test specific commands
            commands_to_test = ['scrape', 'data', 'batch', 'validate']
            working_commands = 0
            
            for cmd in commands_to_test:
                try:
                    cmd_result = subprocess.run([
                        sys.executable, 'src/cli/cli_main.py', cmd, '--help'
                    ], capture_output=True, text=True, cwd=self.project_root, timeout=10)
                    if cmd_result.returncode == 0:
                        working_commands += 1
                except:
                    pass
            
            command_coverage = working_commands / len(commands_to_test)
            
            if command_coverage < 1.0:
                recommendations.append(f"Fix CLI commands (only {command_coverage:.1%} working)")
            
            return ValidationResult(
                name="CLI Functionality",
                passed=passed and command_coverage >= 0.8,
                details={
                    'help_working': passed,
                    'commands_tested': len(commands_to_test),
                    'working_commands': working_commands,
                    'command_coverage': command_coverage,
                    'cli_output': result.stdout
                },
                recommendations=recommendations,
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            return ValidationResult(
                name="CLI Functionality",
                passed=False,
                details={'error': str(e)},
                recommendations=['Fix CLI validation', 'Ensure CLI is properly configured'],
                execution_time=time.time() - start_time,
                error_message=str(e)
            )
    
    def _check_data_integrity(self) -> ValidationResult:
        """Check data integrity and validation"""
        start_time = time.time()
        
        try:
            from operations.validation_ops import ValidationEngine
            
            # Test validation engine
            validation_engine = ValidationEngine()
            
            # Test with mock data
            mock_record = {
                'player_name': 'Test Player',
                'season': 2024,
                'pfr_id': 'test123',
                'cmp_pct': 65.5,
                'rate': 95.2,
                'age': 25,
                'att': 500,
                'cmp': 325,
                'yds': 3500,
                'y_a': 7.0
            }
            
            issues = validation_engine.validate_record(mock_record, 'qb_stats')
            
            # Check that validation is working
            validation_working = isinstance(issues, list)
            
            # Test validation rules
            rules_count = len(validation_engine.rules)
            rules_working = rules_count > 0
            
            passed = validation_working and rules_working
            recommendations = []
            
            if not validation_working:
                recommendations.append("Fix validation engine")
            
            if not rules_working:
                recommendations.append("Add validation rules")
            
            return ValidationResult(
                name="Data Integrity",
                passed=passed,
                details={
                    'validation_working': validation_working,
                    'rules_count': rules_count,
                    'rules_working': rules_working,
                    'test_issues_found': len(issues)
                },
                recommendations=recommendations,
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            return ValidationResult(
                name="Data Integrity",
                passed=False,
                details={'error': str(e)},
                recommendations=['Fix data integrity validation', 'Ensure validation engine is available'],
                execution_time=time.time() - start_time,
                error_message=str(e)
            )
    
    def _check_error_handling(self) -> ValidationResult:
        """Check error handling and logging"""
        start_time = time.time()
        
        try:
            # Check if logging is configured
            logging_configured = len(logging.getLogger().handlers) > 0
            
            # Check if logs directory exists and is writable
            logs_writable = self.logs_dir.exists() and os.access(self.logs_dir, os.W_OK)
            
            # Test error handling in core components
            error_handling_working = True
            
            try:
                from core.scraper import CoreScraper
                scraper = CoreScraper(rate_limit_delay=0.1)
                # Test that scraper has error handling methods
                error_handling_working = hasattr(scraper, 'handle_error')
            except:
                error_handling_working = False
            
            passed = logging_configured and logs_writable and error_handling_working
            recommendations = []
            
            if not logging_configured:
                recommendations.append("Configure logging properly")
            
            if not logs_writable:
                recommendations.append("Ensure logs directory is writable")
            
            if not error_handling_working:
                recommendations.append("Implement proper error handling in core components")
            
            return ValidationResult(
                name="Error Handling",
                passed=passed,
                details={
                    'logging_configured': logging_configured,
                    'logs_writable': logs_writable,
                    'error_handling_working': error_handling_working
                },
                recommendations=recommendations,
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            return ValidationResult(
                name="Error Handling",
                passed=False,
                details={'error': str(e)},
                recommendations=['Fix error handling validation'],
                execution_time=time.time() - start_time,
                error_message=str(e)
            )
    
    def _check_configuration(self) -> ValidationResult:
        """Check configuration and environment setup"""
        start_time = time.time()
        
        try:
            # Check if config is available
            config_available = config is not None
            
            # Check environment variables
            env_vars = ['DATABASE_URL', 'SUPABASE_URL', 'SUPABASE_KEY']
            env_vars_set = sum(1 for var in env_vars if os.getenv(var))
            env_coverage = env_vars_set / len(env_vars)
            
            # Check if .env file exists
            env_file_exists = (self.project_root / '.env').exists()
            
            passed = config_available and env_coverage >= 0.5
            recommendations = []
            
            if not config_available:
                recommendations.append("Ensure configuration is properly set up")
            
            if env_coverage < 1.0:
                recommendations.append(f"Set all environment variables (only {env_coverage:.1%} set)")
                for var in env_vars:
                    if not os.getenv(var):
                        recommendations.append(f"  - Set {var}")
            
            if not env_file_exists:
                recommendations.append("Create .env file for local development")
            
            return ValidationResult(
                name="Configuration",
                passed=passed,
                details={
                    'config_available': config_available,
                    'env_vars_set': env_vars_set,
                    'env_coverage': env_coverage,
                    'env_file_exists': env_file_exists
                },
                recommendations=recommendations,
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            return ValidationResult(
                name="Configuration",
                passed=False,
                details={'error': str(e)},
                recommendations=['Fix configuration validation'],
                execution_time=time.time() - start_time,
                error_message=str(e)
            )
    
    def _assess_production_readiness(self, results: List[ValidationResult]) -> bool:
        """Assess overall production readiness"""
        # Critical checks that must pass
        critical_checks = ['Test Coverage', 'Type Safety', 'Security Scan', 'CLI Functionality']
        
        critical_passed = all(
            any(r.name == check and r.passed for r in results)
            for check in critical_checks
        )
        
        # Overall pass rate should be high
        overall_pass_rate = sum(1 for r in results if r.passed) / len(results)
        
        return critical_passed and overall_pass_rate >= 0.8
    
    def _generate_summary(self, results: List[ValidationResult], overall_passed: bool, production_ready: bool) -> str:
        """Generate human-readable summary"""
        summary = f"Production Quality Validation - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        summary += f"Overall Result: {'PASSED' if overall_passed else 'FAILED'}\n"
        summary += f"Production Ready: {'YES' if production_ready else 'NO'}\n"
        summary += f"Pass Rate: {sum(1 for r in results if r.passed)}/{len(results)} ({sum(1 for r in results if r.passed)/len(results)*100:.1f}%)\n\n"
        
        summary += "Check Results:\n"
        for result in results:
            status = "✓ PASS" if result.passed else "✗ FAIL"
            summary += f"  {status} {result.name}\n"
        
        if not overall_passed:
            summary += "\nCritical Issues:\n"
            for result in results:
                if not result.passed:
                    summary += f"  - {result.name}: {result.error_message or 'Check failed'}\n"
                    for rec in result.recommendations[:2]:  # Show first 2 recommendations
                        summary += f"    → {rec}\n"
        
        return summary
    
    def save_report(self, report: QualityReport, filename: str = None) -> str:
        """Save quality report to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"quality_report_{timestamp}.json"
        
        report_path = self.logs_dir / filename
        
        with open(report_path, 'w') as f:
            json.dump(report.to_dict(), f, indent=2)
        
        logger.info(f"Quality report saved to: {report_path}")
        return str(report_path) 