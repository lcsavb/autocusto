import os
import glob
import subprocess
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
            
            # Encrypt the backup file
            encrypted_file = f"{backup_file}.gpg"
            encrypted_filename = f"{filename}.gpg"
            remote_path = f'backups/{encrypted_filename}'
            
            try:
                # Encrypt the backup file using GPG
                encrypt_cmd = [
                    'gpg', '--trust-model', 'always', '--cipher-algo', 'AES256',
                    '--compress-algo', '2', '--encrypt', '-r', 'lcsavb@gmail.com',
                    '--output', encrypted_file, backup_file
                ]
                
                result = subprocess.run(encrypt_cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    self.stdout.write(
                        self.style.ERROR(f'Failed to encrypt {filename}: {result.stderr}')
                    )
                    continue
                
                self.stdout.write(f'Encrypted {filename} successfully')
                
                # Check if encrypted file already exists on Nextcloud
                try:
                    client.ls(remote_path)
                    self.stdout.write(f'Encrypted file {encrypted_filename} already exists on Nextcloud')
                except:
                    # File doesn't exist, upload the encrypted version
                    client.upload_file(encrypted_file, remote_path)
                    self.stdout.write(
                        self.style.SUCCESS(f'Uploaded encrypted {encrypted_filename} to Nextcloud')
                    )
                
                # Clean up local encrypted file after upload
                if os.path.exists(encrypted_file):
                    os.remove(encrypted_file)
                    self.stdout.write(f'Cleaned up local encrypted file {encrypted_filename}')
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to process {filename}: {str(e)}')
                )
                # Clean up encrypted file if it exists
                if os.path.exists(encrypted_file):
                    os.remove(encrypted_file)