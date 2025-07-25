"""
Management command to collect system health metrics

This command can be run manually or scheduled via cron to collect
real-time system health data for the analytics dashboard.

Usage:
    python manage.py collect_health_metrics
    python manage.py collect_health_metrics --simulate  # For testing
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from analytics.health_utils import collect_all_health_metrics
from analytics.models import SystemHealthLog


class Command(BaseCommand):
    help = 'Collect system health metrics and store them in the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--simulate',
            action='store_true',
            help='Generate simulated data for testing',
        )
        parser.add_argument(
            '--cleanup',
            action='store_true',
            help='Clean up old health metrics (older than 7 days)',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🔍 Starting system health metrics collection...')
        )

        if options['cleanup']:
            self.cleanup_old_metrics()

        if options['simulate']:
            self.generate_simulated_data()
        else:
            self.collect_real_metrics()

        self.stdout.write(
            self.style.SUCCESS('✅ System health metrics collection completed!')
        )

    def collect_real_metrics(self):
        """Collect real system health metrics"""
        try:
            metrics = collect_all_health_metrics()
            
            self.stdout.write(f"📊 Collected metrics:")
            for key, value in metrics.items():
                if key != 'timestamp':
                    if isinstance(value, float):
                        self.stdout.write(f"   • {key}: {value:.2f}")
                    else:
                        self.stdout.write(f"   • {key}: {value}")
            
            # Count total health records
            total_records = SystemHealthLog.objects.count()
            self.stdout.write(f"📈 Total health records in database: {total_records}")
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error collecting metrics: {e}')
            )
            raise

    def generate_simulated_data(self):
        """Generate simulated data for testing purposes"""
        import random
        from decimal import Decimal
        
        self.stdout.write("🎭 Generating simulated health data...")
        
        # Define realistic ranges for each metric type
        metrics_config = [
            ('database_query', 20, 150, 'ms'),      # 20-150ms DB queries
            ('pdf_memory', 15, 80, 'MB'),           # 15-80MB memory usage
            ('api_response', 50, 300, 'ms'),        # 50-300ms API response
            ('error_rate', 0, 5, '%'),              # 0-5% error rate
            ('backup_status', 0, 1, 'success'),     # 0=fail, 1=success
        ]
        
        # Generate data for the last 2 hours (every 5 minutes)
        now = timezone.now()
        for i in range(24):  # 24 data points (2 hours, every 5 minutes)
            timestamp = now - timezone.timedelta(minutes=i * 5)
            
            for metric_type, min_val, max_val, unit in metrics_config:
                # Add some realistic variation
                if metric_type == 'error_rate':
                    # Error rate should usually be low
                    value = random.uniform(0, 2) if random.random() > 0.2 else random.uniform(2, max_val)
                elif metric_type == 'backup_status':
                    # Backup should usually succeed
                    value = 1 if random.random() > 0.1 else 0
                else:
                    # Normal distribution around middle of range
                    mid_point = (min_val + max_val) / 2
                    value = random.normalvariate(mid_point, (max_val - min_val) / 6)
                    value = max(min_val, min(max_val, value))  # Clamp to range
                
                SystemHealthLog.objects.create(
                    metric_type=metric_type,
                    value=Decimal(str(round(value, 2))),
                    unit=unit,
                    timestamp=timestamp,
                    details={
                        'simulated': True,
                        'generated_at': timezone.now().isoformat(),
                        'data_point': i
                    }
                )
        
        total_created = len(metrics_config) * 24
        self.stdout.write(f"✨ Created {total_created} simulated health records")

    def cleanup_old_metrics(self):
        """Clean up health metrics older than 7 days"""
        seven_days_ago = timezone.now() - timezone.timedelta(days=7)
        
        old_count = SystemHealthLog.objects.filter(
            timestamp__lt=seven_days_ago
        ).count()
        
        if old_count > 0:
            SystemHealthLog.objects.filter(
                timestamp__lt=seven_days_ago
            ).delete()
            
            self.stdout.write(f"🗑️ Cleaned up {old_count} old health records")
        else:
            self.stdout.write("🧹 No old health records to clean up")