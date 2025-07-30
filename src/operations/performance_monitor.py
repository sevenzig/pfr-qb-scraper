#!/usr/bin/env python3
"""
Performance Monitoring System for NFL QB Data Scraping System
Production-grade performance tracking and optimization
"""

import time
import logging
import sys
import os
import json
import csv
import uuid
import threading
import psutil
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union, Callable, Iterator
from dataclasses import dataclass, asdict, field
from pathlib import Path
from collections import defaultdict, deque
import functools
from contextlib import contextmanager
from enum import Enum

# Optional imports for enhanced functionality
try:
    from rich.console import Console
    from rich.table import Table
    from rich.live import Live
    from rich.progress import Progress, TaskID, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
    from rich.layout import Layout
    from rich.panel import Panel
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Types of metrics that can be collected"""
    DURATION = "duration"
    MEMORY = "memory"
    CPU = "cpu"
    NETWORK = "network"
    DATABASE = "database"
    ERROR_RATE = "error_rate"
    THROUGHPUT = "throughput"
    CUSTOM = "custom"

class AlertSeverity(Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class Metric:
    """Individual metric data point"""
    name: str
    value: Union[int, float, str]
    timestamp: datetime
    labels: Dict[str, str] = field(default_factory=dict)
    metric_type: MetricType = MetricType.CUSTOM
    unit: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'name': self.name,
            'value': self.value,
            'timestamp': self.timestamp.isoformat(),
            'labels': self.labels,
            'metric_type': self.metric_type.value,
            'unit': self.unit
        }

@dataclass
class MonitoringSession:
    """A monitoring session that tracks metrics over time"""
    session_id: str
    operation_type: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    metrics: Dict[str, List[Metric]] = field(default_factory=lambda: defaultdict(list))
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_metric(self, metric: Metric) -> None:
        """Add a metric to this session"""
        self.metrics[metric.name].append(metric)
    
    def get_metric_values(self, metric_name: str) -> List[Union[int, float]]:
        """Get all values for a specific metric"""
        return [m.value for m in self.metrics.get(metric_name, []) if isinstance(m.value, (int, float))]
    
    def get_latest_metric(self, metric_name: str) -> Optional[Metric]:
        """Get the latest value for a specific metric"""
        metrics = self.metrics.get(metric_name, [])
        return metrics[-1] if metrics else None
    
    def get_duration(self) -> Optional[float]:
        """Get session duration in seconds"""
        if self.ended_at:
            return (self.ended_at - self.started_at).total_seconds()
        return (datetime.now() - self.started_at).total_seconds()

@dataclass
class PerformanceBaseline:
    """Performance baseline for an operation type"""
    operation_type: str
    avg_duration: float
    avg_memory_mb: float
    avg_cpu_percent: float
    avg_records_per_second: float
    success_rate_threshold: float
    p95_duration: float
    p99_duration: float
    created_from_samples: int
    created_at: datetime
    updated_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'operation_type': self.operation_type,
            'avg_duration': self.avg_duration,
            'avg_memory_mb': self.avg_memory_mb,
            'avg_cpu_percent': self.avg_cpu_percent,
            'avg_records_per_second': self.avg_records_per_second,
            'success_rate_threshold': self.success_rate_threshold,
            'p95_duration': self.p95_duration,
            'p99_duration': self.p99_duration,
            'created_from_samples': self.created_from_samples,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

@dataclass
class ValidationResult:
    """Result of performance validation against baseline"""
    operation_type: str
    baseline: PerformanceBaseline
    current_metrics: Dict[str, float]
    passed: bool
    violations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    improvement_percentage: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'operation_type': self.operation_type,
            'baseline': self.baseline.to_dict(),
            'current_metrics': self.current_metrics,
            'passed': self.passed,
            'violations': self.violations,
            'warnings': self.warnings,
            'improvement_percentage': self.improvement_percentage
        }

# Existing dataclasses from the original file
@dataclass
class PerformanceMetric:
    """Individual performance metric (legacy compatibility)"""
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
    report_id: str
    generated_at: datetime
    time_range_hours: int
    total_operations: int
    total_errors: int
    average_duration: float
    average_memory: float
    operations_summary: Dict[str, Dict[str, Any]]
    performance_trends: Dict[str, List[float]]
    recent_alerts: List[PerformanceAlert]
    recommendations: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'report_id': self.report_id,
            'generated_at': self.generated_at.isoformat(),
            'time_range_hours': self.time_range_hours,
            'total_operations': self.total_operations,
            'total_errors': self.total_errors,
            'average_duration': self.average_duration,
            'average_memory': self.average_memory,
            'operations_summary': self.operations_summary,
            'performance_trends': self.performance_trends,
            'recent_alerts': [alert.to_dict() for alert in self.recent_alerts],
            'recommendations': self.recommendations
        }

class SystemMetricsCollector:
    """Collects system-level performance metrics"""
    
    def __init__(self):
        self.process = psutil.Process()
        self._baseline_cpu = None
        self._baseline_memory = None
        self._network_baseline = None
        
    def get_cpu_usage(self) -> float:
        """Get current CPU usage percentage"""
        try:
            return self.process.cpu_percent(interval=0.1)
        except:
            return 0.0
    
    def get_memory_usage(self) -> Dict[str, float]:
        """Get memory usage information"""
        try:
            memory_info = self.process.memory_info()
            return {
                'rss_mb': memory_info.rss / 1024 / 1024,
                'vms_mb': memory_info.vms / 1024 / 1024,
                'percent': self.process.memory_percent()
            }
        except:
            return {'rss_mb': 0.0, 'vms_mb': 0.0, 'percent': 0.0}
    
    def get_network_io(self) -> Dict[str, int]:
        """Get network I/O statistics"""
        try:
            net_io = psutil.net_io_counters()
            return {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv
            }
        except:
            return {'bytes_sent': 0, 'bytes_recv': 0, 'packets_sent': 0, 'packets_recv': 0}
    
    def get_disk_io(self) -> Dict[str, int]:
        """Get disk I/O statistics"""
        try:
            disk_io = psutil.disk_io_counters()
            if disk_io is None:
                return {'read_bytes': 0, 'write_bytes': 0, 'read_count': 0, 'write_count': 0}
            return {
                'read_bytes': disk_io.read_bytes,
                'write_bytes': disk_io.write_bytes,
                'read_count': disk_io.read_count,
                'write_count': disk_io.write_count
            }
        except:
            return {'read_bytes': 0, 'write_bytes': 0, 'read_count': 0, 'write_count': 0}

class MetricsCollector:
    """Enhanced metrics collector with advanced aggregation"""
    
    def __init__(self, max_metrics: int = 10000):
        self.metrics: deque = deque(maxlen=max_metrics)
        self.operation_summaries: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            'count': 0,
            'total_duration': 0.0,
            'total_memory': 0.0,
            'success_count': 0,
            'error_count': 0,
            'min_duration': float('inf'),
            'max_duration': 0.0,
            'recent_durations': deque(maxlen=100),
            'recent_memories': deque(maxlen=100),
            'recent_cpu': deque(maxlen=100)
        })
        self.lock = threading.Lock()
        self.system_collector = SystemMetricsCollector()
    
    def record_operation(self, operation_name: str, duration: float, 
                        memory_used: float, status: str, metadata: Optional[Dict[str, Any]] = None,
                        cpu_usage: Optional[float] = None):
        """Record a performance metric with enhanced data"""
        if metadata is None:
            metadata = {}
        
        metric = PerformanceMetric(
            operation_name=operation_name,
            duration=duration,
            memory_used=memory_used,
            status=status,
            timestamp=datetime.now(),
            metadata=metadata
        )
        
        with self.lock:
            self.metrics.append(metric)
            
            # Update operation summary with enhanced metrics
            summary = self.operation_summaries[operation_name]
            summary['count'] += 1
            summary['total_duration'] += duration
            summary['total_memory'] += memory_used
            summary['recent_durations'].append(duration)
            summary['recent_memories'].append(memory_used)
            
            if cpu_usage is not None:
                summary['recent_cpu'].append(cpu_usage)
            
            if status == 'success':
                summary['success_count'] += 1
            else:
                summary['error_count'] += 1
            
            summary['min_duration'] = min(summary['min_duration'], duration)
            summary['max_duration'] = max(summary['max_duration'], duration)
    
    def get_operation_summaries(self) -> Dict[str, Dict[str, Any]]:
        """Get enhanced summaries for all operations"""
        with self.lock:
            summaries = {}
            for op_name, summary in self.operation_summaries.items():
                if summary['count'] > 0:
                    recent_durations = list(summary['recent_durations'])
                    recent_memories = list(summary['recent_memories'])
                    recent_cpu = list(summary['recent_cpu'])
                    
                    summaries[op_name] = {
                        'count': summary['count'],
                        'success_rate': summary['success_count'] / summary['count'],
                        'avg_duration': summary['total_duration'] / summary['count'],
                        'avg_memory': summary['total_memory'] / summary['count'],
                        'min_duration': summary['min_duration'],
                        'max_duration': summary['max_duration'],
                        'p95_duration': self._calculate_percentile(recent_durations, 95),
                        'p99_duration': self._calculate_percentile(recent_durations, 99),
                        'avg_cpu': sum(recent_cpu) / len(recent_cpu) if recent_cpu else 0.0,
                        'records_per_second': summary['count'] / summary['total_duration'] if summary['total_duration'] > 0 else 0.0
                    }
            return summaries
    
    def _calculate_percentile(self, values: List[float], percentile: int) -> float:
        """Calculate percentile value"""
        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        k = (len(sorted_values) - 1) * percentile / 100
        f = int(k)
        c = k - f
        
        if f == len(sorted_values) - 1:
            return sorted_values[f]
        
        return sorted_values[f] * (1 - c) + sorted_values[f + 1] * c
    
    def get_recent_metrics(self, minutes: int = 30) -> List[PerformanceMetric]:
        """Get metrics from the last N minutes"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        with self.lock:
            return [m for m in self.metrics if m.timestamp >= cutoff_time]

