#!/usr/bin/env python3
"""
Performance Monitoring System for NFL QB Data Scraping System
Production-grade performance tracking and optimization
"""

import time
import logging
import sys
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
import json
import threading
import psutil
from collections import defaultdict, deque
import functools

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetric:
    """Individual performance metric"""
    operation_name: str
    duration: float
    memory_used: float
    status: str  # 'success', 'error', 'timeout'
    timestamp: datetime
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'operation_name': self.operation_name,
            'duration': self.duration,
            'memory_used': self.memory_used,
            'status': self.status,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        }


@dataclass
class PerformanceAlert:
    """Performance alert"""
    alert_id: str
    operation_name: str
    alert_type: str  # 'timeout', 'memory', 'error_rate'
    severity: str  # 'low', 'medium', 'high', 'critical'
    message: str
    timestamp: datetime
    threshold: float
    actual_value: float
    recommendations: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'alert_id': self.alert_id,
            'operation_name': self.operation_name,
            'alert_type': self.alert_type,
            'severity': self.severity,
            'message': self.message,
            'timestamp': self.timestamp.isoformat(),
            'threshold': self.threshold,
            'actual_value': self.actual_value,
            'recommendations': self.recommendations
        }


@dataclass
class PerformanceReport:
    """Comprehensive performance report"""
    timestamp: datetime
    time_range: timedelta
    total_operations: int
    successful_operations: int
    failed_operations: int
    average_duration: float
    max_duration: float
    min_duration: float
    total_memory_used: float
    average_memory_per_operation: float
    operations_summary: Dict[str, Dict[str, Any]]
    performance_trends: Dict[str, List[float]]
    recent_alerts: List[PerformanceAlert]
    recommendations: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'time_range_seconds': self.time_range.total_seconds(),
            'total_operations': self.total_operations,
            'successful_operations': self.successful_operations,
            'failed_operations': self.failed_operations,
            'success_rate': self.successful_operations / self.total_operations if self.total_operations > 0 else 0,
            'average_duration': self.average_duration,
            'max_duration': self.max_duration,
            'min_duration': self.min_duration,
            'total_memory_used': self.total_memory_used,
            'average_memory_per_operation': self.average_memory_per_operation,
            'operations_summary': self.operations_summary,
            'performance_trends': self.performance_trends,
            'recent_alerts': [alert.to_dict() for alert in self.recent_alerts],
            'recommendations': self.recommendations
        }


