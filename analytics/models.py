from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from processos.models import Processo, Doenca, Medicamento
from clinicas.models import Clinica
from pacientes.models import Paciente

User = get_user_model()


class PDFGenerationLog(models.Model):
    """Track every PDF generation event"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pdf_generations')
    processo = models.ForeignKey(Processo, on_delete=models.SET_NULL, null=True, blank=True)
    paciente = models.ForeignKey(Paciente, on_delete=models.SET_NULL, null=True, blank=True)
    doenca = models.ForeignKey(Doenca, on_delete=models.SET_NULL, null=True, blank=True)
    clinica = models.ForeignKey(Clinica, on_delete=models.SET_NULL, null=True, blank=True)
    
    generated_at = models.DateTimeField(default=timezone.now)
    generation_time_ms = models.IntegerField(null=True, blank=True)  # Time taken to generate
    file_size_bytes = models.IntegerField(null=True, blank=True)
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    
    pdf_type = models.CharField(max_length=50, choices=[
        ('prescription', 'Prescrição'),
        ('protocol', 'Protocolo'),
        ('renewal', 'Renovação'),
        ('other', 'Outro')
    ], default='prescription')
    
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        db_table = 'analytics_pdf_generation_log'
        indexes = [
            models.Index(fields=['user', '-generated_at']),
            models.Index(fields=['generated_at']),
            models.Index(fields=['doenca']),
            models.Index(fields=['clinica']),
        ]
        ordering = ['-generated_at']


class UserActivityLog(models.Model):
    """Track user login/logout and other activities"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs', null=True, blank=True)
    activity_type = models.CharField(max_length=50, choices=[
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('signup', 'Cadastro'),
        ('password_reset', 'Reset de Senha'),
        ('profile_update', 'Atualização de Perfil'),
        ('failed_login', 'Tentativa de Login Falha'),
    ])
    
    timestamp = models.DateTimeField(default=timezone.now)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    session_key = models.CharField(max_length=40, blank=True)
    
    extra_data = models.JSONField(default=dict, blank=True)  # For additional context
    
    class Meta:
        db_table = 'analytics_user_activity_log'
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['activity_type', '-timestamp']),
            models.Index(fields=['timestamp']),
        ]
        ordering = ['-timestamp']


class DailyMetrics(models.Model):
    """Aggregated daily metrics for performance"""
    date = models.DateField(unique=True)
    
    # User metrics
    total_users = models.IntegerField(default=0)
    new_users = models.IntegerField(default=0)
    active_users = models.IntegerField(default=0)
    total_logins = models.IntegerField(default=0)
    failed_logins = models.IntegerField(default=0)
    
    # PDF metrics
    pdfs_generated = models.IntegerField(default=0)
    pdf_errors = models.IntegerField(default=0)
    avg_pdf_generation_time_ms = models.IntegerField(null=True, blank=True)
    total_pdf_size_mb = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Healthcare metrics
    total_patients = models.IntegerField(default=0)
    new_patients = models.IntegerField(default=0)
    total_processes = models.IntegerField(default=0)
    new_processes = models.IntegerField(default=0)
    
    # System metrics
    database_size_mb = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    backup_success = models.BooleanField(null=True)
    error_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'analytics_daily_metrics'
        ordering = ['-date']


class ClinicMetrics(models.Model):
    """Metrics per clinic"""
    clinic = models.ForeignKey(Clinica, on_delete=models.CASCADE, related_name='metrics')
    date = models.DateField()
    
    active_doctors = models.IntegerField(default=0)
    pdfs_generated = models.IntegerField(default=0)
    unique_patients = models.IntegerField(default=0)
    new_processes = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'analytics_clinic_metrics'
        unique_together = [['clinic', 'date']]
        indexes = [
            models.Index(fields=['clinic', '-date']),
            models.Index(fields=['date']),
        ]


class DiseaseMetrics(models.Model):
    """Track disease prevalence and treatment patterns"""
    disease = models.ForeignKey(Doenca, on_delete=models.CASCADE, related_name='metrics')
    date = models.DateField()
    
    process_count = models.IntegerField(default=0)
    pdf_count = models.IntegerField(default=0)
    unique_patients = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'analytics_disease_metrics'
        unique_together = [['disease', 'date']]
        indexes = [
            models.Index(fields=['disease', '-date']),
            models.Index(fields=['date']),
        ]


class MedicationUsage(models.Model):
    """Track medication prescription patterns"""
    medication = models.ForeignKey(Medicamento, on_delete=models.CASCADE, related_name='usage_metrics')
    disease = models.ForeignKey(Doenca, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField()
    
    prescription_count = models.IntegerField(default=0)
    unique_patients = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'analytics_medication_usage'
        unique_together = [['medication', 'disease', 'date']]
        indexes = [
            models.Index(fields=['medication', '-date']),
            models.Index(fields=['date']),
        ]


class SystemHealthLog(models.Model):
    """Track system health and performance"""
    timestamp = models.DateTimeField(default=timezone.now)
    
    metric_type = models.CharField(max_length=50, choices=[
        ('database_query', 'Database Query Performance'),
        ('pdf_memory', 'PDF Memory Usage'),
        ('api_response', 'API Response Time'),
        ('backup_status', 'Backup Status'),
        ('error_rate', 'Error Rate'),
    ])
    
    value = models.DecimalField(max_digits=12, decimal_places=2)
    unit = models.CharField(max_length=20)  # ms, MB, percentage, etc.
    
    details = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'analytics_system_health_log'
        indexes = [
            models.Index(fields=['metric_type', '-timestamp']),
            models.Index(fields=['timestamp']),
        ]
        ordering = ['-timestamp']