class AlertManager:
    """Enhanced alert manager with sophisticated thresholds"""
    
    def __init__(self):
        self.alerts: deque = deque(maxlen=1000)
        self.thresholds = {
            'timeout': {'default': 15.0},
            'memory': {'default': 500.0},  # MB
            'cpu': {'default': 80.0},      # Percent
            'error_rate': {'default': 0.05}, # 5%
            'throughput': {'default': 10.0}  # Records per second
        }
        self.lock = threading.Lock()
    
    def send_performance_alert(self, operation: str, duration: Optional[float] = None, 
                              memory_used: Optional[float] = None, cpu_usage: Optional[float] = None,
                              error_rate: Optional[float] = None) -> List[PerformanceAlert]:
        """Generate performance alerts based on thresholds"""
        alerts = []
        
        # Duration alert
        if duration is not None:
            threshold = self.get_threshold(operation, 'timeout')
            if duration > threshold:
                alert = PerformanceAlert(
                    alert_id=str(uuid.uuid4()),
                    operation_name=operation,
                    alert_type='timeout',
                    severity=self._get_severity(duration, threshold),
                    message=f"Operation {operation} took {duration:.2f}s (threshold: {threshold:.2f}s)",
                    timestamp=datetime.now(),
                    threshold=threshold,
                    actual_value=duration,
                    recommendations=self._get_recommendations('timeout', operation)
                )
                alerts.append(alert)
        
        # Memory alert
        if memory_used is not None:
            threshold = self.get_threshold(operation, 'memory')
            if memory_used > threshold:
                alert = PerformanceAlert(
                    alert_id=str(uuid.uuid4()),
                    operation_name=operation,
                    alert_type='memory',
                    severity=self._get_severity(memory_used, threshold),
                    message=f"Operation {operation} used {memory_used:.2f}MB (threshold: {threshold:.2f}MB)",
                    timestamp=datetime.now(),
                    threshold=threshold,
                    actual_value=memory_used,
                    recommendations=self._get_recommendations('memory', operation)
                )
                alerts.append(alert)
        
        # CPU alert
        if cpu_usage is not None:
            threshold = self.get_threshold(operation, 'cpu')
            if cpu_usage > threshold:
                alert = PerformanceAlert(
                    alert_id=str(uuid.uuid4()),
                    operation_name=operation,
                    alert_type='cpu',
                    severity=self._get_severity(cpu_usage, threshold),
                    message=f"Operation {operation} used {cpu_usage:.2f}% CPU (threshold: {threshold:.2f}%)",
                    timestamp=datetime.now(),
                    threshold=threshold,
                    actual_value=cpu_usage,
                    recommendations=self._get_recommendations('cpu', operation)
                )
                alerts.append(alert)
        
        # Error rate alert
        if error_rate is not None:
            threshold = self.get_threshold(operation, 'error_rate')
            if error_rate > threshold:
                alert = PerformanceAlert(
                    alert_id=str(uuid.uuid4()),
                    operation_name=operation,
                    alert_type='error_rate',
                    severity=self._get_severity(error_rate, threshold),
                    message=f"Operation {operation} has {error_rate:.2%} error rate (threshold: {threshold:.2%})",
                    timestamp=datetime.now(),
                    threshold=threshold,
                    actual_value=error_rate,
                    recommendations=self._get_recommendations('error_rate', operation)
                )
                alerts.append(alert)
        
        # Store alerts
        with self.lock:
            self.alerts.extend(alerts)
        
        return alerts
    
    def get_threshold(self, operation_name: str, metric_type: str) -> float:
        """Get threshold for operation and metric type"""
        return self.thresholds.get(metric_type, {}).get(operation_name, 
               self.thresholds.get(metric_type, {}).get('default', 15.0))
    
    def _get_severity(self, actual: float, threshold: float) -> str:
        """Determine alert severity based on threshold deviation"""
        ratio = actual / threshold
        if ratio >= 3.0:
            return 'critical'
        elif ratio >= 2.0:
            return 'high'
        elif ratio >= 1.5:
            return 'medium'
        else:
            return 'low'
    
    def _get_recommendations(self, alert_type: str, operation: str) -> List[str]:
        """Get recommendations for alert type"""
        recommendations = {
            'timeout': [
                "Consider optimizing database queries",
                "Review network latency and connection pooling",
                "Implement caching for frequently accessed data"
            ],
            'memory': [
                "Review memory allocation patterns",
                "Implement streaming for large datasets",
                "Check for memory leaks in long-running operations"
            ],
            'cpu': [
                "Profile CPU-intensive operations",
                "Consider algorithmic optimizations",
                "Review parallel processing opportunities"
            ],
            'error_rate': [
                "Review error logs for patterns",
                "Implement better error handling",
                "Check external service dependencies"
            ]
        }
        return recommendations.get(alert_type, ["Review operation performance"])
    
    def get_alerts_by_severity(self, severity: str) -> List[PerformanceAlert]:
        """Get alerts by severity level"""
        with self.lock:
            return [alert for alert in self.alerts if alert.severity == severity]
    
    def get_recent_alerts(self, hours: int = 24) -> List[PerformanceAlert]:
        """Get alerts from the last N hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        with self.lock:
            return [alert for alert in self.alerts if alert.timestamp >= cutoff_time]

class PerformanceMonitor:
    """Enhanced main performance monitoring system"""
    
    def __init__(self, config=None):
        """Initialize performance monitor with optional configuration"""
        self.config = config
        self.metrics = MetricsCollector()
        self.alerts = AlertManager()
        self.system_collector = SystemMetricsCollector()
        self.monitoring_enabled = True
        self.sessions: Dict[str, MonitoringSession] = {}
        self.baselines: Dict[str, PerformanceBaseline] = {}
        self._load_baselines()
        
        # Real-time monitoring
        self._monitoring_thread = None
        self._stop_monitoring = threading.Event()
        self._real_time_data = {'metrics': [], 'alerts': [], 'system': {}}
        self._real_time_lock = threading.Lock()
    
    def _load_baselines(self) -> None:
        """Load performance baselines from disk"""
        baselines_file = Path(__file__).parent.parent.parent / "logs" / "performance_baselines.json"
        if baselines_file.exists():
            try:
                with open(baselines_file, 'r') as f:
                    data = json.load(f)
                    for op_type, baseline_data in data.items():
                        baseline_data['created_at'] = datetime.fromisoformat(baseline_data['created_at'])
                        baseline_data['updated_at'] = datetime.fromisoformat(baseline_data['updated_at'])
                        self.baselines[op_type] = PerformanceBaseline(**baseline_data)
                logger.info(f"Loaded {len(self.baselines)} performance baselines")
            except Exception as e:
                logger.warning(f"Failed to load baselines: {e}")
    
    def _save_baselines(self) -> None:
        """Save performance baselines to disk"""
        baselines_file = Path(__file__).parent.parent.parent / "logs" / "performance_baselines.json"
        baselines_file.parent.mkdir(exist_ok=True)
        
        try:
            data = {op_type: baseline.to_dict() for op_type, baseline in self.baselines.items()}
            with open(baselines_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved {len(self.baselines)} performance baselines")
        except Exception as e:
            logger.error(f"Failed to save baselines: {e}")
    
    def start_monitoring_session(self, session_id: Optional[str] = None, operation_type: str = "general") -> MonitoringSession:
        """Start a new monitoring session"""
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        session = MonitoringSession(
            session_id=session_id,
            operation_type=operation_type,
            started_at=datetime.now()
        )
        
        self.sessions[session_id] = session
        logger.info(f"Started monitoring session {session_id} for {operation_type}")
        return session
    
    def end_monitoring_session(self, session_id: str) -> Optional[MonitoringSession]:
        """End a monitoring session"""
        session = self.sessions.get(session_id)
        if session:
            session.ended_at = datetime.now()
            logger.info(f"Ended monitoring session {session_id}, duration: {session.get_duration():.2f}s")
        return session
    
    def record_operation_metrics(self, operation: str, metrics: Dict[str, Any], 
                                session_id: Optional[str] = None) -> None:
        """Record metrics for an operation"""
        if not self.monitoring_enabled:
            return
        
        timestamp = datetime.now()
        
        # Record in traditional metrics collector
        duration = metrics.get('duration', 0.0)
        memory_used = metrics.get('memory_delta', 0.0)
        status = metrics.get('status', 'success')
        cpu_usage_raw = metrics.get('cpu_usage')
        cpu_usage = float(cpu_usage_raw) if cpu_usage_raw is not None and isinstance(cpu_usage_raw, (int, float)) else None
        
        self.metrics.record_operation(
            operation, duration, memory_used, status, metrics, cpu_usage
        )
        
        # Record in session if provided
        if session_id and session_id in self.sessions:
            session = self.sessions[session_id]
            for key, value in metrics.items():
                if isinstance(value, (int, float)):
                    metric = Metric(
                        name=key,
                        value=value,
                        timestamp=timestamp,
                        labels={'operation': operation, 'session': session_id}
                    )
                    session.add_metric(metric)
        
        # Check for alerts
        alerts = self.alerts.send_performance_alert(
            operation=operation,
            duration=duration,
            memory_used=memory_used,
            cpu_usage=cpu_usage
        )
        
        # Update real-time data
        with self._real_time_lock:
            self._real_time_data['alerts'].extend(alerts)
            # Keep only recent data
            cutoff = datetime.now() - timedelta(minutes=30)
            self._real_time_data['alerts'] = [
                a for a in self._real_time_data['alerts'] 
                if a.timestamp >= cutoff
            ]
    
    def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get current real-time metrics"""
        with self._real_time_lock:
            memory_metrics = self.system_collector.get_memory_usage()
            system_metrics = {
                **memory_metrics,  # Unpack memory metrics
                'cpu_percent': self.system_collector.get_cpu_usage(),
                'timestamp': datetime.now().isoformat()
            }
            
            return {
                'system': system_metrics,
                'operations': self.metrics.get_operation_summaries(),
                'recent_alerts': [a.to_dict() for a in self._real_time_data['alerts'][-10:]],
                'active_sessions': len([s for s in self.sessions.values() if s.ended_at is None])
            }
    
    def create_performance_baseline(self, operation_type: str, sample_size: int = 10) -> Optional[PerformanceBaseline]:
        """Create a performance baseline from recent operations"""
        recent_metrics = self.metrics.get_recent_metrics(minutes=60)
        operation_metrics = [m for m in recent_metrics if m.operation_name == operation_type]
        
        if len(operation_metrics) < sample_size:
            logger.warning(f"Insufficient samples for baseline: {len(operation_metrics)} < {sample_size}")
            return None
        
        # Calculate baseline statistics
        durations = [m.duration for m in operation_metrics]
        memories = [m.memory_used for m in operation_metrics]
        success_count = sum(1 for m in operation_metrics if m.status == 'success')
        
        baseline = PerformanceBaseline(
            operation_type=operation_type,
            avg_duration=sum(durations) / len(durations),
            avg_memory_mb=sum(memories) / len(memories),
            avg_cpu_percent=0.0,  # Will be updated with CPU data
            avg_records_per_second=len(operation_metrics) / sum(durations),
            success_rate_threshold=success_count / len(operation_metrics),
            p95_duration=self.metrics._calculate_percentile(durations, 95),
            p99_duration=self.metrics._calculate_percentile(durations, 99),
            created_from_samples=len(operation_metrics),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.baselines[operation_type] = baseline
        self._save_baselines()
        logger.info(f"Created baseline for {operation_type} from {sample_size} samples")
        return baseline
    
    def get_performance_baseline(self, operation_type: str) -> Optional[PerformanceBaseline]:
        """Get performance baseline for operation type"""
        return self.baselines.get(operation_type)
    
    def validate_performance_against_baseline(self, current: Dict, baseline: PerformanceBaseline) -> ValidationResult:
        """Validate current performance against baseline"""
        violations = []
        warnings = []
        
        # Check duration
        current_duration = current.get('avg_duration', 0.0)
        if current_duration > baseline.avg_duration * 1.2:  # 20% degradation
            violations.append(f"Duration degraded: {current_duration:.2f}s vs baseline {baseline.avg_duration:.2f}s")
        elif current_duration > baseline.avg_duration * 1.1:  # 10% degradation
            warnings.append(f"Duration slightly increased: {current_duration:.2f}s vs baseline {baseline.avg_duration:.2f}s")
        
        # Check memory
        current_memory = current.get('avg_memory', 0.0)
        if current_memory > baseline.avg_memory_mb * 1.5:  # 50% increase
            violations.append(f"Memory usage increased: {current_memory:.2f}MB vs baseline {baseline.avg_memory_mb:.2f}MB")
        
        # Check success rate
        current_success_rate = current.get('success_rate', 1.0)
        if current_success_rate < baseline.success_rate_threshold:
            violations.append(f"Success rate below threshold: {current_success_rate:.2%} vs {baseline.success_rate_threshold:.2%}")
        
        # Calculate improvement percentage
        improvement = None
        if current_duration > 0 and baseline.avg_duration > 0:
            improvement = ((baseline.avg_duration - current_duration) / baseline.avg_duration) * 100
        
        result = ValidationResult(
            operation_type=baseline.operation_type,
            baseline=baseline,
            current_metrics=current,
            passed=len(violations) == 0,
            violations=violations,
            warnings=warnings,
            improvement_percentage=improvement
        )
        
        return result
    
    def export_metrics(self, format: str = "json", hours: int = 24) -> str:
        """Export metrics in specified format"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        logs_dir = Path(__file__).parent.parent.parent / "logs"
        logs_dir.mkdir(exist_ok=True)
        
        # Get data to export
        recent_metrics = self.metrics.get_recent_metrics(minutes=hours * 60)
        operations_summary = self.metrics.get_operation_summaries()
        recent_alerts = self.alerts.get_recent_alerts(hours=hours)
        
        if format.lower() == "json":
            filename = f"performance_metrics_{timestamp}.json"
            filepath = logs_dir / filename
            
            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                'time_range_hours': hours,
                'metrics': [m.to_dict() for m in recent_metrics],
                'operations_summary': operations_summary,
                'alerts': [a.to_dict() for a in recent_alerts],
                'baselines': {op: baseline.to_dict() for op, baseline in self.baselines.items()}
            }
            
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2)
        
        elif format.lower() == "csv":
            filename = f"performance_metrics_{timestamp}.csv"
            filepath = logs_dir / filename
            
            with open(filepath, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'operation', 'duration', 'memory_mb', 'status'])
                for metric in recent_metrics:
                    writer.writerow([
                        metric.timestamp.isoformat(),
                        metric.operation_name,
                        metric.duration,
                        metric.memory_used,
                        metric.status
                    ])
        
        logger.info(f"Exported metrics to {filepath}")
        return str(filepath)
    
    @contextmanager
    def monitor_operation(self, operation_name: str, session_id: Optional[str] = None):
        """Context manager for monitoring operations"""
        start_time = time.time()
        start_memory = self.system_collector.get_memory_usage()['rss_mb']
        start_cpu = self.system_collector.get_cpu_usage()
        
        try:
            yield
            status = 'success'
        except Exception as e:
            status = 'error'
            raise
        finally:
            if self.monitoring_enabled:
                elapsed = time.time() - start_time
                end_memory = self.system_collector.get_memory_usage()['rss_mb']
                end_cpu = self.system_collector.get_cpu_usage()
                
                metrics = {
                    'duration': elapsed,
                    'memory_delta': end_memory - start_memory,
                    'cpu_usage': (start_cpu + end_cpu) / 2,
                    'status': status,
                    'operation': operation_name
                }
                
                self.record_operation_metrics(operation_name, metrics, session_id)
    
    def track_operation(self, operation_name: str):
        """Decorator to track operation performance"""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                if not self.monitoring_enabled:
                    return func(*args, **kwargs)
                
                with self.monitor_operation(operation_name):
                    return func(*args, **kwargs)
            
            return wrapper
        return decorator
    
    def generate_performance_report(self, hours: int = 24) -> PerformanceReport:
        """Generate comprehensive performance report"""
        time_range = timedelta(hours=hours)
        recent_metrics = self.metrics.get_recent_metrics(minutes=hours * 60)
        recent_alerts = self.alerts.get_recent_alerts(hours=hours)
        operations_summary = self.metrics.get_operation_summaries()
        
        # Calculate trends
        performance_trends = {}
        for op_name in operations_summary.keys():
            op_metrics = [m for m in recent_metrics if m.operation_name == op_name]
            if op_metrics:
                # Group by hour and calculate averages
                hourly_durations = defaultdict(list)
                for metric in op_metrics:
                    hour = metric.timestamp.replace(minute=0, second=0, microsecond=0)
                    hourly_durations[hour].append(metric.duration)
                
                performance_trends[op_name] = [
                    sum(durations) / len(durations) 
                    for durations in hourly_durations.values()
                ]
        
        # Generate recommendations
        recommendations = self._generate_optimization_recommendations(
            operations_summary, recent_alerts,
            sum(m.duration for m in recent_metrics) / len(recent_metrics) if recent_metrics else 0,
            sum(m.memory_used for m in recent_metrics) / len(recent_metrics) if recent_metrics else 0
        )
        
        report = PerformanceReport(
            report_id=str(uuid.uuid4()),
            generated_at=datetime.now(),
            time_range_hours=hours,
            total_operations=len(recent_metrics),
            total_errors=len([m for m in recent_metrics if m.status != 'success']),
            average_duration=sum(m.duration for m in recent_metrics) / len(recent_metrics) if recent_metrics else 0,
            average_memory=sum(m.memory_used for m in recent_metrics) / len(recent_metrics) if recent_metrics else 0,
            operations_summary=operations_summary,
            performance_trends=performance_trends,
            recent_alerts=recent_alerts,
            recommendations=recommendations
        )
        
        return report
    
    def _generate_optimization_recommendations(self, operations_summary: Dict[str, Dict[str, Any]], 
                                             recent_alerts: List[PerformanceAlert],
                                             average_duration: float,
                                             average_memory: float) -> List[str]:
        """Generate optimization recommendations based on performance data"""
        recommendations = []
        
        # Check for slow operations
        for op_name, summary in operations_summary.items():
            if summary.get('avg_duration', 0) > 10.0:
                recommendations.append(f"Optimize {op_name}: average duration {summary['avg_duration']:.2f}s is high")
            
            if summary.get('success_rate', 1.0) < 0.95:
                recommendations.append(f"Improve reliability of {op_name}: success rate {summary['success_rate']:.2%}")
        
        # Check memory usage
        if average_memory > 1000:  # 1GB
            recommendations.append("Consider implementing streaming for large datasets to reduce memory usage")
        
        # Check alert patterns
        timeout_alerts = [a for a in recent_alerts if a.alert_type == 'timeout']
        if len(timeout_alerts) > 5:
            recommendations.append("Multiple timeout alerts detected - review database query performance")
        
        memory_alerts = [a for a in recent_alerts if a.alert_type == 'memory']
        if len(memory_alerts) > 3:
            recommendations.append("Memory usage alerts detected - implement memory optimization")
        
        if len(recent_alerts) > 10:
            recommendations.append("Review and adjust performance thresholds")
        
        return recommendations
    
    def save_report(self, report: PerformanceReport, filename: Optional[str] = None) -> str:
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

class RealTimeMonitor:
    """Real-time monitoring display system"""
    
    def __init__(self, monitor: PerformanceMonitor):
        self.monitor = monitor
        self.console = Console() if RICH_AVAILABLE else None
        
    def display_live_metrics(self, duration: int = 60, interval: int = 5):
        """Display live metrics with console updates"""
        if not RICH_AVAILABLE:
            self._display_simple_metrics(duration, interval)
            return
        
        def generate_table():
            table = Table(title="Performance Monitoring - Live Metrics")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="magenta")
            table.add_column("Status", style="green")
            
            metrics = self.monitor.get_real_time_metrics()
            system = metrics.get('system', {})
            
            table.add_row("CPU Usage", f"{system.get('cpu_percent', 0):.1f}%", 
                         "⚠️" if system.get('cpu_percent', 0) > 80 else "✅")
            table.add_row("Memory Usage", f"{system.get('rss_mb', 0):.1f} MB", 
                         "⚠️" if system.get('rss_mb', 0) > 1000 else "✅")
            table.add_row("Active Sessions", str(metrics.get('active_sessions', 0)), "✅")
            table.add_row("Recent Alerts", str(len(metrics.get('recent_alerts', []))), 
                         "⚠️" if len(metrics.get('recent_alerts', [])) > 0 else "✅")
            
            return table
        
        with Live(generate_table(), refresh_per_second=1/interval) as live:
            start_time = time.time()
            while time.time() - start_time < duration:
                time.sleep(interval)
                live.update(generate_table())
    
    def _display_simple_metrics(self, duration: int, interval: int):
        """Simple metrics display without rich library"""
        start_time = time.time()
        while time.time() - start_time < duration:
            metrics = self.monitor.get_real_time_metrics()
            system = metrics.get('system', {})
            
            print(f"\n--- Performance Metrics ({datetime.now().strftime('%H:%M:%S')}) ---")
            print(f"CPU Usage: {system.get('cpu_percent', 0):.1f}%")
            print(f"Memory Usage: {system.get('rss_mb', 0):.1f} MB")
            print(f"Active Sessions: {metrics.get('active_sessions', 0)}")
            print(f"Recent Alerts: {len(metrics.get('recent_alerts', []))}")
            
            time.sleep(interval)
    
    def generate_performance_alerts(self, current: Dict, baseline: PerformanceBaseline):
        """Generate alerts for performance degradation"""
        validation = self.monitor.validate_performance_against_baseline(current, baseline)
        
        if not validation.passed:
            print("\n🚨 PERFORMANCE ALERTS:")
            for violation in validation.violations:
                print(f"  ❌ {violation}")
        
        if validation.warnings:
            print("\n⚠️ PERFORMANCE WARNINGS:")
            for warning in validation.warnings:
                print(f"  ⚠️ {warning}")
        
        if validation.improvement_percentage and validation.improvement_percentage > 0:
            print(f"\n✅ PERFORMANCE IMPROVEMENT: {validation.improvement_percentage:.1f}% faster") 