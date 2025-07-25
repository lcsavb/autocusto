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
from medicos.models import MEDICAL_SPECIALTIES

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
    from analytics.health_utils import get_system_status, get_active_users_count
    
    try:
        # Get system status with real metrics
        system_data = get_system_status()
        
        # Get recent PDF errors for additional context
        hours = int(request.GET.get('hours', 1))
        start_time = timezone.now() - timedelta(hours=hours)
        recent_pdf_errors = PDFGenerationLog.objects.filter(
            generated_at__gte=start_time,
            success=False
        ).count()
        
        # Calculate uptime percentage (simplified - based on error rate)
        error_rate = system_data.get('metrics', {}).get('error_rate', {}).get('value', 0)
        uptime = max(99.0, 100.0 - error_rate)  # Simplified uptime calculation
        
        # Enhanced response with real data
        data = {
            'status': system_data['status'],
            'metrics': system_data['metrics'],
            'recent_pdf_errors': recent_pdf_errors,
            'active_users': system_data.get('active_users', 0),
            'uptime_percentage': round(uptime, 1),
            'last_updated': timezone.now().isoformat(),
            'data_source': 'real_metrics'
        }
        
        # If no recent metrics, collect some now
        if not system_data['metrics']:
            from analytics.health_utils import collect_all_health_metrics
            fresh_metrics = collect_all_health_metrics()
            data['fresh_collection'] = True
            data['metrics'] = {
                'database_query': {'value': fresh_metrics['database_performance'], 'unit': 'ms'},
                'pdf_memory': {'value': fresh_metrics['pdf_memory_usage'], 'unit': 'MB'},
                'api_response': {'value': fresh_metrics['api_response_time'], 'unit': 'ms'},
                'error_rate': {'value': fresh_metrics['error_rate'], 'unit': '%'}
            }
        
        return JsonResponse(data)
        
    except Exception as e:
        # Fallback response in case of errors
        return JsonResponse({
            'status': 'error',
            'error': str(e),
            'metrics': {},
            'recent_pdf_errors': 0,
            'active_users': 0,
            'uptime_percentage': 0,
            'last_updated': timezone.now().isoformat(),
            'data_source': 'error_fallback'
        })


@staff_member_required
def user_list_analytics(request):
    """Enhanced user analytics list with specialties, activity, and process data"""
    # Get all users with their related data
    users = User.objects.filter(is_active=True).prefetch_related(
        'medicos', 'processos', 'activity_logs'  
    ).annotate(
        login_count_total=Count('activity_logs', filter=Q(activity_logs__activity_type='login'), distinct=True)
    ).order_by('-process_count')
    
    # Build comprehensive user data
    user_analytics = []
    for user in users:
        medico = user.medicos.first()
        
        # Get disease statistics for this user
        disease_stats = Processo.objects.filter(usuario=user).values(
            'doenca__nome', 'doenca__cid'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:5]  # Top 5 diseases
        
        # Get recent login activity
        last_login = UserActivityLog.objects.filter(
            user=user, 
            activity_type='login'
        ).order_by('-timestamp').first()
        
        # Calculate login frequency (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_logins = UserActivityLog.objects.filter(
            user=user,
            activity_type='login',
            timestamp__gte=thirty_days_ago
        ).count()
        
        user_data = {
            'user': user,
            'medico': medico,
            'specialty': dict(MEDICAL_SPECIALTIES).get(medico.especialidade, 'Não informado') if medico and medico.especialidade else 'Não informado',
            'state': medico.get_estado_display() if medico and medico.estado else 'Não informado',
            'crm': f"{medico.crm_medico}/{medico.estado}" if medico and medico.crm_medico and medico.estado else 'Não informado',
            'process_count': user.process_count,
            'login_count': user.login_count_total,
            'recent_logins': recent_logins,
            'last_login': last_login,
            'disease_stats': list(disease_stats),
            'top_disease': disease_stats[0] if disease_stats else None,
        }
        user_analytics.append(user_data)
    
    context = {
        'user_analytics': user_analytics,
        'total_users': len(user_analytics),
        'active_users_30d': len([u for u in user_analytics if u['recent_logins'] > 0]),
        'total_processes': sum(u['process_count'] for u in user_analytics),
    }
    
    return render(request, 'analytics/user_list.html', context)


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
    
    # Disease breakdown
    disease_breakdown = Processo.objects.filter(usuario=user).values(
        'doenca__nome', 'doenca__cid'
    ).annotate(
        process_count=Count('id')
    ).order_by('-process_count')
    
    # Login activity (last 30 days)
    login_activity = UserActivityLog.objects.filter(
        user=user,
        activity_type__in=['login', 'logout'],
        timestamp__gte=timezone.now() - timedelta(days=30)
    ).order_by('-timestamp')[:20]
    
    medico = user.medicos.first()
    
    context = {
        'user': user,
        'medico': medico,
        'specialty': dict(MEDICAL_SPECIALTIES).get(medico.especialidade, 'Não informado') if medico and medico.especialidade else 'Não informado',
        'total_patients': Paciente.objects.filter(usuarios=user).count(),
        'total_processes': user.process_count,
        'disease_breakdown': disease_breakdown,
        'pdf_stats': pdf_stats,
        'login_activity': login_activity,
        'last_login': UserActivityLog.objects.filter(
            user=user, 
            activity_type='login'
        ).order_by('-timestamp').first(),
    }
    
    return render(request, 'analytics/user_detail.html', context)


