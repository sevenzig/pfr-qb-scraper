#!/usr/bin/env python3
"""
Phase 4 Production Tests
Comprehensive testing for production-ready quality gates, performance monitoring, and legacy deprecation
"""

import sys
import os
import unittest
import tempfile
import json
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import subprocess

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.operations.quality_gates import (
    ProductionQualityGates, 
    ValidationResult, 
    QualityReport
)
from src.operations.performance_monitor import (
    PerformanceMonitor,
    MetricsCollector,
    AlertManager,
    PerformanceMetric,
    PerformanceAlert,
    PerformanceReport
)
from src.operations.legacy_deprecation import (
    LegacyDeprecationManager,
    LegacyScript,
    DeprecationWarning
)


class TestProductionQualityGates(unittest.TestCase):
    """Test production quality gates validation system"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.quality_gates = ProductionQualityGates()
        self.temp_dir = tempfile.mkdtemp()
        self.quality_gates.project_root = Path(self.temp_dir)
        self.quality_gates.src_dir = self.quality_gates.project_root / "src"
        self.quality_gates.tests_dir = self.quality_gates.project_root / "tests"
        self.quality_gates.logs_dir = self.quality_gates.project_root / "logs"
        
        # Create test directory structure
        self.quality_gates.src_dir.mkdir(exist_ok=True)
        self.quality_gates.tests_dir.mkdir(exist_ok=True)
        self.quality_gates.logs_dir.mkdir(exist_ok=True)
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_validation_result_creation(self):
        """Test ValidationResult creation and serialization"""
        result = ValidationResult(
            name="Test Check",
            passed=True,
            details={"test": "data"},
            recommendations=["Do this", "Do that"],
            execution_time=1.5
        )
        
        self.assertEqual(result.name, "Test Check")
        self.assertTrue(result.passed)
        self.assertEqual(result.details["test"], "data")
        self.assertEqual(len(result.recommendations), 2)
        self.assertEqual(result.execution_time, 1.5)
        
        # Test serialization
        result_dict = result.to_dict()
        self.assertEqual(result_dict["name"], "Test Check")
        self.assertTrue(result_dict["passed"])
    
    def test_quality_report_creation(self):
        """Test QualityReport creation and methods"""
        results = [
            ValidationResult("Check 1", True, {}, [], 1.0),
            ValidationResult("Check 2", False, {}, [], 2.0),
            ValidationResult("Check 3", True, {}, [], 1.5)
        ]
        
        report = QualityReport(
            timestamp=datetime.now(),
            overall_passed=False,
            total_checks=3,
            passed_checks=2,
            failed_checks=1,
            results=results,
            production_ready=False,
            summary="Test summary"
        )
        
        self.assertEqual(report.total_checks, 3)
        self.assertEqual(report.passed_checks, 2)
        self.assertEqual(report.failed_checks, 1)
        self.assertFalse(report.overall_passed)
        self.assertFalse(report.production_ready)
        
        # Test pass rate calculation
        pass_rate = report.get_pass_rate()
        self.assertEqual(pass_rate, 66.66666666666666)
        
        # Test serialization
        report_dict = report.to_dict()
        self.assertEqual(report_dict["total_checks"], 3)
        self.assertEqual(report_dict["pass_rate"], 66.66666666666666)
    
    @patch('subprocess.run')
    def test_check_test_coverage(self, mock_run):
        """Test test coverage validation"""
        # Mock successful coverage report
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = '''
        {
            "totals": {
                "percent_covered": 87.5
            },
            "missing_lines": []
        }
        JSON report written to coverage.json
        '''
        mock_run.return_value = mock_result
        
        result = self.quality_gates._check_test_coverage()
        
        self.assertEqual(result.name, "Test Coverage")
        self.assertTrue(result.passed)
        self.assertEqual(result.details["total_coverage"], 87.5)
        self.assertEqual(result.details["target_coverage"], 85.0)
    
    @patch('subprocess.run')
    def test_check_type_safety(self, mock_run):
        """Test type safety validation"""
        # Mock successful mypy run
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        result = self.quality_gates._check_type_safety()
        
        self.assertEqual(result.name, "Type Safety")
        self.assertTrue(result.passed)
    
    @patch('subprocess.run')
    def test_check_code_quality(self, mock_run):
        """Test code quality validation"""
        # Mock successful flake8 run
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        result = self.quality_gates._check_code_quality()
        
        self.assertEqual(result.name, "Code Quality")
        self.assertTrue(result.passed)
    
    @patch('subprocess.run')
    def test_check_security(self, mock_run):
        """Test security validation"""
        # Mock successful bandit run with no issues
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "[]"
        mock_run.return_value = mock_result
        
        result = self.quality_gates._check_security()
        
        self.assertEqual(result.name, "Security Scan")
        self.assertTrue(result.passed)
        self.assertEqual(result.details["high_issues"], 0)
    
    def test_check_documentation(self):
        """Test documentation validation"""
        # Create a test Python file with docstrings
        test_file = self.quality_gates.src_dir / "test_module.py"
        test_file.write_text('''
"""
Module docstring
"""

def test_function():
    """
    Function docstring
    """
    pass

class TestClass:
    """
    Class docstring
    """
    
    def test_method(self):
        """
        Method docstring
        """
        pass
''')
        
        result = self.quality_gates._check_documentation()
        
        self.assertEqual(result.name, "Documentation")
        self.assertTrue(result.passed)
        self.assertGreater(result.details["file_doc_coverage"], 0.8)
        self.assertGreater(result.details["function_doc_coverage"], 0.7)
    
    def test_assess_production_readiness(self):
        """Test production readiness assessment"""
        # Test with all critical checks passing
        results = [
            ValidationResult("Test Coverage", True, {}, [], 1.0),
            ValidationResult("Type Safety", True, {}, [], 1.0),
            ValidationResult("Security Scan", True, {}, [], 1.0),
            ValidationResult("CLI Functionality", True, {}, [], 1.0),
            ValidationResult("Other Check", True, {}, [], 1.0)
        ]
        
        production_ready = self.quality_gates._assess_production_readiness(results)
        self.assertTrue(production_ready)
        
        # Test with critical check failing
        results[0] = ValidationResult("Test Coverage", False, {}, [], 1.0)
        production_ready = self.quality_gates._assess_production_readiness(results)
        self.assertFalse(production_ready)
    
    def test_save_report(self):
        """Test report saving functionality"""
        results = [ValidationResult("Test", True, {}, [], 1.0)]
        report = QualityReport(
            timestamp=datetime.now(),
            overall_passed=True,
            total_checks=1,
            passed_checks=1,
            failed_checks=0,
            results=results,
            production_ready=True,
            summary="Test report"
        )
        
        output_path = self.quality_gates.save_report(report, "test_report.json")
        
        self.assertTrue(Path(output_path).exists())
        
        # Verify saved content
        with open(output_path, 'r') as f:
            saved_data = json.load(f)
        
        self.assertTrue(saved_data["overall_passed"])
        self.assertEqual(saved_data["total_checks"], 1)


class TestPerformanceMonitor(unittest.TestCase):
    """Test performance monitoring system"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.monitor = PerformanceMonitor()
    
    def test_metrics_collector_creation(self):
        """Test MetricsCollector creation and basic functionality"""
        collector = MetricsCollector()
        
        # Test recording metrics
        collector.record_operation("test_op", 1.5, 100.0, "success", {"test": "data"})
        
        # Verify metric was recorded
        self.assertEqual(len(collector.metrics), 1)
        metric = collector.metrics[0]
        self.assertEqual(metric.operation_name, "test_op")
        self.assertEqual(metric.duration, 1.5)
        self.assertEqual(metric.memory_used, 100.0)
        self.assertEqual(metric.status, "success")
    
    def test_alert_manager_creation(self):
        """Test AlertManager creation and functionality"""
        alert_manager = AlertManager()
        
        # Test sending performance alert
        alerts = alert_manager.send_performance_alert(
            operation="test_op",
            duration=40.0,  # Exceeds timeout threshold
            memory_used=600.0,  # Exceeds memory threshold
            error_rate=0.15  # Exceeds error rate threshold
        )
        
        # Should generate multiple alerts
        self.assertGreater(len(alerts), 0)
        
        # Check alert types
        alert_types = [alert.alert_type for alert in alerts]
        self.assertIn("timeout", alert_types)
        self.assertIn("memory", alert_types)
        self.assertIn("error_rate", alert_types)
    
    def test_performance_monitor_tracking(self):
        """Test performance monitoring with decorator"""
        @self.monitor.track_operation("test_operation")
        def test_function():
            return "success"
        
        # Call the function
        result = test_function()
        
        # Verify metric was recorded
        self.assertEqual(len(self.monitor.metrics.metrics), 1)
        metric = self.monitor.metrics.metrics[0]
        self.assertEqual(metric.operation_name, "test_operation")
        self.assertEqual(metric.status, "success")
    
    def test_performance_report_generation(self):
        """Test performance report generation"""
        # Add some test metrics
        self.monitor.metrics.record_operation("op1", 1.0, 50.0, "success")
        self.monitor.metrics.record_operation("op2", 2.0, 100.0, "success")
        self.monitor.metrics.record_operation("op3", 0.5, 25.0, "error")
        
        # Generate report
        report = self.monitor.generate_performance_report(hours=24)
        
        # Verify report structure
        self.assertEqual(report.total_operations, 3)
        self.assertEqual(report.successful_operations, 2)
        self.assertEqual(report.failed_operations, 1)
        self.assertEqual(report.average_duration, 1.1666666666666667)
        self.assertEqual(report.max_duration, 2.0)
        self.assertEqual(report.min_duration, 0.5)
    
    def test_performance_monitor_enable_disable(self):
        """Test performance monitoring enable/disable"""
        # Test enable
        self.monitor.enable_monitoring()
        self.assertTrue(self.monitor.monitoring_enabled)
        
        # Test disable
        self.monitor.disable_monitoring()
        self.assertFalse(self.monitor.monitoring_enabled)
    
    def test_clear_metrics_and_alerts(self):
        """Test clearing metrics and alerts"""
        # Add some test data
        self.monitor.metrics.record_operation("test", 1.0, 50.0, "success")
        self.monitor.alerts.send_performance_alert("test", 40.0)
        
        # Verify data exists
        self.assertEqual(len(self.monitor.metrics.metrics), 1)
        self.assertGreater(len(self.monitor.alerts.alerts), 0)
        
        # Clear data
        self.monitor.clear_metrics()
        self.monitor.clear_alerts()
        
        # Verify data is cleared
        self.assertEqual(len(self.monitor.metrics.metrics), 0)
        self.assertEqual(len(self.monitor.alerts.alerts), 0)


