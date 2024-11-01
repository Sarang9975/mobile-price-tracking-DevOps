"""
Monitoring module for application metrics and health checks.
"""

import time
import psutil
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
from collections import deque
import threading
import json

logger = logging.getLogger(__name__)

@dataclass
class SystemMetrics:
    """System resource metrics."""
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_total_mb: float
    disk_usage_percent: float
    network_io: Dict[str, float]
    timestamp: datetime

@dataclass
class ApplicationMetrics:
    """Application-specific metrics."""
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time: float
    cache_hit_rate: float
    active_connections: int
    timestamp: datetime

class MetricsCollector:
    """Collects and stores application and system metrics."""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.system_metrics = deque(maxlen=max_history)
        self.application_metrics = deque(maxlen=max_history)
        self.request_times = deque(maxlen=max_history)
        self.error_log = deque(maxlen=max_history)
        
        # Start background collection
        self.running = False
        self.collection_thread = None
        self.start_collection()
    
    def start_collection(self):
        """Start background metrics collection."""
        if not self.running:
            self.running = True
            self.collection_thread = threading.Thread(target=self._collect_metrics_loop, daemon=True)
            self.collection_thread.start()
            logger.info("Metrics collection started")
    
    def stop_collection(self):
        """Stop background metrics collection."""
        self.running = False
        if self.collection_thread:
            self.collection_thread.join()
            logger.info("Metrics collection stopped")
    
    def _collect_metrics_loop(self):
        """Background loop for collecting metrics."""
        while self.running:
            try:
                self.collect_system_metrics()
                time.sleep(30)  # Collect every 30 seconds
            except Exception as e:
                logger.error(f"Error in metrics collection loop: {e}")
                time.sleep(60)  # Wait longer on error
    
    def collect_system_metrics(self):
        """Collect current system metrics."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_mb = memory.used / (1024 * 1024)
            memory_total_mb = memory.total / (1024 * 1024)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_usage_percent = disk.percent
            
            # Network I/O
            network = psutil.net_io_counters()
            network_io = {
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv,
                'packets_sent': network.packets_sent,
                'packets_recv': network.packets_recv
            }
            
            metrics = SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_used_mb=memory_used_mb,
                memory_total_mb=memory_total_mb,
                disk_usage_percent=disk_usage_percent,
                network_io=network_io,
                timestamp=datetime.now()
            )
            
            self.system_metrics.append(metrics)
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
    
    def record_request(self, response_time: float, success: bool):
        """Record a request metric."""
        self.request_times.append(response_time)
        
        # Update application metrics
        if len(self.application_metrics) > 0:
            last_metrics = self.application_metrics[-1]
            total_requests = last_metrics.total_requests + 1
            successful_requests = last_metrics.successful_requests + (1 if success else 0)
            failed_requests = last_metrics.failed_requests + (0 if success else 1)
        else:
            total_requests = 1
            successful_requests = 1 if success else 0
            failed_requests = 0 if success else 1
        
        # Calculate average response time
        if self.request_times:
            avg_response_time = sum(self.request_times) / len(self.request_times)
        else:
            avg_response_time = 0.0
        
        metrics = ApplicationMetrics(
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            average_response_time=avg_response_time,
            cache_hit_rate=0.0,  # Will be updated by cache module
            active_connections=0,  # Will be updated by connection tracking
            timestamp=datetime.now()
        )
        
        self.application_metrics.append(metrics)
    
    def record_error(self, error_type: str, error_message: str, stack_trace: str = None):
        """Record an error for monitoring."""
        error_entry = {
            'type': error_type,
            'message': error_message,
            'stack_trace': stack_trace,
            'timestamp': datetime.now().isoformat()
        }
        self.error_log.append(error_entry)
        logger.error(f"Error recorded: {error_type} - {error_message}")
    
    def get_current_metrics(self) -> Dict:
        """Get current metrics summary."""
        try:
            # Get latest system metrics
            system_metrics = self.system_metrics[-1] if self.system_metrics else None
            
            # Get latest application metrics
            app_metrics = self.application_metrics[-1] if self.application_metrics else None
            
            # Calculate trends
            system_trend = self._calculate_system_trend()
            app_trend = self._calculate_app_trend()
            
            return {
                'system': {
                    'current': {
                        'cpu_percent': system_metrics.cpu_percent if system_metrics else 0,
                        'memory_percent': system_metrics.memory_percent if system_metrics else 0,
                        'memory_used_mb': round(system_metrics.memory_used_mb, 2) if system_metrics else 0,
                        'memory_total_mb': round(system_metrics.memory_total_mb, 2) if system_metrics else 0,
                        'disk_usage_percent': system_metrics.disk_usage_percent if system_metrics else 0
                    },
                    'trend': system_trend
                },
                'application': {
                    'current': {
                        'total_requests': app_metrics.total_requests if app_metrics else 0,
                        'successful_requests': app_metrics.successful_requests if app_metrics else 0,
                        'failed_requests': app_metrics.failed_requests if app_metrics else 0,
                        'average_response_time': round(app_metrics.average_response_time, 2) if app_metrics else 0,
                        'cache_hit_rate': app_metrics.cache_hit_rate if app_metrics else 0
                    },
                    'trend': app_trend
                },
                'errors': {
                    'total_errors': len(self.error_log),
                    'recent_errors': list(self.error_log)[-10:]  # Last 10 errors
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get current metrics: {e}")
            return {}
    
    def _calculate_system_trend(self) -> Dict:
        """Calculate system metrics trend over the last hour."""
        try:
            one_hour_ago = datetime.now() - timedelta(hours=1)
            recent_metrics = [
                m for m in self.system_metrics 
                if m.timestamp > one_hour_ago
            ]
            
            if len(recent_metrics) < 2:
                return {'cpu': 'stable', 'memory': 'stable', 'disk': 'stable'}
            
            # Calculate trends
            cpu_values = [m.cpu_percent for m in recent_metrics]
            memory_values = [m.memory_percent for m in recent_metrics]
            disk_values = [m.disk_usage_percent for m in recent_metrics]
            
            def get_trend(values):
                if len(values) < 2:
                    return 'stable'
                slope = (values[-1] - values[0]) / len(values)
                if slope > 1:
                    return 'increasing'
                elif slope < -1:
                    return 'decreasing'
                else:
                    return 'stable'
            
            return {
                'cpu': get_trend(cpu_values),
                'memory': get_trend(memory_values),
                'disk': get_trend(disk_values)
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate system trend: {e}")
            return {'cpu': 'stable', 'memory': 'stable', 'disk': 'stable'}
    
    def _calculate_app_trend(self) -> Dict:
        """Calculate application metrics trend over the last hour."""
        try:
            one_hour_ago = datetime.now() - timedelta(hours=1)
            recent_metrics = [
                m for m in self.application_metrics 
                if m.timestamp > one_hour_ago
            ]
            
            if len(recent_metrics) < 2:
                return {'requests': 'stable', 'response_time': 'stable', 'errors': 'stable'}
            
            # Calculate trends
            request_values = [m.total_requests for m in recent_metrics]
            response_values = [m.average_response_time for m in recent_metrics]
            error_values = [m.failed_requests for m in recent_metrics]
            
            def get_trend(values):
                if len(values) < 2:
                    return 'stable'
                slope = (values[-1] - values[0]) / len(values)
                if slope > 0.1:
                    return 'increasing'
                elif slope < -0.1:
                    return 'decreasing'
                else:
                    return 'stable'
            
            return {
                'requests': get_trend(request_values),
                'response_time': get_trend(response_values),
                'errors': get_trend(error_values)
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate app trend: {e}")
            return {'requests': 'stable', 'response_time': 'stable', 'errors': 'stable'}
    
    def get_metrics_history(self, hours: int = 24) -> Dict:
        """Get metrics history for the specified number of hours."""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            system_history = [
                {
                    'timestamp': m.timestamp.isoformat(),
                    'cpu_percent': m.cpu_percent,
                    'memory_percent': m.memory_percent,
                    'disk_usage_percent': m.disk_usage_percent
                }
                for m in self.system_metrics
                if m.timestamp > cutoff_time
            ]
            
            app_history = [
                {
                    'timestamp': m.timestamp.isoformat(),
                    'total_requests': m.total_requests,
                    'successful_requests': m.successful_requests,
                    'failed_requests': m.failed_requests,
                    'average_response_time': m.average_response_time
                }
                for m in self.application_metrics
                if m.timestamp > cutoff_time
            ]
            
            return {
                'system': system_history,
                'application': app_history,
                'hours': hours
            }
            
        except Exception as e:
            logger.error(f"Failed to get metrics history: {e}")
            return {'system': [], 'application': [], 'hours': hours}
    
    def export_metrics(self, filepath: str):
        """Export metrics to a JSON file."""
        try:
            metrics_data = {
                'system_metrics': [
                    {
                        'timestamp': m.timestamp.isoformat(),
                        'cpu_percent': m.cpu_percent,
                        'memory_percent': m.memory_percent,
                        'memory_used_mb': m.memory_used_mb,
                        'memory_total_mb': m.memory_total_mb,
                        'disk_usage_percent': m.disk_usage_percent,
                        'network_io': m.network_io
                    }
                    for m in self.system_metrics
                ],
                'application_metrics': [
                    {
                        'timestamp': m.timestamp.isoformat(),
                        'total_requests': m.total_requests,
                        'successful_requests': m.successful_requests,
                        'failed_requests': m.failed_requests,
                        'average_response_time': m.average_response_time,
                        'cache_hit_rate': m.cache_hit_rate,
                        'active_connections': m.active_connections
                    }
                    for m in self.application_metrics
                ],
                'error_log': list(self.error_log),
                'export_timestamp': datetime.now().isoformat()
            }
            
            with open(filepath, 'w') as f:
                json.dump(metrics_data, f, indent=2)
            
            logger.info(f"Metrics exported to {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to export metrics: {e}")

# Global metrics collector instance
metrics_collector = MetricsCollector() 