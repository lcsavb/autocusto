from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.db.models import Count, Q, Avg, Sum, Max, Min
from django.utils import timezone
from datetime import datetime, timedelta
from analytics.models import (
    PDFGenerationLog, UserActivityLog, DailyMetrics, 
    ClinicMetrics, DiseaseMetrics, MedicationUsage, SystemHealthLog
)
from django.contrib.auth import get_user_model
from processos.models import Processo, Doenca, Medicamento
from clinicas.models import Clinica
from pacientes.models import Paciente

User = get_user_model()


@staff_member_required
def analytics_dashboard(request):
    """Main analytics dashboard - uses cached daily metrics"""
    today = timezone.now().date()
    
    # Get latest daily metrics
    latest_metrics = DailyMetrics.objects.order_by('-date').first()
    
    # Basic counts (these are fast queries)
    context = {
        'total_users': User.objects.count(),
        'total_patients': Paciente.objects.count(),
        'total_processes': Processo.objects.count(),
        'total_clinics': Clinica.objects.count(),
        'latest_metrics': latest_metrics,
        'last_updated': latest_metrics.updated_at if latest_metrics else None,
    }
    
    return render(request, 'analytics/dashboard.html', context)


@staff_member_required
def api_daily_trends(request):
    """API for daily trends chart data - cached data"""
    days = int(request.GET.get('days', 30))
    
    metrics = DailyMetrics.objects.order_by('-date')[:days]
    metrics = list(reversed(metrics))  # Chronological order
    
    data = {
        'dates': [m.date.strftime('%Y-%m-%d') for m in metrics],
        'new_users': [m.new_users for m in metrics],
        'active_users': [m.active_users for m in metrics],
        'pdfs_generated': [m.pdfs_generated for m in metrics],
        'total_logins': [m.total_logins for m in metrics],
        'failed_logins': [m.failed_logins for m in metrics],
        'new_patients': [m.new_patients for m in metrics],
        'new_processes': [m.new_processes for m in metrics],
    }
    
    return JsonResponse(data)


@staff_member_required
def api_pdf_analytics(request):
    """PDF generation analytics - aggregated data"""
    days = int(request.GET.get('days', 30))
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    
    # PDF by type (from logs)
    pdf_by_type = PDFGenerationLog.objects.filter(
        generated_at__date__range=(start_date, end_date)
    ).values('pdf_type').annotate(count=Count('id')).order_by('-count')
    
    # Top PDF generators
    top_users = PDFGenerationLog.objects.filter(
        generated_at__date__range=(start_date, end_date),
        success=True
    ).values('user__email').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Performance metrics
    performance = PDFGenerationLog.objects.filter(
        generated_at__date__range=(start_date, end_date),
        success=True
    ).aggregate(
        avg_time=Avg('generation_time_ms'),
        max_time=Max('generation_time_ms'),
        min_time=Min('generation_time_ms')
    )
    
    data = {
        'pdf_by_type': list(pdf_by_type),
        'top_users': list(top_users),
        'avg_generation_time': performance['avg_time'] or 0,
        'max_generation_time': performance['max_time'] or 0,
        'min_generation_time': performance['min_time'] or 0,
    }
    
    return JsonResponse(data)


@staff_member_required
def api_healthcare_insights(request):
    """Healthcare metrics - aggregated daily data"""
    days = int(request.GET.get('days', 30))
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    
    # Top diseases
    diseases = DiseaseMetrics.objects.filter(
        date__range=(start_date, end_date)
    ).values('disease__nome').annotate(
        total_processes=Sum('process_count'),
        total_pdfs=Sum('pdf_count')
    ).order_by('-total_processes')[:10]
    
    # Clinic performance
    clinics = ClinicMetrics.objects.filter(
        date__range=(start_date, end_date)
    ).values('clinic__nome_clinica').annotate(
        total_pdfs=Sum('pdfs_generated'),
        unique_patients=Sum('unique_patients')
    ).order_by('-total_pdfs')[:10]
    
    data = {
        'top_diseases': list(diseases),
        'clinic_performance': list(clinics),
    }
    
    return JsonResponse(data)


@staff_member_required
def system_health_dashboard(request):
    """Real-time system health monitoring"""
    return render(request, 'analytics/system_health.html')


@staff_member_required
def api_system_health_realtime(request):
    """Real-time system health API"""
    hours = int(request.GET.get('hours', 1))
    end_time = timezone.now()
    start_time = end_time - timedelta(hours=hours)
    
    # Get latest metrics by type
    latest_metrics = {}
    for metric_type, _ in SystemHealthLog._meta.get_field('metric_type').choices:
        latest = SystemHealthLog.objects.filter(
            metric_type=metric_type,
            timestamp__gte=start_time
        ).order_by('-timestamp').first()
        
        if latest:
            latest_metrics[metric_type] = {
                'value': float(latest.value),
                'unit': latest.unit,
                'timestamp': latest.timestamp.isoformat(),
                'details': latest.details
            }
    
    # Recent errors from PDF generation
    recent_pdf_errors = PDFGenerationLog.objects.filter(
        generated_at__gte=start_time,
        success=False
    ).count()
    
    # System status summary
    status = 'healthy'
    if recent_pdf_errors > 10:
        status = 'warning'
    if recent_pdf_errors > 50:
        status = 'critical'
    
    data = {
        'status': status,
        'metrics': latest_metrics,
        'recent_pdf_errors': recent_pdf_errors,
        'last_updated': timezone.now().isoformat()
    }
    
    return JsonResponse(data)


@staff_member_required
def user_analytics(request, user_id):
    """Individual user analytics"""
    user = get_object_or_404(User, id=user_id)
    last_30_days = timezone.now().date() - timedelta(days=30)
    
    # User metrics
    pdf_stats = PDFGenerationLog.objects.filter(user=user).aggregate(
        total_pdfs=Count('id'),
        recent_pdfs=Count('id', filter=Q(generated_at__date__gte=last_30_days)),
        avg_generation_time=Avg('generation_time_ms', filter=Q(success=True)),
        error_rate=Count('id', filter=Q(success=False))
    )
    
    context = {
        'user': user,
        'total_patients': Paciente.objects.filter(usuario=user).count(),
        'total_processes': Processo.objects.filter(usuario=user).count(),
        'pdf_stats': pdf_stats,
        'last_login': UserActivityLog.objects.filter(
            user=user, 
            activity_type='login'
        ).order_by('-timestamp').first(),
    }
    
    return render(request, 'analytics/user_detail.html', context)
