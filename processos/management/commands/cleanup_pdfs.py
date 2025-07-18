import os
import time
import glob
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Clean up old PDF files from /tmp directory'

    def add_arguments(self, parser):
        parser.add_argument(
            '--max-age-minutes',
            type=int,
            default=5,
            help='Maximum age of PDF files in minutes (default: 5)'
        )

    def handle(self, *args, **options):
        max_age_minutes = options['max_age_minutes']
        max_age_seconds = max_age_minutes * 60
        
        self.stdout.write(f'Cleaning up PDFs older than {max_age_minutes} minutes...')
        
        # Find all PDF files in /tmp that match our naming pattern
        pdf_files = glob.glob("/tmp/pdf_*.pdf")
        
        if not pdf_files:
            self.stdout.write('No PDF files found in /tmp')
            return
        
        current_time = time.time()
        deleted_count = 0
        
        for pdf_file in pdf_files:
            try:
                file_age = current_time - os.path.getmtime(pdf_file)
                
                if file_age > max_age_seconds:
                    os.remove(pdf_file)
                    self.stdout.write(f'Deleted: {pdf_file}')
                    deleted_count += 1
                    
            except Exception as e:
                self.stdout.write(f'Error processing {pdf_file}: {e}')
        
        self.stdout.write(f'Cleanup complete: Deleted {deleted_count} PDF files')