# -*- coding: utf-8 -*-
"""
Performance Monitoring and Diagnostics
Comprehensive performance monitoring, profiling, and diagnostic tools
"""

import time
import threading
import json
import statistics
from typing import Dict, List, Any, Optional, Callable, Union
from collections import deque, defaultdict
from dataclasses import dataclass, asdict
from enum import Enum
import psutil
import traceback

class MetricType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"

class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class PerformanceMetric:
    """Single performance metric"""
    name: str
    value: Union[int, float]
    metric_type: MetricType
    timestamp: float
    tags: Dict[str, str] = None
    unit: str = ""

@dataclass
class PerformanceAlert:
    """Performance alert"""
    level: AlertLevel
    message: str
    metric_name: str
    value: float
    threshold: float
    timestamp: float
    tags: Dict[str, str] = None

@dataclass
class FunctionProfile:
    """Function profiling data"""
    function_name: str
    call_count: int
    total_time: float
    avg_time: float
    min_time: float
    max_time: float
    last_call: float

class PerformanceMonitor:
    """
    Comprehensive performance monitoring system
    """
    
    def __init__(self, max_history: int = 1000, alert_thresholds: Dict[str, Dict[str, float]] = None):
        self.max_history = max_history
        self.alert_thresholds = alert_thresholds or {
            'memory_usage_mb': {'warning': 1024, 'critical': 2048},
            'cpu_usage_percent': {'warning': 80, 'critical': 95},
            'frame_time_ms': {'warning': 16.67, 'critical': 33.33},
            'response_time_ms': {'warning': 1000, 'critical': 5000}
        }
        
        # Metrics storage
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_history))
        self.counters: Dict[str, int] = defaultdict(int)
        self.gauges: Dict[str, float] = defaultdict(float)
        self.histograms: Dict[str, List[float]] = defaultdict(list)
        self.timers: Dict[str, List[float]] = defaultdict(list)
        
        # Alerts
        self.alerts: List[PerformanceAlert] = []
        self.alert_callbacks: List[Callable[[PerformanceAlert], None]] = []
        
        # Function profiling
        self.function_profiles: Dict[str, FunctionProfile] = {}
        self.profiling_enabled = False
        
        # System monitoring
        self.process = psutil.Process()
        self.system_monitoring = True
        
        # History tracking
        self.metric_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_history))
        self.performance_summary: Dict[str, Any] = {}
        
        # Threading
        self.monitoring_active = False
        self.monitor_thread = None
        self.monitoring_interval = 1.0
        
        # Performance baselines
        self.baseline_metrics: Dict[str, float] = {}
        
        # Start monitoring
        self.start_monitoring()
    
    def start_monitoring(self):
        """Start background monitoring"""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
    
    def _monitor_loop(self):
        """Background monitoring loop"""
        while self.monitoring_active:
            try:
                self._collect_system_metrics()
                self._check_alerts()
                self._update_performance_summary()
                time.sleep(self.monitoring_interval)
            except Exception as e:
                print(f"Monitoring error: {e}")
    
    def _collect_system_metrics(self):
        """Collect system performance metrics"""
        current_time = time.time()
        
        # Memory metrics
        memory_info = self.process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024
        self.record_gauge('memory_usage_mb', memory_mb)
        
        # CPU metrics
        cpu_percent = self.process.cpu_percent()
        self.record_gauge('cpu_usage_percent', cpu_percent)
        
        # Thread count
        thread_count = self.process.num_threads()
        self.record_gauge('thread_count', thread_count)
        
        # File descriptors
        try:
            fd_count = self.process.num_fds()
            self.record_gauge('fd_count', fd_count)
        except (AttributeError, psutil.AccessDenied):
            pass
        
        # System-wide metrics
        system_cpu = psutil.cpu_percent(interval=None)
        self.record_gauge('system_cpu_percent', system_cpu)
        
        system_memory = psutil.virtual_memory()
        self.record_gauge('system_memory_percent', system_memory.percent)
    
    def record_counter(self, name: str, value: int = 1, tags: Dict[str, str] = None):
        """Record counter metric"""
        self.counters[name] += value
        metric = PerformanceMetric(
            name=name,
            value=self.counters[name],
            metric_type=MetricType.COUNTER,
            timestamp=time.time(),
            tags=tags or {}
        )
        self._store_metric(name, metric)
    
    def record_gauge(self, name: str, value: float, tags: Dict[str, str] = None):
        """Record gauge metric"""
        self.gauges[name] = value
        metric = PerformanceMetric(
            name=name,
            value=value,
            metric_type=MetricType.GAUGE,
            timestamp=time.time(),
            tags=tags or {}
        )
        self._store_metric(name, metric)
    
    def record_histogram(self, name: str, value: float, tags: Dict[str, str] = None):
        """Record histogram metric"""
        self.histograms[name].append(value)
        if len(self.histograms[name]) > 1000:  # Keep histogram manageable
            self.histograms[name] = self.histograms[name][-1000:]
        
        metric = PerformanceMetric(
            name=name,
            value=value,
            metric_type=MetricType.HISTOGRAM,
            timestamp=time.time(),
            tags=tags or {}
        )
        self._store_metric(name, metric)
    
    def record_timer(self, name: str, duration: float, tags: Dict[str, str] = None):
        """Record timer metric"""
        self.timers[name].append(duration)
        if len(self.timers[name]) > 1000:
            self.timers[name] = self.timers[name][-1000:]
        
        metric = PerformanceMetric(
            name=name,
            value=duration,
            metric_type=MetricType.TIMER,
            timestamp=time.time(),
            tags=tags or {}
        )
        self._store_metric(name, metric)
    
    def _store_metric(self, name: str, metric: PerformanceMetric):
        """Store metric in history"""
        self.metrics[name].append(metric)
        self.metric_history[name].append(metric)
    
    def _check_alerts(self):
        """Check for performance alerts"""
        current_time = time.time()
        
        for metric_name, thresholds in self.alert_thresholds.items():
            current_value = self.gauges.get(metric_name)
            if current_value is None:
                continue
            
            # Check critical threshold
            if current_value >= thresholds.get('critical', float('inf')):
                self._create_alert(
                    AlertLevel.CRITICAL,
                    f"Critical: {metric_name} = {current_value:.2f}",
                    metric_name,
                    current_value,
                    thresholds['critical'],
                    current_time
                )
            
            # Check warning threshold
            elif current_value >= thresholds.get('warning', float('inf')):
                self._create_alert(
                    AlertLevel.WARNING,
                    f"Warning: {metric_name} = {current_value:.2f}",
                    metric_name,
                    current_value,
                    thresholds['warning'],
                    current_time
                )
    
    def _create_alert(self, level: AlertLevel, message: str, metric_name: str,
                     value: float, threshold: float, timestamp: float):
        """Create performance alert"""
        alert = PerformanceAlert(
            level=level,
            message=message,
            metric_name=metric_name,
            value=value,
            threshold=threshold,
            timestamp=timestamp
        )
        
        # Store alert
        self.alerts.append(alert)
        
        # Keep only recent alerts
        if len(self.alerts) > 1000:
            self.alerts = self.alerts[-1000:]
        
        # Notify callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                print(f"Alert callback error: {e}")
    
    def _update_performance_summary(self):
        """Update performance summary statistics"""
        summary = {
            'timestamp': time.time(),
            'metrics': {},
            'alerts_count': {
                'critical': len([a for a in self.alerts if a.level == AlertLevel.CRITICAL]),
                'error': len([a for a in self.alerts if a.level == AlertLevel.ERROR]),
                'warning': len([a for a in self.alerts if a.level == AlertLevel.WARNING]),
                'info': len([a for a in self.alerts if a.level == AlertLevel.INFO])
            }
        }
        
        # Add metric summaries
        for name, metric_list in self.metrics.items():
            if not metric_list:
                continue
            
            recent_metrics = list(metric_list)[-100:]  # Last 100 metrics
            values = [m.value for m in recent_metrics]
            
            summary['metrics'][name] = {
                'count': len(values),
                'current': values[-1] if values else 0,
                'min': min(values),
                'max': max(values),
                'avg': statistics.mean(values),
                'median': statistics.median(values),
                'std_dev': statistics.stdev(values) if len(values) > 1 else 0
            }
        
        self.performance_summary = summary
    
    def start_function_profiling(self):
        """Enable function profiling"""
        self.profiling_enabled = True
    
    def stop_function_profiling(self):
        """Disable function profiling"""
        self.profiling_enabled = False
    
    def profile_function(self, func_name: str, duration: float):
        """Record function execution time"""
        if not self.profiling_enabled:
            return
        
        if func_name not in self.function_profiles:
            self.function_profiles[func_name] = FunctionProfile(
                function_name=func_name,
                call_count=0,
                total_time=0.0,
                avg_time=0.0,
                min_time=duration,
                max_time=duration,
                last_call=0.0
            )
        
        profile = self.function_profiles[func_name]
        profile.call_count += 1
        profile.total_time += duration
        profile.avg_time = profile.total_time / profile.call_count
        profile.min_time = min(profile.min_time, duration)
        profile.max_time = max(profile.max_time, duration)
        profile.last_call = time.time()
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        return {
            'summary': self.performance_summary,
            'counters': dict(self.counters),
            'gauges': dict(self.gauges),
            'function_profiles': {name: asdict(profile) for name, profile in self.function_profiles.items()},
            'alert_count': len(self.alerts),
            'recent_alerts': [asdict(alert) for alert in self.alerts[-10:]],
            'system_info': self._get_system_info()
        }
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        try:
            return {
                'cpu_count': psutil.cpu_count(),
                'memory_total_gb': psutil.virtual_memory().total / 1024 / 1024 / 1024,
                'disk_usage': {
                    'total_gb': psutil.disk_usage('/').total / 1024 / 1024 / 1024,
                    'free_gb': psutil.disk_usage('/').free / 1024 / 1024 / 1024
                },
                'boot_time': psutil.boot_time()
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_metric_history(self, metric_name: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get metric history"""
        if metric_name not in self.metric_history:
            return []
        
        history = list(self.metric_history[metric_name])[-limit:]
        return [
            {
                'timestamp': m.timestamp,
                'value': m.value,
                'type': m.metric_type.value,
                'tags': m.tags or {}
            }
            for m in history
        ]
    
    def add_alert_callback(self, callback: Callable[[PerformanceAlert], None]):
        """Add alert callback"""
        self.alert_callbacks.append(callback)
    
    def remove_alert_callback(self, callback: Callable[[PerformanceAlert], None]):
        """Remove alert callback"""
        if callback in self.alert_callbacks:
            self.alert_callbacks.remove(callback)
    
    def set_baseline(self, metric_name: str, value: float):
        """Set performance baseline"""
        self.baseline_metrics[metric_name] = value
    
    def compare_to_baseline(self) -> Dict[str, Dict[str, float]]:
        """Compare current metrics to baseline"""
        comparison = {}
        
        for metric_name, baseline_value in self.baseline_metrics.items():
            current_value = self.gauges.get(metric_name)
            if current_value is not None:
                comparison[metric_name] = {
                    'baseline': baseline_value,
                    'current': current_value,
                    'difference': current_value - baseline_value,
                    'percent_change': ((current_value - baseline_value) / baseline_value) * 100
                }
        
        return comparison
    
    def export_metrics(self, filename: str, format: str = 'json'):
        """Export metrics to file"""
        data = {
            'timestamp': time.time(),
            'stats': self.get_performance_stats(),
            'metrics': {
                name: [
                    {
                        'timestamp': m.timestamp,
                        'value': m.value,
                        'type': m.metric_type.value,
                        'tags': m.tags
                    }
                    for m in metric_list
                ]
                for name, metric_list in self.metrics.items()
            }
        }
        
        if format == 'json':
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def clear_metrics(self):
        """Clear all metrics"""
        self.metrics.clear()
        self.counters.clear()
        self.gauges.clear()
        self.histograms.clear()
        self.timers.clear()
        self.alerts.clear()
        self.function_profiles.clear()
        self.metric_history.clear()
    
    def cleanup(self):
        """Cleanup performance monitor"""
        self.stop_monitoring()
        self.clear_metrics()

class PerformanceProfiler:
    """Function performance profiler"""
    
    def __init__(self, monitor: PerformanceMonitor):
        self.monitor = monitor
    
    def __call__(self, func_name: str = None):
        """Decorator for profiling functions"""
        def decorator(func):
            name = func_name or f"{func.__module__}.{func.__name__}"
            
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    duration = time.time() - start_time
                    self.monitor.profile_function(name, duration)
                    self.monitor.record_timer(f"function_duration_{name}", duration)
            
            return wrapper
        return decorator
    
    def profile_context(self, name: str):
        """Context manager for profiling code blocks"""
        return ProfileContext(self.monitor, name)

class ProfileContext:
    """Context manager for profiling"""
    
    def __init__(self, monitor: PerformanceMonitor, name: str):
        self.monitor = monitor
        self.name = name
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = time.time() - self.start_time
            self.monitor.profile_function(self.name, duration)
            self.monitor.record_timer(f"block_duration_{self.name}", duration)

# Global performance monitor instance
_performance_monitor = None

def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance"""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor

def cleanup_performance_monitor():
    """Cleanup global performance monitor"""
    global _performance_monitor
    if _performance_monitor:
        _performance_monitor.cleanup()
        _performance_monitor = None

# Decorator for easy profiling
def profile_performance(name: str = None):
    """Decorator for profiling function performance"""
    monitor = get_performance_monitor()
    profiler = PerformanceProfiler(monitor)
    return profiler(name)

# Context manager for profiling
profile_block = lambda name: ProfileContext(get_performance_monitor(), name)