class MetricsCollector:
    """Collect and store performance metrics"""
    
    def __init__(self, max_metrics: int = 10000):
        """Initialize metrics collector"""
        self.metrics: deque = deque(maxlen=max_metrics)
        self.operation_summaries: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            'count': 0,
            'total_duration': 0.0,
            'total_memory': 0.0,
            'success_count': 0,
            'error_count': 0,
            'min_duration': float('inf'),
            'max_duration': 0.0,
            'recent_durations': deque(maxlen=100)
        })
        self.lock = threading.Lock()
    
    def record_operation(self, operation_name: str, duration: float, 
                        memory_used: float, status: str, metadata: Dict[str, Any] = None):
        """Record a performance metric"""
        metric = PerformanceMetric(
            operation_name=operation_name,
            duration=duration,
            memory_used=memory_used,
            status=status,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        
        with self.lock:
            self.metrics.append(metric)
            
            # Update operation summary
            summary = self.operation_summaries[operation_name]
            summary['count'] += 1
            summary['total_duration'] += duration
            summary['total_memory'] += memory_used
            summary['recent_durations'].append(duration)
            
            if status == 'success':
                summary['success_count'] += 1
            else:
                summary['error_count'] += 1
            
            summary['min_duration'] = min(summary['min_duration'], duration)
            summary['max_duration'] = max(summary['max_duration'], duration)
    
    def get_operation_summaries(self) -> Dict[str, Dict[str, Any]]:
        """Get summaries for all operations"""
        with self.lock:
            summaries = {}
            for op_name, summary in self.operation_summaries.items():
                if summary['count'] > 0:
                    summaries[op_name] = {
                        'count': summary['count'],
                        'average_duration': summary['total_duration'] / summary['count'],
                        'average_memory': summary['total_memory'] / summary['count'],
                        'success_rate': summary['success_count'] / summary['count'],
                        'min_duration': summary['min_duration'] if summary['min_duration'] != float('inf') else 0,
                        'max_duration': summary['max_duration'],
                        'recent_average': sum(summary['recent_durations']) / len(summary['recent_durations']) if summary['recent_durations'] else 0
                    }
            return summaries
    
    def get_performance_trends(self, hours: int = 24) -> Dict[str, List[float]]:
        """Get performance trends over time"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        with self.lock:
            trends = defaultdict(list)
            for metric in self.metrics:
                if metric.timestamp >= cutoff_time:
                    trends[metric.operation_name].append(metric.duration)
            
            # Calculate hourly averages
            hourly_trends = {}
            for op_name, durations in trends.items():
                if durations:
                    # Simple average for now, could be enhanced with proper time bucketing
                    hourly_trends[op_name] = [sum(durations) / len(durations)]
            
            return hourly_trends
    
    def get_recent_metrics(self, minutes: int = 60) -> List[PerformanceMetric]:
        """Get recent metrics within specified time window"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        
        with self.lock:
            return [metric for metric in self.metrics if metric.timestamp >= cutoff_time]


class AlertManager:
    """Manage performance alerts"""
    
    def __init__(self):
        """Initialize alert manager"""
        self.alerts: List[PerformanceAlert] = []
        self.thresholds = {
            'timeout': {
                'scrape_operation': 30.0,
                'validation_operation': 10.0,
                'export_operation': 60.0,
                'import_operation': 60.0,
                'default': 15.0
            },
            'memory': {
                'scrape_operation': 500.0,  # MB
                'validation_operation': 200.0,
                'export_operation': 1000.0,
                'import_operation': 1000.0,
                'default': 300.0
            },
            'error_rate': {
                'default': 0.1  # 10% error rate threshold
            }
        }
        self.lock = threading.Lock()
    
    def send_performance_alert(self, operation: str, duration: float, 
                             memory_used: float = 0.0, error_rate: float = 0.0):
        """Send performance alert if thresholds are exceeded"""
        alerts = []
        
        # Check timeout threshold
        timeout_threshold = self.thresholds['timeout'].get(operation, self.thresholds['timeout']['default'])
        if duration > timeout_threshold:
            severity = 'critical' if duration > timeout_threshold * 2 else 'high'
            alerts.append(PerformanceAlert(
                alert_id=f"timeout_{operation}_{int(time.time())}",
                operation_name=operation,
                alert_type='timeout',
                severity=severity,
                message=f"Operation {operation} took {duration:.2f}s (threshold: {timeout_threshold}s)",
                timestamp=datetime.now(),
                threshold=timeout_threshold,
                actual_value=duration,
                recommendations=[
                    "Optimize the operation implementation",
                    "Check for network issues or external service delays",
                    "Consider implementing caching",
                    "Review database query performance"
                ]
            ))
        
        # Check memory threshold
        memory_threshold = self.thresholds['memory'].get(operation, self.thresholds['memory']['default'])
        if memory_used > memory_threshold:
            severity = 'critical' if memory_used > memory_threshold * 2 else 'high'
            alerts.append(PerformanceAlert(
                alert_id=f"memory_{operation}_{int(time.time())}",
                operation_name=operation,
                alert_type='memory',
                severity=severity,
                message=f"Operation {operation} used {memory_used:.2f}MB (threshold: {memory_threshold}MB)",
                timestamp=datetime.now(),
                threshold=memory_threshold,
                actual_value=memory_used,
                recommendations=[
                    "Optimize memory usage in the operation",
                    "Consider streaming for large datasets",
                    "Review data structures and algorithms",
                    "Check for memory leaks"
                ]
            ))
        
        # Check error rate threshold
        error_threshold = self.thresholds['error_rate']['default']
        if error_rate > error_threshold:
            severity = 'critical' if error_rate > error_threshold * 2 else 'high'
            alerts.append(PerformanceAlert(
                alert_id=f"error_rate_{operation}_{int(time.time())}",
                operation_name=operation,
                alert_type='error_rate',
                severity=severity,
                message=f"Operation {operation} has {error_rate:.1%} error rate (threshold: {error_threshold:.1%})",
                timestamp=datetime.now(),
                threshold=error_threshold,
                actual_value=error_rate,
                recommendations=[
                    "Investigate error causes",
                    "Improve error handling and recovery",
                    "Check external service availability",
                    "Review input data quality"
                ]
            ))
        
        # Add alerts to the list
        with self.lock:
            self.alerts.extend(alerts)
            # Keep only recent alerts (last 1000)
            if len(self.alerts) > 1000:
                self.alerts = self.alerts[-1000:]
        
        return alerts
    
    def get_recent_alerts(self, hours: int = 24) -> List[PerformanceAlert]:
        """Get recent alerts within specified time window"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        with self.lock:
            return [alert for alert in self.alerts if alert.timestamp >= cutoff_time]
    
    def get_alerts_by_severity(self, severity: str) -> List[PerformanceAlert]:
        """Get alerts by severity level"""
        with self.lock:
            return [alert for alert in self.alerts if alert.severity == severity]


class PerformanceMonitor:
    """Main performance monitoring system"""
    
    def __init__(self):
        """Initialize performance monitor"""
        self.metrics = MetricsCollector()
        self.alerts = AlertManager()
        self.monitoring_enabled = True
    
    def track_operation(self, operation_name: str):
        """Decorator to track operation performance"""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                if not self.monitoring_enabled:
                    return func(*args, **kwargs)
                
                start_time = time.time()
                start_memory = self._get_memory_usage()
                
                try:
                    result = func(*args, **kwargs)
                    status = 'success'
                    return result
                except Exception as e:
                    status = 'error'
                    raise
                finally:
                    elapsed = time.time() - start_time
                    memory_used = self._get_memory_usage() - start_memory
                    
                    # Record metric
                    self.metrics.record_operation(
                        operation_name=operation_name,
                        duration=elapsed,
                        memory_used=memory_used,
                        status=status,
                        metadata={'function': func.__name__}
                    )
                    
                    # Check for alerts
                    alerts = self.alerts.send_performance_alert(
                        operation=operation_name,
                        duration=elapsed,
                        memory_used=memory_used
                    )
                    
                    # Log alerts
                    for alert in alerts:
                        if alert.severity in ['high', 'critical']:
                            logger.warning(f"Performance alert: {alert.message}")
                        else:
                            logger.info(f"Performance alert: {alert.message}")
            
            return wrapper
        return decorator
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # Convert to MB
        except:
            return 0.0
    
    def get_threshold(self, operation_name: str, metric_type: str = 'timeout') -> float:
        """Get threshold for operation and metric type"""
        return self.alerts.thresholds.get(metric_type, {}).get(operation_name, 
               self.alerts.thresholds.get(metric_type, {}).get('default', 15.0))
    
    def generate_performance_report(self, hours: int = 24) -> PerformanceReport:
        """Generate comprehensive performance report"""
        time_range = timedelta(hours=hours)
        recent_metrics = self.metrics.get_recent_metrics(minutes=hours * 60)
        
        if not recent_metrics:
            return PerformanceReport(
                timestamp=datetime.now(),
                time_range=time_range,
                total_operations=0,
                successful_operations=0,
                failed_operations=0,
                average_duration=0.0,
                max_duration=0.0,
                min_duration=0.0,
                total_memory_used=0.0,
                average_memory_per_operation=0.0,
                operations_summary={},
                performance_trends={},
                recent_alerts=[],
                recommendations=[]
            )
        
        # Calculate overall statistics
        total_operations = len(recent_metrics)
        successful_operations = sum(1 for m in recent_metrics if m.status == 'success')
        failed_operations = total_operations - successful_operations
        
        durations = [m.duration for m in recent_metrics]
        memory_usage = [m.memory_used for m in recent_metrics]
        
        average_duration = sum(durations) / len(durations)
        max_duration = max(durations)
        min_duration = min(durations)
        total_memory_used = sum(memory_usage)
        average_memory_per_operation = total_memory_used / total_operations
        
        # Get operation summaries and trends
        operations_summary = self.metrics.get_operation_summaries()
        performance_trends = self.metrics.get_performance_trends(hours)
        recent_alerts = self.alerts.get_recent_alerts(hours)
        
        # Generate recommendations
        recommendations = self._generate_optimization_recommendations(
            operations_summary, recent_alerts, average_duration, average_memory_per_operation
        )
        
        return PerformanceReport(
            timestamp=datetime.now(),
            time_range=time_range,
            total_operations=total_operations,
            successful_operations=successful_operations,
            failed_operations=failed_operations,
            average_duration=average_duration,
            max_duration=max_duration,
            min_duration=min_duration,
            total_memory_used=total_memory_used,
            average_memory_per_operation=average_memory_per_operation,
            operations_summary=operations_summary,
            performance_trends=performance_trends,
            recent_alerts=recent_alerts,
            recommendations=recommendations
        )
    
    def _generate_optimization_recommendations(self, operations_summary: Dict[str, Dict[str, Any]], 
                                             recent_alerts: List[PerformanceAlert],
                                             average_duration: float,
                                             average_memory: float) -> List[str]:
        """Generate optimization recommendations based on performance data"""
        recommendations = []
        
        # Check for slow operations
        for op_name, summary in operations_summary.items():
            if summary['average_duration'] > 10.0:
                recommendations.append(f"Optimize {op_name} (avg: {summary['average_duration']:.2f}s)")
            
            if summary['success_rate'] < 0.9:
                recommendations.append(f"Improve error handling for {op_name} (success rate: {summary['success_rate']:.1%})")
        
        # Check for high memory usage
        if average_memory > 500.0:
            recommendations.append("Consider implementing memory optimization strategies")
        
        # Check for critical alerts
        critical_alerts = [a for a in recent_alerts if a.severity == 'critical']
        if critical_alerts:
            recommendations.append(f"Address {len(critical_alerts)} critical performance alerts")
        
        # General recommendations
        if average_duration > 5.0:
            recommendations.append("Consider implementing caching for frequently accessed data")
        
        if len(recent_alerts) > 10:
            recommendations.append("Review and adjust performance thresholds")
        
        return recommendations
    
    def save_report(self, report: PerformanceReport, filename: str = None) -> str:
        """Save performance report to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_report_{timestamp}.json"
        
        logs_dir = Path(__file__).parent.parent.parent / "logs"
        logs_dir.mkdir(exist_ok=True)
        
        report_path = logs_dir / filename
        
        with open(report_path, 'w') as f:
            json.dump(report.to_dict(), f, indent=2)
        
        logger.info(f"Performance report saved to: {report_path}")
        return str(report_path)
    
    def enable_monitoring(self):
        """Enable performance monitoring"""
        self.monitoring_enabled = True
        logger.info("Performance monitoring enabled")
    
    def disable_monitoring(self):
        """Disable performance monitoring"""
        self.monitoring_enabled = False
        logger.info("Performance monitoring disabled")
    
    def clear_metrics(self):
        """Clear all collected metrics"""
        self.metrics.metrics.clear()
        self.metrics.operation_summaries.clear()
        logger.info("Performance metrics cleared")
    
    def clear_alerts(self):
        """Clear all alerts"""
        self.alerts.alerts.clear()
        logger.info("Performance alerts cleared") 