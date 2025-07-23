from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Count, Q, Avg
from django.db import models
from datetime import datetime, timedelta
from analytics.models import (
    DailyMetrics, PDFGenerationLog, UserActivityLog,
    ClinicMetrics, DiseaseMetrics, MedicationUsage
)
from django.contrib.auth import get_user_model
from processos.models import Processo, Doenca, Medicamento
from clinicas.models import Clinica
from pacientes.models import Paciente

User = get_user_model()


class Command(BaseCommand):
    help = 'Calculate daily metrics for analytics dashboard'

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            type=str,
            help='Date to calculate metrics for (YYYY-MM-DD). Defaults to yesterday.',
        )
        parser.add_argument(
            '--days-back',
            type=int,
            default=1,
            help='Number of days back to calculate (default: 1)',
        )

    def handle(self, *args, **options):
        if options['date']:
            target_date = datetime.strptime(options['date'], '%Y-%m-%d').date()
            dates_to_process = [target_date]
        else:
            # Calculate for the last N days
            end_date = timezone.now().date() - timedelta(days=1)  # Yesterday
            days_back = options['days_back']
            dates_to_process = [
                end_date - timedelta(days=i) for i in range(days_back)
            ]

        for date in dates_to_process:
            self.calculate_daily_metrics(date)
            self.calculate_clinic_metrics(date)
            self.calculate_disease_metrics(date)
            self.calculate_medication_usage(date)

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully calculated metrics for {len(dates_to_process)} days'
            )
        )

    def calculate_daily_metrics(self, date):
        """Calculate daily metrics for a specific date"""
        self.stdout.write(f'Calculating daily metrics for {date}...')
        
        # Date range for the day
        start_datetime = timezone.make_aware(datetime.combine(date, datetime.min.time()))
        end_datetime = start_datetime + timedelta(days=1)

        # User metrics
        new_users = User.objects.filter(date_joined__date=date).count()
        total_users = User.objects.filter(date_joined__date__lte=date).count()
        
        # Active users (logged in on this date)
        active_users = UserActivityLog.objects.filter(
            activity_type='login',
            timestamp__date=date
        ).values('user').distinct().count()

        # Login metrics
        total_logins = UserActivityLog.objects.filter(
            activity_type='login',
            timestamp__date=date
        ).count()
        
        failed_logins = UserActivityLog.objects.filter(
            activity_type='failed_login',
            timestamp__date=date
        ).count()

        # PDF metrics
        pdf_logs = PDFGenerationLog.objects.filter(generated_at__date=date)
        pdfs_generated = pdf_logs.filter(success=True).count()
        pdf_errors = pdf_logs.filter(success=False).count()
        
        # Average PDF generation time
        successful_pdfs = pdf_logs.filter(success=True, generation_time_ms__isnull=False)
        avg_pdf_time = None
        if successful_pdfs.exists():
            avg_pdf_time = successful_pdfs.aggregate(
                avg=Avg('generation_time_ms')
            )['avg']

        # Healthcare metrics
        new_patients = Paciente.objects.filter(
            created_at__date=date if hasattr(Paciente, 'created_at') else None
        ).count() if hasattr(Paciente, 'created_at') else 0
        
        total_patients = Paciente.objects.count()
        
        new_processes = Processo.objects.filter(
            created_at__date=date if hasattr(Processo, 'created_at') else None
        ).count() if hasattr(Processo, 'created_at') else 0
        
        total_processes = Processo.objects.count()

        # Create or update daily metrics
        metrics, created = DailyMetrics.objects.update_or_create(
            date=date,
            defaults={
                'total_users': total_users,
                'new_users': new_users,
                'active_users': active_users,
                'total_logins': total_logins,
                'failed_logins': failed_logins,
                'pdfs_generated': pdfs_generated,
                'pdf_errors': pdf_errors,
                'avg_pdf_generation_time_ms': int(avg_pdf_time) if avg_pdf_time else None,
                'total_patients': total_patients,
                'new_patients': new_patients,
                'total_processes': total_processes,
                'new_processes': new_processes,
            }
        )

        action = "Created" if created else "Updated"
        self.stdout.write(f'  {action} daily metrics: {pdfs_generated} PDFs, {active_users} active users')

    def calculate_clinic_metrics(self, date):
        """Calculate clinic-specific metrics"""
        clinics = Clinica.objects.all()
        
        for clinic in clinics:
            # Get users associated with this clinic through their processes
            clinic_processes = Processo.objects.filter(
                emissor__clinica=clinic
            )
            
            # PDFs generated for this clinic on this date
            pdfs_generated = PDFGenerationLog.objects.filter(
                clinica=clinic,
                generated_at__date=date
            ).count()

            # Active doctors in this clinic
            active_doctors = clinic_processes.values('usuario').distinct().count()

            # Unique patients treated
            unique_patients = clinic_processes.values('paciente').distinct().count()

            # New processes created
            new_processes = 0  # Would need created_at field on Processo

            ClinicMetrics.objects.update_or_create(
                clinic=clinic,
                date=date,
                defaults={
                    'active_doctors': active_doctors,
                    'pdfs_generated': pdfs_generated,
                    'unique_patients': unique_patients,
                    'new_processes': new_processes,
                }
            )

    def calculate_disease_metrics(self, date):
        """Calculate disease-specific metrics"""
        diseases = Doenca.objects.all()
        
        for disease in diseases:
            # PDFs generated for this disease
            pdf_count = PDFGenerationLog.objects.filter(
                doenca=disease,
                generated_at__date=date
            ).count()

            # Processes for this disease
            process_count = Processo.objects.filter(doenca=disease).count()

            # Unique patients with this disease
            unique_patients = Processo.objects.filter(
                doenca=disease
            ).values('paciente').distinct().count()

            DiseaseMetrics.objects.update_or_create(
                disease=disease,
                date=date,
                defaults={
                    'process_count': process_count,
                    'pdf_count': pdf_count,
                    'unique_patients': unique_patients,
                }
            )

    def calculate_medication_usage(self, date):
        """Calculate medication usage metrics"""
        medications = Medicamento.objects.all()
        
        for medication in medications:
            # This would require tracking medication usage in processes
            # For now, we'll create placeholder entries
            
            MedicationUsage.objects.update_or_create(
                medication=medication,
                date=date,
                defaults={
                    'prescription_count': 0,  # Would need actual tracking
                    'unique_patients': 0,     # Would need actual tracking
                }
            )