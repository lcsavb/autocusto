"""
System Health Monitoring Utilities

This module provides functions to collect and log real system health metrics
for the AutoCusto application, focusing on critical performance indicators
for a Django application handling PDF generation and medical data.
"""

import time
import psutil
import os
from decimal import Decimal
from django.db import connection
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from analytics.models import SystemHealthLog, PDFGenerationLog
from processos.models import Processo
from pacientes.models import Paciente


User = get_user_model()


def log_system_health_metric(metric_type, value, unit, details=None):
    """
    Log a system health metric to the database
    
    Args:
        metric_type: One of the choices from SystemHealthLog.metric_type
        value: Numeric value of the metric
        unit: Unit of measurement (ms, MB, %, etc.)
        details: Optional JSON details about the metric
    """
    try:
        SystemHealthLog.objects.create(
            metric_type=metric_type,
            value=Decimal(str(value)),
            unit=unit,
            details=details or {}
        )
    except Exception as e:
        # Don't let health logging break the application
        print(f"Warning: Failed to log system health metric {metric_type}: {e}")


def measure_database_performance():
    """
    Measure database query performance by timing a simple query
    
    Returns:
        float: Query time in milliseconds
    """
    start_time = time.time()
    
    try:
        # Execute a simple query to measure DB performance
        # Use a table that definitely exists in AutoCusto
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM usuarios_usuario")
            result = cursor.fetchone()
        
        end_time = time.time()
        query_time_ms = (end_time - start_time) * 1000
        
        # Log the metric
        log_system_health_metric(
            metric_type='database_query',
            value=round(query_time_ms, 2),
            unit='ms',
            details={
                'query': 'SELECT COUNT(*) FROM usuarios_usuario',
                'result_count': result[0] if result else 0,
                'timestamp': timezone.now().isoformat()
            }
        )
        
        return query_time_ms
        
    except Exception as e:
        # Log error but return a default high value
        log_system_health_metric(
            metric_type='database_query',
            value=9999,
            unit='ms',
            details={
                'error': str(e),
                'timestamp': timezone.now().isoformat()
            }
        )
        return 9999


def measure_pdf_memory_usage():
    """
    Measure memory usage of the PDF generation directory (/dev/shm)
    
    Returns:
        float: Memory usage in MB
    """
    try:
        # Check /dev/shm usage (AutoCusto stores PDF templates in memory)
        shm_path = '/dev/shm'
        if os.path.exists(shm_path):
            # Get disk usage of /dev/shm
            shm_usage = psutil.disk_usage(shm_path)
            used_mb = shm_usage.used / (1024 * 1024)  # Convert to MB
            total_mb = shm_usage.total / (1024 * 1024)
            percent_used = (used_mb / total_mb) * 100
        else:
            # Fallback to general memory usage
            memory = psutil.virtual_memory()
            used_mb = memory.used / (1024 * 1024)
            percent_used = memory.percent
        
        # Log the metric
        log_system_health_metric(
            metric_type='pdf_memory',
            value=round(used_mb, 2),
            unit='MB',
            details={
                'percent_used': round(percent_used, 2),
                'path_checked': shm_path if os.path.exists(shm_path) else 'system_memory',
                'timestamp': timezone.now().isoformat()
            }
        )
        
        return used_mb
        
    except Exception as e:
        log_system_health_metric(
            metric_type='pdf_memory',
            value=0,
            unit='MB',
            details={
                'error': str(e),
                'timestamp': timezone.now().isoformat()
            }
        )
        return 0


def measure_api_response_time():
    """
    Measure API response time by timing a simple view operation
    
    Returns:
        float: Response time in milliseconds
    """
    start_time = time.time()
    
    try:
        # Simulate an API operation by counting recent processes
        thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
        recent_processes = Processo.objects.filter(data1__gte=thirty_days_ago).count()
        
        end_time = time.time()
        response_time_ms = (end_time - start_time) * 1000
        
        # Log the metric
        log_system_health_metric(
            metric_type='api_response',
            value=round(response_time_ms, 2),
            unit='ms',
            details={
                'operation': 'count_recent_processes',
                'result_count': recent_processes,
                'timestamp': timezone.now().isoformat()
            }
        )
        
        return response_time_ms
        
    except Exception as e:
        log_system_health_metric(
            metric_type='api_response',
            value=9999,
            unit='ms',
            details={
                'error': str(e),
                'timestamp': timezone.now().isoformat()
            }
        )
        return 9999


