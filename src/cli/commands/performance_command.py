#!/usr/bin/env python3
"""
Performance Monitoring CLI Commands
Provides comprehensive performance monitoring and analysis capabilities
"""

import argparse
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

from ..base_command import BaseCommand
from ...operations.performance_monitor import PerformanceMonitor, RealTimeMonitor
from ...config.config import config

class PerformanceCommand(BaseCommand):
    """Performance monitoring command with real-time capabilities"""
    
    # Class variables instead of properties
    name: str = "performance"
    description: str = "Monitor system performance in real-time"
    aliases: List[str] = ["perf"]
    
    def __init__(self):
        super().__init__()
        self.monitor = PerformanceMonitor(config)
        self.real_time_monitor = RealTimeMonitor(self.monitor)
    
    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """Add command-specific arguments"""
        
        # Subcommands for different monitoring operations
        subparsers = parser.add_subparsers(dest='action', help='Performance monitoring actions')
        
        # Real-time monitoring
        live_parser = subparsers.add_parser('live', help='Display live performance metrics')
        live_parser.add_argument(
            '--duration', '-d',
            type=int,
            default=60,
            help='Monitoring duration in seconds (default: 60)'
        )
        live_parser.add_argument(
            '--interval', '-i',
            type=int,
            default=5,
            help='Update interval in seconds (default: 5)'
        )
        live_parser.add_argument(
            '--format',
            choices=['table', 'simple'],
            default='table',
            help='Display format (default: table)'
        )
        
        # Baseline management
        baseline_parser = subparsers.add_parser('baseline', help='Manage performance baselines')
        baseline_parser.add_argument(
            '--operation', '-o',
            required=True,
            help='Operation type to create baseline for'
        )
        baseline_parser.add_argument(
            '--samples', '-s',
            type=int,
            default=10,
            help='Number of samples for baseline (default: 10)'
        )
        baseline_parser.add_argument(
            '--list',
            action='store_true',
            help='List existing baselines'
        )
        
        # Performance validation
        validate_parser = subparsers.add_parser('validate', help='Validate performance against baseline')
        validate_parser.add_argument(
            '--operation', '-o',
            required=True,
            help='Operation type to validate'
        )
        validate_parser.add_argument(
            '--baseline-file',
            help='Custom baseline file to compare against'
        )
        validate_parser.add_argument(
            '--hours',
            type=int,
            default=1,
            help='Hours of recent data to analyze (default: 1)'
        )
        
        # Metrics export
        export_parser = subparsers.add_parser('export', help='Export performance metrics')
        export_parser.add_argument(
            '--format', '-f',
            choices=['json', 'csv', 'html'],
            default='json',
            help='Export format (default: json)'
        )
        export_parser.add_argument(
            '--hours',
            type=int,
            default=24,
            help='Hours of data to export (default: 24)'
        )
        export_parser.add_argument(
            '--output', '-o',
            help='Output file path (default: auto-generated)'
        )
        
        # Performance report
        report_parser = subparsers.add_parser('report', help='Generate performance report')
        report_parser.add_argument(
            '--hours',
            type=int,
            default=24,
            help='Hours of data for report (default: 24)'
        )
        report_parser.add_argument(
            '--format',
            choices=['json', 'summary'],
            default='summary',
            help='Report format (default: summary)'
        )
        report_parser.add_argument(
            '--save',
            action='store_true',
            help='Save report to file'
        )
        
        # Metrics summary
        summary_parser = subparsers.add_parser('summary', help='Show performance summary')
        summary_parser.add_argument(
            '--hours',
            type=int,
            default=24,
            help='Hours of data to summarize (default: 24)'
        )
        summary_parser.add_argument(
            '--operation',
            help='Filter by specific operation'
        )
        
        # Alerts management
        alerts_parser = subparsers.add_parser('alerts', help='Manage performance alerts')
        alerts_parser.add_argument(
            '--list',
            action='store_true',
            help='List recent alerts'
        )
        alerts_parser.add_argument(
            '--severity',
            choices=['low', 'medium', 'high', 'critical'],
            help='Filter alerts by severity'
        )
        alerts_parser.add_argument(
            '--hours',
            type=int,
            default=24,
            help='Hours of alerts to show (default: 24)'
        )
        alerts_parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear all alerts'
        )
        
        # Session management
        session_parser = subparsers.add_parser('session', help='Manage monitoring sessions')
        session_parser.add_argument(
            '--start',
            help='Start new monitoring session with given name'
        )
        session_parser.add_argument(
            '--stop',
            help='Stop monitoring session by ID'
        )
        session_parser.add_argument(
            '--list',
            action='store_true',
            help='List active sessions'
        )
        
        # Configuration
        config_parser = subparsers.add_parser('config', help='Show monitoring configuration')
        config_parser.add_argument(
            '--validate',
            action='store_true',
            help='Validate configuration'
        )
    
    def validate_args(self, args: argparse.Namespace) -> list:
        """Validate command arguments"""
        errors = []
        
        if not args.action:
            errors.append("No action specified. Use --help to see available actions.")
            return errors
        
        # Action-specific validation
        if args.action == 'baseline':
            if not hasattr(args, 'operation') or not args.operation:
                if not args.list:
                    errors.append("Operation name is required for baseline creation")
            
            if hasattr(args, 'samples') and args.samples < 3:
                errors.append("Baseline requires at least 3 samples")
        
        elif args.action == 'live':
            if args.duration <= 0:
                errors.append("Duration must be positive")
            
            if args.interval <= 0:
                errors.append("Interval must be positive")
            
            if args.interval > args.duration:
                errors.append("Interval cannot be longer than duration")
        
        elif args.action == 'export':
            if args.hours <= 0:
                errors.append("Hours must be positive")
        
        return errors
    
    def run(self, args: argparse.Namespace) -> int:
        """Execute the performance command"""
        try:
            if args.action == 'live':
                return self._run_live_monitoring(args)
            elif args.action == 'baseline':
                return self._run_baseline_management(args)
            elif args.action == 'validate':
                return self._run_performance_validation(args)
            elif args.action == 'export':
                return self._run_metrics_export(args)
            elif args.action == 'report':
                return self._run_performance_report(args)
            elif args.action == 'summary':
                return self._run_performance_summary(args)
            elif args.action == 'alerts':
                return self._run_alerts_management(args)
            elif args.action == 'session':
                return self._run_session_management(args)
            elif args.action == 'config':
                return self._run_config_management(args)
            else:
                self.logger.error(f"Unknown action: {args.action}")
                return 1
                
        except KeyboardInterrupt:
            self.logger.info("Performance monitoring cancelled by user")
            return 130
        except Exception as e:
            self.logger.error(f"Performance monitoring failed: {e}")
            return 1
    
    def _run_live_monitoring(self, args: argparse.Namespace) -> int:
        """Run live performance monitoring"""
        self.logger.info(f"Starting live performance monitoring for {args.duration}s")
        
        print(f"🔍 Live Performance Monitoring")
        print(f"Duration: {args.duration}s | Update Interval: {args.interval}s")
        print(f"Press Ctrl+C to stop early\n")
        
        try:
            self.real_time_monitor.display_live_metrics(
                duration=args.duration,
                interval=args.interval
            )
            
            # Show final summary
            print(f"\n📊 Final Summary:")
            real_time_metrics = self.monitor.get_real_time_metrics()
            system = real_time_metrics.get('system', {})
            
            print(f"Final CPU Usage: {system.get('cpu_percent', 0):.1f}%")
            print(f"Final Memory Usage: {system.get('rss_mb', 0):.1f} MB")
            print(f"Active Sessions: {real_time_metrics.get('active_sessions', 0)}")
            print(f"Recent Alerts: {len(real_time_metrics.get('recent_alerts', []))}")
            
            self.logger.info("Live monitoring completed successfully")
            return 0
            
        except Exception as e:
            self.logger.error(f"Live monitoring failed: {e}")
            return 1
    
    def _run_baseline_management(self, args: argparse.Namespace) -> int:
        """Manage performance baselines"""
        if args.list:
            baselines = self.monitor.baselines
            if not baselines:
                print("No performance baselines found")
                return 0
            
            print("📈 Performance Baselines:")
            print("-" * 60)
            for op_type, baseline in baselines.items():
                print(f"Operation: {op_type}")
                print(f"  Average Duration: {baseline.avg_duration:.2f}s")
                print(f"  Average Memory: {baseline.avg_memory_mb:.2f} MB")
                print(f"  Success Rate: {baseline.success_rate_threshold:.2%}")
                print(f"  P95 Duration: {baseline.p95_duration:.2f}s")
                print(f"  Created: {baseline.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"  Samples: {baseline.created_from_samples}")
                print()
            
            return 0
        
        # Create baseline
        self.logger.info(f"Creating baseline for operation: {args.operation}")
        baseline = self.monitor.create_performance_baseline(args.operation, args.samples)
        
        if baseline:
            print(f"✅ Baseline created for '{args.operation}':")
            print(f"  Average Duration: {baseline.avg_duration:.2f}s")
            print(f"  Average Memory: {baseline.avg_memory_mb:.2f} MB")
            print(f"  Success Rate: {baseline.success_rate_threshold:.2%}")
            print(f"  P95 Duration: {baseline.p95_duration:.2f}s")
            print(f"  P99 Duration: {baseline.p99_duration:.2f}s")
            print(f"  Created from {baseline.created_from_samples} samples")
            
            self.logger.info(f"Baseline created successfully for {args.operation}")
            return 0
        else:
            print(f"❌ Failed to create baseline for '{args.operation}'")
            print(f"   Insufficient data samples (need at least {args.samples})")
            return 1
    
    def _run_performance_validation(self, args: argparse.Namespace) -> int:
        """Validate performance against baseline"""
        baseline = self.monitor.get_performance_baseline(args.operation)
        if not baseline:
            print(f"❌ No baseline found for operation '{args.operation}'")
            print("   Create a baseline first using: performance baseline --operation <name>")
            return 1
        
        # Get recent metrics for the operation
        operations_summary = self.monitor.metrics.get_operation_summaries()
        current_metrics = operations_summary.get(args.operation)
        
        if not current_metrics:
            print(f"❌ No recent performance data found for operation '{args.operation}'")
            return 1
        
        # Validate performance
        validation = self.monitor.validate_performance_against_baseline(current_metrics, baseline)
        
        print(f"🔍 Performance Validation for '{args.operation}':")
        print("-" * 60)
        
        if validation.passed:
            print("✅ PERFORMANCE VALIDATION PASSED")
        else:
            print("❌ PERFORMANCE VALIDATION FAILED")
        
        print(f"\nBaseline Comparison:")
        print(f"  Duration: {current_metrics.get('avg_duration', 0):.2f}s vs {baseline.avg_duration:.2f}s (baseline)")
        print(f"  Memory: {current_metrics.get('avg_memory', 0):.2f}MB vs {baseline.avg_memory_mb:.2f}MB (baseline)")
        print(f"  Success Rate: {current_metrics.get('success_rate', 1.0):.2%} vs {baseline.success_rate_threshold:.2%} (baseline)")
        
        if validation.improvement_percentage:
            if validation.improvement_percentage > 0:
                print(f"  Performance: {validation.improvement_percentage:.1f}% FASTER than baseline ✅")
            else:
                print(f"  Performance: {abs(validation.improvement_percentage):.1f}% SLOWER than baseline ⚠️")
        
        if validation.violations:
            print(f"\n❌ Performance Violations:")
            for violation in validation.violations:
                print(f"  • {violation}")
        
        if validation.warnings:
            print(f"\n⚠️ Performance Warnings:")
            for warning in validation.warnings:
                print(f"  • {warning}")
        
        return 0 if validation.passed else 1
    
    def _run_metrics_export(self, args: argparse.Namespace) -> int:
        """Export performance metrics"""
        try:
            filepath = self.monitor.export_metrics(
                format=args.format,
                hours=args.hours
            )
            
            print(f"✅ Metrics exported successfully:")
            print(f"   Format: {args.format.upper()}")
            print(f"   Time Range: {args.hours} hours")
            print(f"   Output File: {filepath}")
            
            self.logger.info(f"Metrics exported to {filepath}")
            return 0
            
        except Exception as e:
            print(f"❌ Failed to export metrics: {e}")
            self.logger.error(f"Metrics export failed: {e}")
            return 1
    
    def _run_performance_report(self, args: argparse.Namespace) -> int:
        """Generate performance report"""
        try:
            report = self.monitor.generate_performance_report(hours=args.hours)
            
            if args.format == 'summary':
                self._display_report_summary(report)
            else:
                print(json.dumps(report.to_dict(), indent=2))
            
            if args.save:
                filepath = self.monitor.save_report(report)
                print(f"\n💾 Report saved to: {filepath}")
            
            return 0
            
        except Exception as e:
            print(f"❌ Failed to generate report: {e}")
            self.logger.error(f"Report generation failed: {e}")
            return 1
    
    def _display_report_summary(self, report) -> None:
        """Display a human-readable report summary"""
        print(f"📊 Performance Report Summary")
        print("=" * 60)
        print(f"Time Range: {report.time_range_hours} hours")
        print(f"Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Report ID: {report.report_id}")
        print()
        
        print(f"📈 Overall Statistics:")
        print(f"  Total Operations: {report.total_operations:,}")
        print(f"  Total Errors: {report.total_errors:,}")
        print(f"  Success Rate: {((report.total_operations - report.total_errors) / report.total_operations * 100) if report.total_operations > 0 else 0:.1f}%")
        print(f"  Average Duration: {report.average_duration:.2f}s")
        print(f"  Average Memory: {report.average_memory:.2f}MB")
        print()
        
        if report.operations_summary:
            print(f"🔧 Operations Summary:")
            for op_name, summary in report.operations_summary.items():
                print(f"  {op_name}:")
                print(f"    Count: {summary.get('count', 0):,}")
                print(f"    Success Rate: {summary.get('success_rate', 0):.2%}")
                print(f"    Avg Duration: {summary.get('avg_duration', 0):.2f}s")
                print(f"    P95 Duration: {summary.get('p95_duration', 0):.2f}s")
            print()
        
        if report.recent_alerts:
            print(f"⚠️ Recent Alerts ({len(report.recent_alerts)}):")
            for alert in report.recent_alerts[-5:]:  # Show last 5 alerts
                print(f"  [{alert.severity.upper()}] {alert.message}")
            print()
        
        if report.recommendations:
            print(f"💡 Recommendations:")
            for i, rec in enumerate(report.recommendations, 1):
                print(f"  {i}. {rec}")
    
    def _run_performance_summary(self, args: argparse.Namespace) -> int:
        """Show performance summary"""
        operations_summary = self.monitor.metrics.get_operation_summaries()
        
        if not operations_summary:
            print("No performance data available")
            return 0
        
        # Filter by operation if specified
        if args.operation:
            operations_summary = {
                k: v for k, v in operations_summary.items() 
                if args.operation.lower() in k.lower()
            }
            
            if not operations_summary:
                print(f"No data found for operation: {args.operation}")
                return 0
        
        print(f"📊 Performance Summary (Last {args.hours} hours)")
        print("=" * 80)
        
        for op_name, summary in operations_summary.items():
            print(f"\n🔧 {op_name}")
            print(f"   Operations: {summary.get('count', 0):,}")
            print(f"   Success Rate: {summary.get('success_rate', 0):.2%}")
            print(f"   Avg Duration: {summary.get('avg_duration', 0):.2f}s")
            print(f"   Min/Max Duration: {summary.get('min_duration', 0):.2f}s / {summary.get('max_duration', 0):.2f}s")
            print(f"   P95/P99 Duration: {summary.get('p95_duration', 0):.2f}s / {summary.get('p99_duration', 0):.2f}s")
            print(f"   Avg Memory: {summary.get('avg_memory', 0):.2f}MB")
            print(f"   Avg CPU: {summary.get('avg_cpu', 0):.1f}%")
            print(f"   Records/sec: {summary.get('records_per_second', 0):.1f}")
        
        return 0
    
    def _run_alerts_management(self, args: argparse.Namespace) -> int:
        """Manage performance alerts"""
        if args.clear:
            self.monitor.clear_alerts()
            print("✅ All alerts cleared")
            return 0
        
        # Get alerts
        if args.severity:
            alerts = self.monitor.alerts.get_alerts_by_severity(args.severity)
        else:
            alerts = self.monitor.alerts.get_recent_alerts(hours=args.hours)
        
        if not alerts:
            print("No alerts found")
            return 0
        
        print(f"⚠️ Performance Alerts (Last {args.hours} hours)")
        print("=" * 60)
        
        # Group by severity
        alerts_by_severity = {'critical': [], 'high': [], 'medium': [], 'low': []}
        for alert in alerts:
            alerts_by_severity[alert.severity].append(alert)
        
        for severity in ['critical', 'high', 'medium', 'low']:
            severity_alerts = alerts_by_severity[severity]
            if severity_alerts:
                icon = {'critical': '🚨', 'high': '⚠️', 'medium': '⚡', 'low': 'ℹ️'}[severity]
                print(f"\n{icon} {severity.upper()} ({len(severity_alerts)} alerts)")
                
                for alert in severity_alerts[-10:]:  # Show last 10 per severity
                    print(f"   {alert.timestamp.strftime('%H:%M:%S')} | {alert.operation_name} | {alert.message}")
        
        return 0
    
    def _run_session_management(self, args: argparse.Namespace) -> int:
        """Manage monitoring sessions"""
        if args.start:
            session = self.monitor.start_monitoring_session(operation_type=args.start)
            print(f"✅ Started monitoring session: {session.session_id}")
            print(f"   Operation Type: {session.operation_type}")
            print(f"   Started At: {session.started_at.strftime('%Y-%m-%d %H:%M:%S')}")
            return 0
        
        elif args.stop:
            session = self.monitor.end_monitoring_session(args.stop)
            if session:
                print(f"✅ Stopped monitoring session: {session.session_id}")
                print(f"   Duration: {session.get_duration():.2f} seconds")
            else:
                print(f"❌ Session not found: {args.stop}")
                return 1
            return 0
        
        elif args.list:
            sessions = self.monitor.sessions
            if not sessions:
                print("No active monitoring sessions")
                return 0
            
            print("🔄 Active Monitoring Sessions:")
            print("-" * 60)
            
            for session_id, session in sessions.items():
                status = "Active" if session.ended_at is None else "Completed"
                duration = session.get_duration()
                
                print(f"Session ID: {session_id}")
                print(f"  Operation: {session.operation_type}")
                print(f"  Status: {status}")
                print(f"  Duration: {duration:.2f}s")
                print(f"  Started: {session.started_at.strftime('%Y-%m-%d %H:%M:%S')}")
                if session.ended_at:
                    print(f"  Ended: {session.ended_at.strftime('%Y-%m-%d %H:%M:%S')}")
                print()
            
            return 0
        
        else:
            print("No session action specified. Use --help for options.")
            return 1
    
    def _run_config_management(self, args: argparse.Namespace) -> int:
        """Show monitoring configuration"""
        if args.validate:
            errors = config.monitoring.validate()
            if errors:
                print("❌ Configuration Validation Errors:")
                for error in errors:
                    print(f"  • {error}")
                return 1
            else:
                print("✅ Configuration validation passed")
        
        print("⚙️ Monitoring Configuration:")
        print("-" * 40)
        print(f"Enabled: {config.monitoring.enabled}")
        print(f"Collection Interval: {config.monitoring.collection_interval_seconds}s")
        print(f"Retention Days: {config.monitoring.retention_days}")
        print(f"Baseline Sample Size: {config.monitoring.baseline_sample_size}")
        print(f"Performance Degradation Threshold: {config.monitoring.performance_degradation_threshold:.1%}")
        print(f"Memory Alert Threshold: {config.monitoring.memory_alert_threshold_mb}MB")
        print(f"CPU Alert Threshold: {config.monitoring.cpu_alert_threshold_percent}%")
        print(f"Error Rate Alert Threshold: {config.monitoring.error_rate_alert_threshold:.1%}")
        print(f"Export Format: {config.monitoring.export_format}")
        print(f"Auto Baseline Creation: {config.monitoring.auto_baseline_creation}")
        
        print(f"\nOperation-specific Thresholds:")
        for operation, threshold in config.monitoring.alert_thresholds.items():
            print(f"  {operation}: {threshold}s")
        
        return 0 