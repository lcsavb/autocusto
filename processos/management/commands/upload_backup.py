import os
import glob
import subprocess
from django.core.management.base import BaseCommand
from webdav4.client import Client


class Command(BaseCommand):
    help = 'Upload database backups to Nextcloud'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('[DEBUG] Starting upload_backup command'))
        
        # Nextcloud configuration
        nc_url = os.environ.get('NC_BACKUP_URL')
        nc_username = os.environ.get('NC_BACKUP_USERNAME')
        nc_password = os.environ.get('NC_BACKUP_PASSWORD')
        
        self.stdout.write(f'[DEBUG] Environment variables:')
        self.stdout.write(f'[DEBUG]   NC_BACKUP_URL: {nc_url}')
        self.stdout.write(f'[DEBUG]   NC_BACKUP_USERNAME: {nc_username}')
        self.stdout.write(f'[DEBUG]   NC_BACKUP_PASSWORD: {"*" * len(nc_password) if nc_password else None}')
        
        if not all([nc_url, nc_username, nc_password]):
            self.stdout.write(
                self.style.WARNING('[DEBUG] Nextcloud credentials not configured - missing values!')
            )
            return
        
        # WebDAV client setup with webdav4
        self.stdout.write('[DEBUG] Creating WebDAV client...')
        client = Client(nc_url, auth=(nc_username, nc_password), timeout=60)
        self.stdout.write('[DEBUG] WebDAV client created successfully')
        
        # Find backup files
        backup_dir = '/var/backups/autocusto/'
        self.stdout.write(f'[DEBUG] Looking for backup files in: {backup_dir}')
        
        # Check if backup directory exists
        if not os.path.exists(backup_dir):
            self.stdout.write(
                self.style.ERROR(f'[DEBUG] Backup directory does not exist: {backup_dir}')
            )
            return
            
        backup_files = glob.glob(os.path.join(backup_dir, 'autocusto_db_*.psql.bin'))
        self.stdout.write(f'[DEBUG] Found {len(backup_files)} backup files:')
        for bf in backup_files:
            file_size = os.path.getsize(bf) if os.path.exists(bf) else 0
            self.stdout.write(f'[DEBUG]   - {bf} ({file_size} bytes)')
        
        if not backup_files:
            self.stdout.write(
                self.style.WARNING('[DEBUG] No backup files found to upload')
            )
            return
        
        try:
            # Test connection first
            self.stdout.write('[DEBUG] Testing WebDAV connection...')
            root_listing = client.ls("/")
            self.stdout.write(f'[DEBUG] WebDAV connection successful. Root listing: {len(root_listing)} items')
            
            # Ensure backups directory exists
            self.stdout.write('[DEBUG] Checking if backups directory exists...')
            try:
                backups_listing = client.ls("backups/")
                self.stdout.write(f'[DEBUG] Backups directory exists with {len(backups_listing)} items')
            except Exception as mkdir_e:
                self.stdout.write(f'[DEBUG] Backups directory not found: {mkdir_e}')
                self.stdout.write('[DEBUG] Creating backups directory...')
                client.mkdir("backups")
                self.stdout.write(
                    self.style.SUCCESS('[DEBUG] Created backups directory on Nextcloud')
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'[DEBUG] Connection error: {str(e)}')
            )
            return
        
        for backup_file in backup_files:
            filename = os.path.basename(backup_file)
            self.stdout.write(f'\n[DEBUG] === Processing backup file: {filename} ===')
            
            # Encrypt the backup file
            encrypted_file = f"{backup_file}.gpg"
            encrypted_filename = f"{filename}.gpg"
            remote_path = f'backups/{encrypted_filename}'
            
            self.stdout.write(f'[DEBUG] Paths:')
            self.stdout.write(f'[DEBUG]   Source file: {backup_file}')
            self.stdout.write(f'[DEBUG]   Encrypted file: {encrypted_file}')
            self.stdout.write(f'[DEBUG]   Remote path: {remote_path}')
            
            try:
                # Check GPG setup first
                self.stdout.write('[DEBUG] Checking GPG setup...')
                gpg_test_cmd = ['gpg', '--list-keys', 'lcsavb@gmail.com']
                gpg_test_result = subprocess.run(gpg_test_cmd, capture_output=True, text=True)
                
                if gpg_test_result.returncode == 0:
                    self.stdout.write('[DEBUG] GPG key found for lcsavb@gmail.com')
                else:
                    self.stdout.write(f'[DEBUG] GPG key check failed: {gpg_test_result.stderr}')
                    self.stdout.write('[DEBUG] Available GPG keys:')
                    list_keys_cmd = ['gpg', '--list-keys']
                    list_result = subprocess.run(list_keys_cmd, capture_output=True, text=True)
                    self.stdout.write(f'[DEBUG] {list_result.stdout}')
                
                # Encrypt the backup file using GPG
                self.stdout.write('[DEBUG] Starting GPG encryption...')
                encrypt_cmd = [
                    'gpg', '--trust-model', 'always', '--cipher-algo', 'AES256',
                    '--compress-algo', '2', '--encrypt', '-r', 'lcsavb@gmail.com',
                    '--output', encrypted_file, backup_file
                ]
                
                self.stdout.write(f'[DEBUG] GPG command: {" ".join(encrypt_cmd)}')
                result = subprocess.run(encrypt_cmd, capture_output=True, text=True)
                
                self.stdout.write(f'[DEBUG] GPG return code: {result.returncode}')
                self.stdout.write(f'[DEBUG] GPG stdout: {result.stdout}')
                self.stdout.write(f'[DEBUG] GPG stderr: {result.stderr}')
                
                if result.returncode != 0:
                    self.stdout.write(
                        self.style.ERROR(f'[DEBUG] Failed to encrypt {filename}: {result.stderr}')
                    )
                    continue
                
                # Check if encrypted file was created
                if os.path.exists(encrypted_file):
                    encrypted_size = os.path.getsize(encrypted_file)
                    self.stdout.write(f'[DEBUG] Encrypted file created successfully ({encrypted_size} bytes)')
                else:
                    self.stdout.write(
                        self.style.ERROR(f'[DEBUG] Encrypted file was not created: {encrypted_file}')
                    )
                    continue
                
                self.stdout.write(f'[DEBUG] Encrypted {filename} successfully')
                
                # Check if encrypted file already exists on Nextcloud
                self.stdout.write('[DEBUG] Checking if file exists on Nextcloud...')
                try:
                    existing_file = client.ls(remote_path)
                    self.stdout.write(f'[DEBUG] Encrypted file {encrypted_filename} already exists on Nextcloud')
                    self.stdout.write(f'[DEBUG] Existing file info: {existing_file}')
                except Exception as check_e:
                    self.stdout.write(f'[DEBUG] File does not exist on Nextcloud: {check_e}')
                    
                    # File doesn't exist, upload the encrypted version
                    self.stdout.write('[DEBUG] Starting upload to Nextcloud...')
                    try:
                        client.upload_file(encrypted_file, remote_path)
                        self.stdout.write(
                            self.style.SUCCESS(f'[DEBUG] Uploaded encrypted {encrypted_filename} to Nextcloud')
                        )
                    except Exception as upload_e:
                        self.stdout.write(
                            self.style.ERROR(f'[DEBUG] Upload failed: {upload_e}')
                        )
                        continue
                
                # Clean up local encrypted file after upload
                self.stdout.write('[DEBUG] Cleaning up local encrypted file...')
                if os.path.exists(encrypted_file):
                    os.remove(encrypted_file)
                    self.stdout.write(f'[DEBUG] Cleaned up local encrypted file {encrypted_filename}')
                else:
                    self.stdout.write(f'[DEBUG] Encrypted file already removed: {encrypted_file}')
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'[DEBUG] Failed to process {filename}: {str(e)}')
                )
                self.stdout.write(f'[DEBUG] Exception type: {type(e).__name__}')
                import traceback
                self.stdout.write(f'[DEBUG] Traceback: {traceback.format_exc()}')
                
                # Clean up encrypted file if it exists
                if os.path.exists(encrypted_file):
                    self.stdout.write(f'[DEBUG] Cleaning up failed encrypted file: {encrypted_file}')
                    os.remove(encrypted_file)
        
        self.stdout.write(self.style.SUCCESS('[DEBUG] Upload backup command completed'))