@staff_member_required
def api_user_analytics(request):
    """API endpoint for user analytics data"""
    # Get all active users with analytics data
    users = User.objects.filter(is_active=True).prefetch_related(
        'medicos', 'processos__doenca'
    ).annotate(
        login_count_total=Count('activity_logs', filter=Q(activity_logs__activity_type='login'), distinct=True)
    )
    
    user_data = []
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    for user in users:
        medico = user.medicos.first()
        
        # Get disease statistics
        disease_stats = Processo.objects.filter(usuario=user).values(
            'doenca__nome', 'doenca__cid'
        ).annotate(count=Count('id')).order_by('-count')
        
        # Recent login activity
        recent_logins = UserActivityLog.objects.filter(
            user=user,
            activity_type='login',
            timestamp__gte=thirty_days_ago
        ).count()
        
        last_login = UserActivityLog.objects.filter(
            user=user, 
            activity_type='login'
        ).order_by('-timestamp').first()
        
        user_info = {
            'id': user.id,
            'email': user.email,
            'name': medico.nome_medico if medico else 'N/A',
            'specialty': dict(MEDICAL_SPECIALTIES).get(medico.especialidade, 'Não informado') if medico and medico.especialidade else 'Não informado',
            'state': medico.get_estado_display() if medico and medico.estado else 'N/A',
            'crm': f"{medico.crm_medico}/{medico.estado}" if medico and medico.crm_medico and medico.estado else 'N/A',
            'process_count': user.process_count,
            'total_logins': user.login_count_total,
            'recent_logins_30d': recent_logins,
            'last_login': last_login.timestamp.isoformat() if last_login else None,
            'diseases': [
                {
                    'name': d['doenca__nome'],
                    'cid': d['doenca__cid'],
                    'count': d['count']
                } for d in disease_stats
            ],
            'top_disease': disease_stats[0]['doenca__nome'] if disease_stats else 'N/A',
            'date_joined': user.date_joined.isoformat(),
        }
        user_data.append(user_info)
    
    # Sort by process count descending
    user_data.sort(key=lambda x: x['process_count'], reverse=True)
    
    # Summary statistics
    total_users = len(user_data)
    active_users_30d = len([u for u in user_data if u['recent_logins_30d'] > 0])
    total_processes = sum(u['process_count'] for u in user_data)
    
    # Specialty breakdown
    specialty_stats = {}
    for user in user_data:
        specialty = user['specialty']
        if specialty not in specialty_stats:
            specialty_stats[specialty] = {'count': 0, 'processes': 0}
        specialty_stats[specialty]['count'] += 1
        specialty_stats[specialty]['processes'] += user['process_count']
    
    response_data = {
        'users': user_data,
        'summary': {
            'total_users': total_users,
            'active_users_30d': active_users_30d,
            'total_processes': total_processes,
            'avg_processes_per_user': round(total_processes / total_users, 2) if total_users > 0 else 0,
        },
        'specialty_breakdown': [
            {
                'specialty': k,
                'user_count': v['count'],
                'total_processes': v['processes'],
                'avg_processes': round(v['processes'] / v['count'], 2) if v['count'] > 0 else 0
            }
            for k, v in specialty_stats.items()
        ],
        'last_updated': timezone.now().isoformat()
    }
    
    return JsonResponse(response_data)


@staff_member_required  
def api_disease_analytics(request):
    """API endpoint for disease analytics by user"""
    # Get disease statistics grouped by user and specialty
    disease_data = Processo.objects.select_related(
        'usuario', 'doenca', 'usuario__medicos'
    ).values(
        'doenca__nome',
        'doenca__cid', 
        'usuario__medicos__especialidade'
    ).annotate(
        process_count=Count('id'),
        unique_users=Count('usuario', distinct=True)
    ).order_by('-process_count')
    
    # Group by disease
    disease_stats = {}
    for item in disease_data:
        disease_name = item['doenca__nome']
        disease_cid = item['doenca__cid']
        specialty = item['usuario__medicos__especialidade']
        specialty_display = dict(MEDICAL_SPECIALTIES).get(specialty, 'Não informado') if specialty else 'Não informado'
        
        if disease_name not in disease_stats:
            disease_stats[disease_name] = {
                'name': disease_name,
                'cid': disease_cid,
                'total_processes': 0,
                'unique_users': 0,
                'by_specialty': {}
            }
        
        disease_stats[disease_name]['total_processes'] += item['process_count']
        disease_stats[disease_name]['unique_users'] += item['unique_users']
        
        if specialty_display not in disease_stats[disease_name]['by_specialty']:
            disease_stats[disease_name]['by_specialty'][specialty_display] = 0
        disease_stats[disease_name]['by_specialty'][specialty_display] += item['process_count']
    
    # Convert to list and sort
    disease_list = list(disease_stats.values())
    disease_list.sort(key=lambda x: x['total_processes'], reverse=True)
    
    return JsonResponse({
        'diseases': disease_list,
        'total_diseases': len(disease_list),
        'last_updated': timezone.now().isoformat()
    })
