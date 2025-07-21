import os
import glob
from django.core.management.base import BaseCommand
from webdav4.client import Client


class Command(BaseCommand):
    help = 'Upload database backups to Nextcloud'

    def handle(self, *args, **options):
        # Nextcloud configuration
        nc_url = os.environ.get('NC_BACKUP_URL')
        nc_username = os.environ.get('NC_BACKUP_USERNAME')
        nc_password = os.environ.get('NC_BACKUP_PASSWORD')
        
        if not all([nc_url, nc_username, nc_password]):
            self.stdout.write(
                self.style.WARNING('Nextcloud credentials not configured')
            )
            return
        
        # WebDAV client setup with webdav4
        client = Client(nc_url, auth=(nc_username, nc_password), timeout=60)
        
        # Find backup files
        backup_dir = '/var/backups/autocusto/'
        backup_files = glob.glob(os.path.join(backup_dir, 'autocusto_db_*.psql.bin'))
        
        try:
            # Test connection first
            client.ls("/")
            
            # Ensure backups directory exists
            try:
                client.ls("backups/")
            except:
                client.mkdir("backups")
                self.stdout.write(
                    self.style.SUCCESS('Created backups directory on Nextcloud')
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Connection error: {str(e)}')
            )
            return
        
        for backup_file in backup_files:
            filename = os.path.basename(backup_file)
            remote_path = f'backups/{filename}'
            
            try:
                # Check if file already exists on Nextcloud
                try:
                    client.ls(remote_path)
                    self.stdout.write(f'File {filename} already exists on Nextcloud')
                except:
                    # File doesn't exist, upload it
                    client.upload_file(backup_file, remote_path)
                    self.stdout.write(
                        self.style.SUCCESS(f'Uploaded {filename} to Nextcloud')
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to upload {filename}: {str(e)}')
                )