def calculate_error_rate():
    """
    Calculate system error rate based on failed PDF generations in last hour
    
    Returns:
        float: Error rate as percentage
    """
    try:
        one_hour_ago = timezone.now() - timezone.timedelta(hours=1)
        
        # Count total and failed PDF generations in last hour
        total_pdfs = PDFGenerationLog.objects.filter(
            generated_at__gte=one_hour_ago
        ).count()
        
        failed_pdfs = PDFGenerationLog.objects.filter(
            generated_at__gte=one_hour_ago,
            success=False
        ).count()
        
        if total_pdfs > 0:
            error_rate = (failed_pdfs / total_pdfs) * 100
        else:
            error_rate = 0
        
        # Log the metric
        log_system_health_metric(
            metric_type='error_rate',
            value=round(error_rate, 2),
            unit='%',
            details={
                'total_pdfs': total_pdfs,
                'failed_pdfs': failed_pdfs,
                'time_window': '1_hour',
                'timestamp': timezone.now().isoformat()
            }
        )
        
        return error_rate
        
    except Exception as e:
        log_system_health_metric(
            metric_type='error_rate',
            value=0,
            unit='%',
            details={
                'error': str(e),
                'timestamp': timezone.now().isoformat()
            }
        )
        return 0


def get_active_users_count():
    """
    Get count of users who have been active in the last 30 minutes
    
    Returns:
        int: Number of recently active users
    """
    try:
        # Check for recent user activity in UserActivityLog
        thirty_minutes_ago = timezone.now() - timezone.timedelta(minutes=30)
        
        from analytics.models import UserActivityLog
        
        # Count users who have had any activity in the last 30 minutes
        recent_active_users = UserActivityLog.objects.filter(
            timestamp__gte=thirty_minutes_ago,
            user__isnull=False
        ).values('user').distinct().count()
        
        # If no recent activity logs, fall back to a more conservative session check
        if recent_active_users == 0:
            # Look for sessions that were created or accessed recently
            # This is a rough approximation based on session creation
            
            # Get sessions that expire more than 2 weeks from now (recently created)
            two_weeks_from_now = timezone.now() + timezone.timedelta(days=14)
            recent_sessions = Session.objects.filter(
                expire_date__gte=timezone.now(),
                expire_date__lte=two_weeks_from_now  # Sessions usually expire in 2 weeks
            )
            
            # Count unique users from recent sessions
            active_user_ids = set()
            for session in recent_sessions:
                session_data = session.get_decoded()
                user_id = session_data.get('_auth_user_id')
                if user_id:
                    active_user_ids.add(user_id)
            
            return len(active_user_ids)
        
        return recent_active_users
        
    except Exception as e:
        print(f"Warning: Failed to count active users: {e}")
        return 0


def collect_all_health_metrics():
    """
    Collect all system health metrics and return a summary
    
    Returns:
        dict: Summary of all collected metrics
    """
    print("🔍 Collecting system health metrics...")
    
    metrics = {
        'database_performance': measure_database_performance(),
        'pdf_memory_usage': measure_pdf_memory_usage(),
        'api_response_time': measure_api_response_time(),
        'error_rate': calculate_error_rate(),
        'active_users': get_active_users_count(),
        'timestamp': timezone.now().isoformat()
    }
    
    print(f"✅ Collected metrics: {metrics}")
    return metrics


def get_system_status():
    """
    Determine overall system status based on recent metrics
    
    Returns:
        dict: System status with overall health and recent metrics
    """
    try:
        # Get latest metrics from the last 5 minutes
        five_minutes_ago = timezone.now() - timezone.timedelta(minutes=5)
        
        recent_metrics = {}
        for metric_type, _ in SystemHealthLog._meta.get_field('metric_type').choices:
            latest = SystemHealthLog.objects.filter(
                metric_type=metric_type,
                timestamp__gte=five_minutes_ago
            ).order_by('-timestamp').first()
            
            if latest:
                recent_metrics[metric_type] = {
                    'value': float(latest.value),
                    'unit': latest.unit,
                    'timestamp': latest.timestamp.isoformat(),
                    'details': latest.details
                }
        
        # Determine overall status
        status = 'healthy'
        error_count = 0
        
        # Check database performance (should be < 100ms)
        db_perf = recent_metrics.get('database_query', {}).get('value', 0)
        if db_perf > 500:
            status = 'critical'
            error_count += 1
        elif db_perf > 200:
            status = 'warning'
        
        # Check error rate (should be < 5%)
        error_rate = recent_metrics.get('error_rate', {}).get('value', 0)
        if error_rate > 20:
            status = 'critical'
            error_count += 1
        elif error_rate > 10:
            status = 'warning'
        
        # Check memory usage (should be reasonable)
        memory_usage = recent_metrics.get('pdf_memory', {}).get('value', 0)
        if memory_usage > 500:  # More than 500MB
            status = 'warning'
        
        return {
            'status': status,
            'metrics': recent_metrics,
            'error_count': error_count,
            'last_updated': timezone.now().isoformat(),
            'active_users': get_active_users_count()
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'last_updated': timezone.now().isoformat(),
            'active_users': 0
        }