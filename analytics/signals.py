import time
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.auth import get_user_model
from analytics.models import UserActivityLog, PDFGenerationLog
from processos.models import Processo
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


def get_client_ip(request):
    """Extract client IP from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent(request):
    """Extract user agent from request"""
    return request.META.get('HTTP_USER_AGENT', '')


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Track successful login"""
    try:
        UserActivityLog.objects.create(
            user=user,
            activity_type='login',
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            session_key=request.session.session_key if hasattr(request, 'session') and request.session.session_key else ''
        )
        
        # Note: Daily metrics updated via management command, not real-time
        
    except Exception as e:
        logger.error(f"Error logging user login: {e}")


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Track logout"""
    try:
        if user:
            UserActivityLog.objects.create(
                user=user,
                activity_type='logout',
                ip_address=get_client_ip(request),
                user_agent=get_user_agent(request),
                session_key=request.session.session_key if hasattr(request, 'session') and request.session.session_key else ''
            )
    except Exception as e:
        logger.error(f"Error logging user logout: {e}")


@receiver(user_login_failed)
def log_login_failed(sender, credentials, request, **kwargs):
    """Track failed login attempts"""
    try:
        # Try to find user by email
        email = credentials.get('username', '')
        user = None
        if email:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                pass
        
        UserActivityLog.objects.create(
            user=user,
            activity_type='failed_login',
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            extra_data={'attempted_username': email}
        )
        
        # Note: Daily metrics updated via management command, not real-time
        
    except Exception as e:
        logger.error(f"Error logging failed login: {e}")


@receiver(post_save, sender=User)
def log_user_signup(sender, instance, created, **kwargs):
    """Track new user signups"""
    if created:
        try:
            UserActivityLog.objects.create(
                user=instance,
                activity_type='signup',
                timestamp=instance.date_joined
            )
            
            # Note: Daily metrics updated via management command, not real-time
            
        except Exception as e:
            logger.error(f"Error logging user signup: {e}")


# Patient and Process metrics are calculated via management command, not signals


# PDF generation tracking will be done via decorator
def track_pdf_generation(pdf_type='prescription'):
    """Decorator to track PDF generation"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            request = None
            user = None
            processo = None
            
            # Extract request and processo from args/kwargs
            for arg in args:
                if hasattr(arg, 'user'):  # It's a request
                    request = arg
                    user = request.user
                elif hasattr(arg, 'usuario'):  # It's a processo
                    processo = arg
                    user = processo.usuario
            
            # Also check kwargs for explicit user parameter
            request = kwargs.get('request', request)
            processo = kwargs.get('processo', processo)
            user = kwargs.get('user', user)  # Explicit user parameter
            
            # If no user found yet, try to extract from prescription data
            if not user and args and len(args) > 1 and isinstance(args[1], dict):
                prescription_data = args[1]
                user = prescription_data.get('usuario')
            
            success = True
            error_message = ''
            result = None
            
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                success = False
                error_message = str(e)
                raise
            finally:
                try:
                    generation_time_ms = int((time.time() - start_time) * 1000)
                    
                    # Only log if we have a user (required field)
                    if user:
                        log_entry = PDFGenerationLog.objects.create(
                            user=user,
                            processo=processo,
                            paciente=processo.paciente if processo else None,
                            doenca=processo.doenca if processo else None,
                            clinica=processo.emissor.clinica if processo and processo.emissor else None,
                            generation_time_ms=generation_time_ms,
                            success=success,
                            error_message=error_message or '',
                            pdf_type=pdf_type,
                            ip_address=get_client_ip(request) if request else '',
                            user_agent=get_user_agent(request) if request else ''
                        )
                        
                        # Note: Daily PDF metrics updated via management command, not real-time
                    else:
                        logger.warning(f"PDF generation tracking skipped - no user found for {pdf_type}")
                    
                except Exception as e:
                    logger.error(f"Error tracking PDF generation: {e}")
            
            return result
        return wrapper
    return decorator