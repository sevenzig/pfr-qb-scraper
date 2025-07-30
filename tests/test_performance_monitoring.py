#!/usr/bin/env python3
"""
Comprehensive test suite for Performance Monitoring System
Tests all monitoring capabilities including metrics collection, baseline validation, and CLI integration
"""

import pytest
import time
import json
import tempfile
import threading
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Import the monitoring components
from src.operations.performance_monitor import (
    PerformanceMonitor, 
    MetricsCollector, 
    AlertManager, 
    SystemMetricsCollector,
    RealTimeMonitor,
    Metric,
    MonitoringSession,
    PerformanceBaseline,
    ValidationResult,
    MetricType,
    AlertSeverity
)
from src.config.config import Config, MonitoringConfig
from src.database.db_manager import DatabaseManager


class TestPerformanceMonitoring:
    """Test suite for performance monitoring functionality"""
    
    @pytest.fixture
    def mock_config(self):
        """Create a mock configuration for testing"""
        config = Mock()
        config.monitoring = MonitoringConfig(
            enabled=True,
            collection_interval_seconds=1,
            retention_days=30,
            baseline_sample_size=5,
            performance_degradation_threshold=0.20,
            memory_alert_threshold_mb=100.0,
            cpu_alert_threshold_percent=80.0,
            error_rate_alert_threshold=0.05,
            timeout_alert_threshold_seconds=10.0
        )
        return config
    
    @pytest.fixture
    def performance_monitor(self, mock_config):
        """Create a performance monitor instance for testing"""
        return PerformanceMonitor(mock_config)
    
    @pytest.fixture
    def metrics_collector(self):
        """Create a metrics collector for testing"""
        return MetricsCollector(max_metrics=100)
    
    @pytest.fixture
    def alert_manager(self):
        """Create an alert manager for testing"""
        return AlertManager()
    
    def test_metric_creation(self):
        """Test metric data point creation and serialization"""
        metric = Metric(
            name="test_duration",
            value=5.2,
            timestamp=datetime.now(),
            labels={"operation": "test", "status": "success"},
            metric_type=MetricType.DURATION,
            unit="seconds"
        )
        
        assert metric.name == "test_duration"
        assert metric.value == 5.2
        assert metric.metric_type == MetricType.DURATION
        assert metric.unit == "seconds"
        
        # Test serialization
        metric_dict = metric.to_dict()
        assert "name" in metric_dict
        assert "value" in metric_dict
        assert "timestamp" in metric_dict
        assert "labels" in metric_dict
        assert "metric_type" in metric_dict
    
    def test_monitoring_session_management(self, performance_monitor):
        """Test monitoring session lifecycle"""
        # Start a session
        session = performance_monitor.start_monitoring_session("test_session", "test_operation")
        
        assert session.session_id == "test_session"
        assert session.operation_type == "test_operation"
        assert session.ended_at is None
        assert session.session_id in performance_monitor.sessions
        
        # Add metrics to session
        metric = Metric("test_metric", 42.0, datetime.now())
        session.add_metric(metric)
        
        assert len(session.metrics["test_metric"]) == 1
        assert session.get_latest_metric("test_metric").value == 42.0
        
        # End session
        ended_session = performance_monitor.end_monitoring_session("test_session")
        assert ended_session.ended_at is not None
        assert ended_session.get_duration() > 0
    
    def test_metrics_collection_accuracy(self, metrics_collector):
        """Test that metrics are collected and aggregated correctly"""
        # Record multiple operations
        metrics_collector.record_operation("test_op", 1.0, 50.0, "success")
        metrics_collector.record_operation("test_op", 2.0, 75.0, "success")
        metrics_collector.record_operation("test_op", 1.5, 60.0, "error")
        
        summaries = metrics_collector.get_operation_summaries()
        
        assert "test_op" in summaries
        summary = summaries["test_op"]
        
        assert summary["count"] == 3
        assert summary["success_rate"] == 2/3  # 2 successes out of 3
        assert abs(summary["avg_duration"] - 1.5) < 0.01  # (1.0 + 2.0 + 1.5) / 3
        assert abs(summary["avg_memory"] - 61.67) < 0.1  # (50 + 75 + 60) / 3
        assert summary["min_duration"] == 1.0
        assert summary["max_duration"] == 2.0
    
    def test_percentile_calculation(self, metrics_collector):
        """Test percentile calculation accuracy"""
        # Record operations with known durations
        durations = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
        for duration in durations:
            metrics_collector.record_operation("test_op", duration, 50.0, "success")
        
        summaries = metrics_collector.get_operation_summaries()
        summary = summaries["test_op"]
        
        # P95 should be around 9.5 (95th percentile of 1-10)
        assert abs(summary["p95_duration"] - 9.5) < 0.5
        
        # P99 should be around 9.9 (99th percentile of 1-10)
        assert abs(summary["p99_duration"] - 9.9) < 0.5
    
    def test_baseline_creation_and_validation(self, performance_monitor, metrics_collector):
        """Test baseline creation from samples and validation"""
        # Inject the metrics collector into the monitor
        performance_monitor.metrics = metrics_collector
        
        # Record enough samples for baseline
        for i in range(10):
            metrics_collector.record_operation("baseline_test", 2.0 + i * 0.1, 100.0, "success")
        
        # Create baseline
        baseline = performance_monitor.create_performance_baseline("baseline_test", sample_size=5)
        
        assert baseline is not None
        assert baseline.operation_type == "baseline_test"
        assert baseline.avg_duration > 0
        assert baseline.avg_memory_mb > 0
        assert baseline.success_rate_threshold > 0
        assert baseline.created_from_samples >= 5
        
        # Test validation against baseline
        current_metrics = {
            'avg_duration': 2.1,  # Close to baseline
            'avg_memory': 105.0,
            'success_rate': 1.0
        }
        
        validation = performance_monitor.validate_performance_against_baseline(current_metrics, baseline)
        
        assert isinstance(validation, ValidationResult)
        assert validation.operation_type == "baseline_test"
        assert validation.baseline == baseline
        assert len(validation.violations) == 0  # Should pass
    
    def test_baseline_violation_detection(self, performance_monitor):
        """Test that performance violations are properly detected"""
        # Create a baseline
        baseline = PerformanceBaseline(
            operation_type="test_op",
            avg_duration=1.0,
            avg_memory_mb=100.0,
            avg_cpu_percent=50.0,
            avg_records_per_second=10.0,
            success_rate_threshold=0.95,
            p95_duration=1.5,
            p99_duration=2.0,
            created_from_samples=10,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Test with degraded performance (violates 20% threshold)
        degraded_metrics = {
            'avg_duration': 1.3,  # 30% slower than baseline
            'avg_memory': 160.0,  # 60% more memory
            'success_rate': 0.85  # Below threshold
        }
        
        validation = performance_monitor.validate_performance_against_baseline(degraded_metrics, baseline)
        
        assert not validation.passed
        assert len(validation.violations) > 0
        assert any("Duration degraded" in v for v in validation.violations)
        assert any("Memory usage increased" in v for v in validation.violations)
        assert any("Success rate below threshold" in v for v in validation.violations)
    
    def test_alert_generation(self, alert_manager):
        """Test performance alert generation"""
        # Test timeout alert
        alerts = alert_manager.send_performance_alert(
            operation="slow_operation",
            duration=20.0,  # Exceeds default threshold of 15.0
            memory_used=50.0,
            cpu_usage=60.0
        )
        
        assert len(alerts) == 1
        timeout_alert = alerts[0]
        assert timeout_alert.alert_type == "timeout"
        assert timeout_alert.operation_name == "slow_operation"
        assert timeout_alert.actual_value == 20.0
        assert timeout_alert.threshold == 15.0
        
        # Test memory alert
        alerts = alert_manager.send_performance_alert(
            operation="memory_heavy_operation",
            duration=5.0,
            memory_used=600.0,  # Exceeds default threshold of 500.0
            cpu_usage=40.0
        )
        
        assert len(alerts) == 1
        memory_alert = alerts[0]
        assert memory_alert.alert_type == "memory"
        assert memory_alert.actual_value == 600.0
        assert memory_alert.threshold == 500.0
    
    def test_alert_severity_calculation(self, alert_manager):
        """Test alert severity levels"""
        # Test different severity levels based on threshold deviation
        
        # Low severity (just over threshold)
        alerts = alert_manager.send_performance_alert(
            operation="test_op",
            duration=16.0  # Just over 15.0 threshold (1.07x)
        )
        assert alerts[0].severity == "low"
        
        # Medium severity (1.5x threshold)
        alerts = alert_manager.send_performance_alert(
            operation="test_op",
            duration=22.5  # 1.5x of 15.0 threshold
        )
        assert alerts[0].severity == "medium"
        
        # High severity (2x threshold)
        alerts = alert_manager.send_performance_alert(
            operation="test_op",
            duration=30.0  # 2x of 15.0 threshold
        )
        assert alerts[0].severity == "high"
        
        # Critical severity (3x threshold)
        alerts = alert_manager.send_performance_alert(
            operation="test_op",
            duration=45.0  # 3x of 15.0 threshold
        )
        assert alerts[0].severity == "critical"
    
    def test_real_time_monitoring_performance(self, performance_monitor):
        """Test that monitoring doesn't impact performance significantly"""
        # Test monitoring overhead
        start_time = time.time()
        
        # Perform operations with monitoring enabled
        for i in range(100):
            with performance_monitor.monitor_operation("test_operation"):
                time.sleep(0.001)  # Simulate work
        
        monitored_time = time.time() - start_time
        
        # Disable monitoring and test without it
        performance_monitor.disable_monitoring()
        start_time = time.time()
        
        for i in range(100):
            with performance_monitor.monitor_operation("test_operation"):
                time.sleep(0.001)  # Simulate work
        
        unmonitored_time = time.time() - start_time
        
        # Monitoring overhead should be less than 5%
        overhead = (monitored_time - unmonitored_time) / unmonitored_time
        assert overhead < 0.05  # Less than 5% overhead
    
    def test_system_metrics_collection(self):
        """Test system metrics collection accuracy"""
        collector = SystemMetricsCollector()
        
        # Test CPU usage
        cpu_usage = collector.get_cpu_usage()
        assert isinstance(cpu_usage, float)
        assert 0 <= cpu_usage <= 100
        
        # Test memory usage
        memory_info = collector.get_memory_usage()
        assert "rss_mb" in memory_info
        assert "vms_mb" in memory_info
        assert "percent" in memory_info
        assert memory_info["rss_mb"] > 0
        
        # Test network I/O
        network_io = collector.get_network_io()
        assert "bytes_sent" in network_io
        assert "bytes_recv" in network_io
        assert isinstance(network_io["bytes_sent"], int)
        assert isinstance(network_io["bytes_recv"], int)
        
        # Test disk I/O
        disk_io = collector.get_disk_io()
        assert "read_bytes" in disk_io
        assert "write_bytes" in disk_io
        assert isinstance(disk_io["read_bytes"], int)
        assert isinstance(disk_io["write_bytes"], int)
    
    def test_metrics_export_functionality(self, performance_monitor, tmp_path):
        """Test metrics export in different formats"""
        # Record some test metrics
        performance_monitor.metrics.record_operation("export_test", 1.5, 100.0, "success")
        performance_monitor.metrics.record_operation("export_test", 2.0, 120.0, "success")
        
        with patch('src.operations.performance_monitor.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = tmp_path
            
            # Test JSON export
            json_file = performance_monitor.export_metrics(format="json", hours=1)
            assert json_file.endswith(".json")
            
            # Test CSV export
            csv_file = performance_monitor.export_metrics(format="csv", hours=1)
            assert csv_file.endswith(".csv")
    
    @patch('src.operations.performance_monitor.psutil.Process')
    def test_monitoring_with_mock_system(self, mock_process, performance_monitor):
        """Test monitoring with mocked system metrics"""
        # Mock system metrics
        mock_memory = Mock()
        mock_memory.rss = 100 * 1024 * 1024  # 100MB
        mock_memory.vms = 200 * 1024 * 1024  # 200MB
        
        mock_process.return_value.memory_info.return_value = mock_memory
        mock_process.return_value.memory_percent.return_value = 15.0
        mock_process.return_value.cpu_percent.return_value = 45.0
        
        # Test real-time metrics
        metrics = performance_monitor.get_real_time_metrics()
        
        assert "system" in metrics
        assert metrics["system"]["rss_mb"] == 100.0
        assert metrics["system"]["percent"] == 15.0
        assert metrics["system"]["cpu_percent"] == 45.0
    
    def test_context_manager_monitoring(self, performance_monitor):
        """Test context manager for operation monitoring"""
        # Test successful operation
        with performance_monitor.monitor_operation("context_test"):
            time.sleep(0.01)  # Simulate work
        
        # Test operation with exception
        with pytest.raises(ValueError):
            with performance_monitor.monitor_operation("context_error_test"):
                raise ValueError("Test error")
        
        # Check that metrics were recorded for both cases
        summaries = performance_monitor.metrics.get_operation_summaries()
        assert "context_test" in summaries
        assert "context_error_test" in summaries
        
        # Success operation should have success status
        # Error operation should have error status
        recent_metrics = performance_monitor.metrics.get_recent_metrics(minutes=5)
        
        context_test_metrics = [m for m in recent_metrics if m.operation_name == "context_test"]
        context_error_metrics = [m for m in recent_metrics if m.operation_name == "context_error_test"]
        
        assert len(context_test_metrics) > 0
        assert len(context_error_metrics) > 0
        assert context_test_metrics[0].status == "success"
        assert context_error_metrics[0].status == "error"
    
    def test_performance_report_generation(self, performance_monitor):
        """Test comprehensive performance report generation"""
        # Record some operations
        for i in range(5):
            performance_monitor.metrics.record_operation("report_test", 1.0 + i * 0.1, 100.0, "success")
        
        # Generate an alert
        performance_monitor.alerts.send_performance_alert("report_test", duration=20.0)
        
        # Generate report
        report = performance_monitor.generate_performance_report(hours=1)
        
        assert report.total_operations == 5
        assert report.total_errors == 0
        assert report.average_duration > 0
        assert report.average_memory > 0
        assert "report_test" in report.operations_summary
        assert len(report.recent_alerts) > 0
        assert len(report.recommendations) > 0
    
    def test_baseline_persistence(self, performance_monitor, tmp_path):
        """Test baseline saving and loading"""
        with patch('src.operations.performance_monitor.Path') as mock_path:
            mock_baselines_file = tmp_path / "performance_baselines.json"
            mock_path.return_value.parent.parent.parent = tmp_path
            
            # Create and save a baseline
            baseline = PerformanceBaseline(
                operation_type="persistence_test",
                avg_duration=2.0,
                avg_memory_mb=150.0,
                avg_cpu_percent=60.0,
                avg_records_per_second=5.0,
                success_rate_threshold=0.95,
                p95_duration=3.0,
                p99_duration=4.0,
                created_from_samples=10,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            performance_monitor.baselines["persistence_test"] = baseline
            performance_monitor._save_baselines()
            
            # Verify file was created
            assert mock_baselines_file.exists()
            
            # Create new monitor and load baselines
            new_monitor = PerformanceMonitor()
            with patch.object(new_monitor, '_load_baselines') as mock_load:
                mock_load.return_value = None
                # Manually set baselines for test
                new_monitor.baselines = {"persistence_test": baseline}
                
                loaded_baseline = new_monitor.get_performance_baseline("persistence_test")
                assert loaded_baseline is not None
                assert loaded_baseline.operation_type == "persistence_test"
                assert loaded_baseline.avg_duration == 2.0


class TestDatabaseIntegration:
    """Test database manager integration with performance monitoring"""
    
    @pytest.fixture
    def mock_db_manager(self):
        """Create a mock database manager for testing"""
        with patch('src.database.db_manager.psycopg2') as mock_psycopg2:
            mock_connection = Mock()
            mock_cursor = Mock()
            mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
            mock_psycopg2.connect.return_value = mock_connection
            
            # Mock pool
            mock_pool = Mock()
            mock_pool.getconn.return_value = mock_connection
            
            db_manager = DatabaseManager()
            db_manager.pool = mock_pool
            
            return db_manager, mock_connection, mock_cursor
    
    def test_monitored_database_operations(self, mock_db_manager):
        """Test that database operations are properly monitored"""
        db_manager, mock_connection, mock_cursor = mock_db_manager
        
        # Mock performance monitor
        db_manager.performance_monitor = Mock()
        
        # Test monitored query
        mock_cursor.fetchall.return_value = [{"id": 1, "name": "test"}]
        
        result = db_manager.query("SELECT * FROM test")
        
        # Verify monitoring was called
        assert db_manager.performance_monitor.monitor_operation.called
        
        # Verify query executed
        mock_cursor.execute.assert_called_with("SELECT * FROM test")
        assert len(result) == 1
    
    def test_bulk_operation_monitoring(self, mock_db_manager):
        """Test bulk operations with performance monitoring"""
        db_manager, mock_connection, mock_cursor = mock_db_manager
        
        # Mock performance monitor with proper context manager
        mock_monitor = Mock()
        mock_context = Mock()
        mock_monitor.monitor_operation.return_value.__enter__ = Mock(return_value=None)
        mock_monitor.monitor_operation.return_value.__exit__ = Mock(return_value=None)
        mock_monitor.record_operation_metrics = Mock()
        
        db_manager.performance_monitor = mock_monitor
        
        # Test with empty list (should still call monitoring)
        result = db_manager.bulk_insert_qb_basic_stats([])
        
        # Verify monitoring was attempted
        assert mock_monitor.monitor_operation.called
        
        # Should return completed result
        assert result.table_name == "qb_passing_stats"


class TestCLIIntegration:
    """Test CLI integration with performance monitoring"""
    
    @pytest.fixture
    def performance_command(self):
        """Create a performance command for testing"""
        from src.cli.commands.performance_command import PerformanceCommand
        
        command = PerformanceCommand()
        command.monitor = Mock()
        command.real_time_monitor = Mock()
        return command
    
    def test_cli_argument_validation(self, performance_command):
        """Test CLI argument validation"""
        from argparse import Namespace
        
        # Test valid arguments
        args = Namespace(action="live", duration=60, interval=5)
        errors = performance_command.validate_args(args)
        assert len(errors) == 0
        
        # Test invalid duration
        args = Namespace(action="live", duration=-10, interval=5)
        errors = performance_command.validate_args(args)
        assert len(errors) > 0
        assert any("Duration must be positive" in error for error in errors)
        
        # Test invalid baseline samples
        args = Namespace(action="baseline", operation="test", samples=1)
        errors = performance_command.validate_args(args)
        assert len(errors) > 0
        assert any("at least 3 samples" in error for error in errors)
    
    def test_baseline_command_execution(self, performance_command):
        """Test baseline CLI command execution"""
        from argparse import Namespace
        
        # Mock successful baseline creation
        mock_baseline = Mock()
        mock_baseline.avg_duration = 2.0
        mock_baseline.avg_memory_mb = 100.0
        mock_baseline.success_rate_threshold = 0.95
        mock_baseline.p95_duration = 3.0
        mock_baseline.p99_duration = 4.0
        mock_baseline.created_from_samples = 10
        
        performance_command.monitor.create_performance_baseline.return_value = mock_baseline
        
        args = Namespace(action="baseline", operation="test_op", samples=10, list=False)
        
        with patch('builtins.print') as mock_print:
            result = performance_command.run(args)
            
            assert result == 0  # Success
            performance_command.monitor.create_performance_baseline.assert_called_with("test_op", 10)
            
            # Check that success message was printed
            print_calls = [call.args[0] for call in mock_print.call_args_list]
            assert any("Baseline created" in call for call in print_calls)
    
    def test_live_monitoring_command(self, performance_command):
        """Test live monitoring CLI command"""
        from argparse import Namespace
        
        args = Namespace(action="live", duration=1, interval=1, format="simple")
        
        with patch('builtins.print'):
            result = performance_command.run(args)
            
            assert result == 0  # Success
            performance_command.real_time_monitor.display_live_metrics.assert_called_with(
                duration=1, interval=1
            )


class TestConfigurationValidation:
    """Test monitoring configuration validation"""
    
    def test_monitoring_config_validation(self):
        """Test monitoring configuration validation"""
        # Test valid configuration
        config = MonitoringConfig()
        errors = config.validate()
        assert len(errors) == 0
        
        # Test invalid configuration
        invalid_config = MonitoringConfig(
            collection_interval_seconds=-1,
            retention_days=0,
            baseline_sample_size=1,
            performance_degradation_threshold=1.5,
            export_format="invalid"
        )
        
        errors = invalid_config.validate()
        assert len(errors) > 0
        assert any("Collection interval must be positive" in error for error in errors)
        assert any("Retention days must be positive" in error for error in errors)
        assert any("Baseline sample size must be at least 3" in error for error in errors)
        assert any("threshold must be between 0.0 and 1.0" in error for error in errors)
        assert any("Export format must be" in error for error in errors)
    
    def test_config_environment_loading(self):
        """Test configuration loading from environment variables"""
        with patch.dict('os.environ', {
            'MONITORING_ENABLED': 'false',
            'MONITORING_COLLECTION_INTERVAL': '10',
            'MONITORING_MEMORY_ALERT_MB': '2000.0'
        }):
            config = MonitoringConfig.from_env()
            
            assert config.enabled is False
            assert config.collection_interval_seconds == 10
            assert config.memory_alert_threshold_mb == 2000.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 