class TestLegacyDeprecationManager(unittest.TestCase):
    """Test legacy deprecation management system"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)
        self.scripts_dir = self.project_root / "scripts"
        self.legacy_dir = self.project_root / "legacy"
        
        # Create test directory structure
        self.scripts_dir.mkdir(exist_ok=True)
        self.legacy_dir.mkdir(exist_ok=True)
        
        # Create test legacy scripts
        self._create_test_scripts()
        
        # Initialize deprecation manager
        self.deprecation_manager = LegacyDeprecationManager()
        self.deprecation_manager.project_root = self.project_root
        self.deprecation_manager.scripts_dir = self.scripts_dir
        self.deprecation_manager.legacy_dir = self.legacy_dir
        self.deprecation_manager.legacy_scripts = self.deprecation_manager._build_legacy_registry()
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _create_test_scripts(self):
        """Create test legacy scripts"""
        test_scripts = [
            ("enhanced_qb_scraper.py", "print('Enhanced scraper')"),
            ("robust_qb_scraper.py", "print('Robust scraper')"),
            ("simple_scrape.py", "print('Simple scraper')")
        ]
        
        for script_name, content in test_scripts:
            script_path = self.scripts_dir / script_name
            script_path.write_text(content)
    
    def test_legacy_script_creation(self):
        """Test LegacyScript creation"""
        script = LegacyScript(
            name="test_script.py",
            path=Path("/test/path"),
            cli_equivalent="scrape --test",
            deprecated_since=datetime.now(),
            removal_date=datetime.now() + timedelta(days=90),
            migration_notes="Use CLI instead"
        )
        
        self.assertEqual(script.name, "test_script.py")
        self.assertEqual(script.cli_equivalent, "scrape --test")
        self.assertIsInstance(script.deprecated_since, datetime)
        self.assertIsInstance(script.removal_date, datetime)
    
    def test_deprecation_warning_creation(self):
        """Test DeprecationWarning creation"""
        warning = DeprecationWarning(
            script_name="test.py",
            warning_type="deprecated",
            message="This script is deprecated",
            timestamp=datetime.now(),
            cli_alternative="pfr-scraper test",
            migration_guide="Use the CLI instead"
        )
        
        self.assertEqual(warning.script_name, "test.py")
        self.assertEqual(warning.warning_type, "deprecated")
        self.assertEqual(warning.cli_alternative, "pfr-scraper test")
    
    def test_build_legacy_registry(self):
        """Test building legacy script registry"""
        registry = self.deprecation_manager._build_legacy_registry()
        
        # Should find our test scripts
        self.assertIn("enhanced_qb_scraper.py", registry)
        self.assertIn("robust_qb_scraper.py", registry)
        self.assertIn("simple_scrape.py", registry)
        
        # Check script information
        enhanced_script = registry["enhanced_qb_scraper.py"]
        self.assertEqual(enhanced_script.name, "enhanced_qb_scraper.py")
        self.assertEqual(enhanced_script.cli_equivalent, "scrape --enhanced")
        self.assertIsInstance(enhanced_script.deprecated_since, datetime)
        self.assertIsInstance(enhanced_script.removal_date, datetime)
    
    def test_add_deprecation_warnings(self):
        """Test adding deprecation warnings to scripts"""
        # Add warnings to all scripts
        self.deprecation_manager.add_deprecation_warnings()
        
        # Check that warnings were added
        for script_name in self.deprecation_manager.legacy_scripts:
            script_path = self.scripts_dir / script_name
            content = script_path.read_text()
            
            # Should contain deprecation warning
            self.assertIn("DEPRECATED", content)
            self.assertIn("MIGRATION", content)
            self.assertIn("CLI EQUIVALENT", content)
    
    def test_create_redirect_scripts(self):
        """Test creating redirect scripts"""
        self.deprecation_manager.create_redirect_scripts()
        
        # Check that redirect scripts were created
        for script_name in self.deprecation_manager.legacy_scripts:
            redirect_path = self.legacy_dir / f"redirect_{script_name}"
            self.assertTrue(redirect_path.exists())
            
            # Check redirect script content
            content = redirect_path.read_text()
            self.assertIn("Redirect script", content)
            self.assertIn("src.cli.cli_main", content)
    
    def test_generate_migration_guide(self):
        """Test migration guide generation"""
        guide = self.deprecation_manager.generate_migration_guide()
        
        # Should contain key sections
        self.assertIn("Legacy Script Migration Guide", guide)
        self.assertIn("Migration Timeline", guide)
        self.assertIn("Script Migration Table", guide)
        self.assertIn("enhanced_qb_scraper.py", guide)
        self.assertIn("scrape --enhanced", guide)
    
    def test_check_usage_patterns(self):
        """Test usage pattern checking"""
        usage_data = self.deprecation_manager.check_usage_patterns()
        
        # Should return expected structure
        self.assertIn("total_scripts", usage_data)
        self.assertIn("scripts_with_usage", usage_data)
        self.assertIn("total_usage_count", usage_data)
        self.assertIn("most_used_scripts", usage_data)
        self.assertIn("recent_usage", usage_data)
        
        # Should have correct counts
        self.assertEqual(usage_data["total_scripts"], 3)
    
    def test_create_removal_plan(self):
        """Test removal plan creation"""
        removal_plan = self.deprecation_manager.create_removal_plan()
        
        # Should return expected structure
        self.assertIn("immediate_removal", removal_plan)
        self.assertIn("scheduled_removal", removal_plan)
        self.assertIn("keep_for_compatibility", removal_plan)
        self.assertIn("migration_required", removal_plan)
        
        # All lists should be present
        self.assertIsInstance(removal_plan["immediate_removal"], list)
        self.assertIsInstance(removal_plan["scheduled_removal"], list)
        self.assertIsInstance(removal_plan["keep_for_compatibility"], list)
        self.assertIsInstance(removal_plan["migration_required"], list)
    
    def test_execute_migration(self):
        """Test script migration execution"""
        script_name = "enhanced_qb_scraper.py"
        
        # Test dry run
        success = self.deprecation_manager.execute_migration(script_name, dry_run=True)
        self.assertTrue(success)
        
        # Verify original script still exists
        original_path = self.scripts_dir / script_name
        self.assertTrue(original_path.exists())
        
        # Test actual migration
        success = self.deprecation_manager.execute_migration(script_name, dry_run=False)
        self.assertTrue(success)
        
        # Verify redirect script was created
        redirect_path = self.legacy_dir / f"redirect_{script_name}"
        self.assertTrue(redirect_path.exists())
    
    def test_generate_usage_report(self):
        """Test usage report generation"""
        report = self.deprecation_manager.generate_usage_report()
        
        # Should contain key sections
        self.assertIn("Legacy Script Usage Report", report)
        self.assertIn("Summary", report)
        self.assertIn("Most Used Scripts", report)
        self.assertIn("Removal Plan", report)
        
        # Should include script information
        self.assertIn("enhanced_qb_scraper.py", report)


class TestPhase4Integration(unittest.TestCase):
    """Integration tests for Phase 4 features"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)
        
        # Create test directory structure
        (self.project_root / "src").mkdir(exist_ok=True)
        (self.project_root / "tests").mkdir(exist_ok=True)
        (self.project_root / "logs").mkdir(exist_ok=True)
        (self.project_root / "scripts").mkdir(exist_ok=True)
        (self.project_root / "legacy").mkdir(exist_ok=True)
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_quality_gates_with_performance_monitor(self):
        """Test integration between quality gates and performance monitor"""
        # Create quality gates
        quality_gates = ProductionQualityGates()
        quality_gates.project_root = self.project_root
        quality_gates.src_dir = self.project_root / "src"
        quality_gates.tests_dir = self.project_root / "tests"
        quality_gates.logs_dir = self.project_root / "logs"
        
        # Create performance monitor
        monitor = PerformanceMonitor()
        
        # Track performance during quality validation
        @monitor.track_operation("quality_validation")
        def run_validation():
            return quality_gates.run_comprehensive_validation()
        
        # Run validation with performance tracking
        report = run_validation()
        
        # Verify both systems worked
        self.assertIsInstance(report, QualityReport)
        self.assertEqual(len(monitor.metrics.metrics), 1)
        
        # Check performance metric
        metric = monitor.metrics.metrics[0]
        self.assertEqual(metric.operation_name, "quality_validation")
        self.assertEqual(metric.status, "success")
    
    def test_legacy_deprecation_with_quality_gates(self):
        """Test integration between legacy deprecation and quality gates"""
        # Create deprecation manager
        deprecation_manager = LegacyDeprecationManager()
        deprecation_manager.project_root = self.project_root
        deprecation_manager.scripts_dir = self.project_root / "scripts"
        deprecation_manager.legacy_dir = self.project_root / "legacy"

        # Create test script (must match a legacy definition)
        test_script = self.project_root / "scripts" / "enhanced_qb_scraper.py"
        test_script.write_text("print('test')")

        # Rebuild registry
        deprecation_manager.legacy_scripts = deprecation_manager._build_legacy_registry()

        # Add deprecation warnings
        deprecation_manager.add_deprecation_warnings()

        # Create quality gates
        quality_gates = ProductionQualityGates()
        quality_gates.project_root = self.project_root
        quality_gates.src_dir = self.project_root / "src"
        quality_gates.tests_dir = self.project_root / "tests"
        quality_gates.logs_dir = self.project_root / "logs"

        # Run quality validation
        report = quality_gates.run_comprehensive_validation()

        # Verify both systems worked together
        self.assertIsInstance(report, QualityReport)
        self.assertGreater(len(deprecation_manager.legacy_scripts), 0)

    def test_comprehensive_phase4_workflow(self):
        """Test comprehensive Phase 4 workflow"""
        # 1. Set up performance monitoring
        monitor = PerformanceMonitor()
        monitor.enable_monitoring()

        # 2. Set up legacy deprecation
        deprecation_manager = LegacyDeprecationManager()
        deprecation_manager.project_root = self.project_root
        deprecation_manager.scripts_dir = self.project_root / "scripts"
        deprecation_manager.legacy_dir = self.project_root / "legacy"

        # 3. Create test script (must match a legacy definition)
        test_script = self.project_root / "scripts" / "enhanced_qb_scraper.py"
        test_script.write_text("print('test')")
        deprecation_manager.legacy_scripts = deprecation_manager._build_legacy_registry()

        # 4. Set up quality gates
        quality_gates = ProductionQualityGates()
        quality_gates.project_root = self.project_root
        quality_gates.src_dir = self.project_root / "src"
        quality_gates.tests_dir = self.project_root / "tests"
        quality_gates.logs_dir = self.project_root / "logs"

        # 5. Run comprehensive workflow
        @monitor.track_operation("phase4_workflow")
        def run_workflow():
            # Add deprecation warnings
            deprecation_manager.add_deprecation_warnings()

            # Create redirect scripts
            deprecation_manager.create_redirect_scripts()

            # Run quality validation
            return quality_gates.run_comprehensive_validation()

        # Execute workflow
        quality_report = run_workflow()

        # 6. Generate performance report
        performance_report = monitor.generate_performance_report()

        # 7. Generate legacy report
        legacy_report = deprecation_manager.generate_usage_report()

        # Verify all components worked
        self.assertIsInstance(quality_report, QualityReport)
        self.assertIsInstance(performance_report, PerformanceReport)
        self.assertIsInstance(legacy_report, str)

        # Verify performance tracking
        self.assertEqual(len(monitor.metrics.metrics), 1)
        metric = monitor.metrics.metrics[0]
        self.assertEqual(metric.operation_name, "phase4_workflow")
        self.assertEqual(metric.status, "success")

        # Verify legacy management
        self.assertGreater(len(deprecation_manager.legacy_scripts), 0)

        # Verify files were created
        self.assertTrue((self.project_root / "legacy" / "redirect_enhanced_qb_scraper.py").exists())


if __name__ == '__main__':
    unittest.main() 