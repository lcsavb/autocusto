"""
System Health Monitoring Middleware

This middleware automatically collects system health metrics
during request processing to provide real-time monitoring.
"""

import time
import random
from django.utils import timezone
from analytics.health_utils import log_system_health_metric


class SystemHealthMiddleware:
    """
    Middleware to collect system health metrics during request processing
    
    This middleware:
    1. Measures request processing time for API performance monitoring
    2. Periodically triggers health metric collection
    3. Logs important system events
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.last_health_check = timezone.now()
        self.health_check_interval = 300  # 5 minutes

    def __call__(self, request):
        # Start timing the request
        start_time = time.time()
        
        response = self.get_response(request)
        
        # Calculate response time
        response_time_ms = (time.time() - start_time) * 1000
        
        # Log API response time for significant requests (not static files)
        if self._should_log_request(request, response_time_ms):
            log_system_health_metric(
                metric_type='api_response',
                value=round(response_time_ms, 2),
                unit='ms',
                details={
                    'path': request.path,
                    'method': request.method,
                    'status_code': response.status_code,
                    'user_authenticated': request.user.is_authenticated if hasattr(request, 'user') else False,
                    'timestamp': timezone.now().isoformat()
                }
            )
        
        # Periodic health check
        if self._should_run_health_check():
            self._run_background_health_check()
        
        return response

    def _should_log_request(self, request, response_time_ms):
        """
        Determine if this request should be logged for health monitoring
        
        Args:
            request: Django request object
            response_time_ms: Response time in milliseconds
            
        Returns:
            bool: True if request should be logged
        """
        # Skip static files
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            return False
        
        # Skip favicon requests
        if 'favicon' in request.path:
            return False
        
        # Log slow requests (> 100ms)
        if response_time_ms > 100:
            return True
        
        # Log analytics requests
        if request.path.startswith('/analytics/'):
            return True
        
        # Log PDF generation requests
        if 'pdf' in request.path.lower():
            return True
        
        # Randomly sample other requests (10%)
        return random.random() < 0.1

    def _should_run_health_check(self):
        """Check if it's time to run a background health check"""
        now = timezone.now()
        time_since_last = (now - self.last_health_check).total_seconds()
        return time_since_last >= self.health_check_interval

    def _run_background_health_check(self):
        """Run a lightweight background health check"""
        try:
            from analytics.health_utils import measure_database_performance, calculate_error_rate
            
            # Run lightweight checks
            measure_database_performance()
            calculate_error_rate()
            
            self.last_health_check = timezone.now()
            
        except Exception as e:
            # Don't let health monitoring break the application
            print(f"Warning: Background health check failed: {e}")


class PDFGenerationMonitoringMixin:
    """
    Mixin to add to PDF generation functions to monitor performance
    """
    
    @staticmethod
    def log_pdf_generation(pdf_type, generation_time_ms, success=True, error_message=None, user=None):
        """
        Log PDF generation metrics
        
        Args:
            pdf_type: Type of PDF (prescription, protocol, etc.)
            generation_time_ms: Time taken to generate PDF
            success: Whether generation was successful
            error_message: Error message if failed
            user: User who generated the PDF
        """
        try:
            from analytics.models import PDFGenerationLog
            
            PDFGenerationLog.objects.create(
                user=user,
                generated_at=timezone.now(),
                generation_time_ms=int(generation_time_ms),
                success=success,
                error_message=error_message or '',
                pdf_type=pdf_type,
                ip_address=None,  # Could be added if request is available
                user_agent=''     # Could be added if request is available
            )
            
            # Also log as health metric if it's a performance issue
            if generation_time_ms > 5000:  # More than 5 seconds
                log_system_health_metric(
                    metric_type='pdf_memory',
                    value=generation_time_ms / 1000,  # Convert to seconds
                    unit='s',
                    details={
                        'slow_pdf_generation': True,
                        'pdf_type': pdf_type,
                        'success': success,
                        'error': error_message,
                        'timestamp': timezone.now().isoformat()
                    }
                )
                
        except Exception as e:
            print(f"Warning: Failed to log PDF generation: {e}")


def monitor_backup_status(success, details=None):
    """
    Function to log backup status from backup scripts
    
    Args:
        success: Boolean indicating if backup was successful
        details: Additional details about the backup
    """
    try:
        log_system_health_metric(
            metric_type='backup_status',
            value=1 if success else 0,
            unit='success',
            details={
                'backup_details': details or {},
                'timestamp': timezone.now().isoformat()
            }
        )
    except Exception as e:
        print(f"Warning: Failed to log backup status: {e}")