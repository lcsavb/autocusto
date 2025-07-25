"""
Management command to check for orphaned versions without proper assignments.

This helps monitor data integrity and detect when version creation succeeded
but assignment failed.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from pacientes.models import Paciente, PacienteVersion, PacienteUsuarioVersion
from clinicas.models import Clinica, ClinicaVersion, ClinicaUsuarioVersion

User = get_user_model()


class Command(BaseCommand):
    help = 'Check for orphaned versions without proper user assignments'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Attempt to fix orphaned versions by creating missing assignments',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed information about each orphaned version',
        )

    def handle(self, *args, **options):
        self.check_patient_versions(options)
        self.check_clinic_versions(options)

    def check_patient_versions(self, options):
        self.stdout.write(self.style.SUCCESS('\n=== Checking Patient Versions ==='))
        
        # Find all patient versions
        all_versions = PacienteVersion.objects.select_related('paciente', 'created_by').all()
        orphaned_versions = []
        
        for version in all_versions:
            # Check if this version has any assignments
            assignments = PacienteUsuarioVersion.objects.filter(version=version)
            
            if not assignments.exists():
                orphaned_versions.append(version)
                
                if options['verbose']:
                    self.stdout.write(
                        self.style.WARNING(
                            f"🔍 Orphaned Patient Version {version.version_number}:\n"
                            f"   Patient: {version.paciente.cpf_paciente}\n"
                            f"   Name: '{version.nome_paciente}'\n"
                            f"   Created By: {version.created_by.email if version.created_by else 'Unknown'}\n"
                            f"   Created At: {version.created_at}\n"
                        )
                    )
                    
                if options['fix']:
                    self.fix_orphaned_patient_version(version)
        
        if orphaned_versions:
            self.stdout.write(
                self.style.ERROR(f"❌ Found {len(orphaned_versions)} orphaned patient versions")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"✅ No orphaned patient versions found")
            )

    def check_clinic_versions(self, options):
        self.stdout.write(self.style.SUCCESS('\n=== Checking Clinic Versions ==='))
        
        # Find all clinic versions
        all_versions = ClinicaVersion.objects.select_related('clinica', 'created_by').all()
        orphaned_versions = []
        
        for version in all_versions:
            # Check if this version has any assignments
            assignments = ClinicaUsuarioVersion.objects.filter(version=version)
            
            if not assignments.exists():
                orphaned_versions.append(version)
                
                if options['verbose']:
                    self.stdout.write(
                        self.style.WARNING(
                            f"🔍 Orphaned Clinic Version {version.version_number}:\n"
                            f"   Clinic: {version.clinica.cns_clinica}\n"
                            f"   Name: '{version.nome_clinica}'\n"
                            f"   Created By: {version.created_by.email if version.created_by else 'Unknown'}\n"
                            f"   Created At: {version.created_at}\n"
                        )
                    )
                    
                if options['fix']:
                    self.fix_orphaned_clinic_version(version)
        
        if orphaned_versions:
            self.stdout.write(
                self.style.ERROR(f"❌ Found {len(orphaned_versions)} orphaned clinic versions")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"✅ No orphaned clinic versions found")
            )

    def fix_orphaned_patient_version(self, version):
        """Attempt to fix an orphaned patient version"""
        try:
            # Find the user who created this version
            creator = version.created_by
            if not creator:
                self.stdout.write(
                    self.style.ERROR(f"❌ Cannot fix version {version.version_number} - no creator info")
                )
                return
            
            # Check if creator has relationship with patient
            patient_usuario = version.paciente.usuarios.through.objects.filter(
                paciente=version.paciente, 
                usuario=creator
            ).first()
            
            if patient_usuario:
                # Create the missing assignment
                assignment, created = PacienteUsuarioVersion.objects.update_or_create(
                    paciente_usuario=patient_usuario,
                    defaults={'version': version}
                )
                
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✅ Fixed: Created assignment for patient version {version.version_number} "
                            f"to user {creator.email}"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f"⚠️  Updated existing assignment for patient version {version.version_number}"
                        )
                    )
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f"❌ Cannot fix version {version.version_number} - creator {creator.email} "
                        f"has no relationship with patient {version.paciente.cpf_paciente}"
                    )
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error fixing patient version {version.version_number}: {e}")
            )

    def fix_orphaned_clinic_version(self, version):
        """Attempt to fix an orphaned clinic version"""
        try:
            # Find the user who created this version
            creator = version.created_by
            if not creator:
                self.stdout.write(
                    self.style.ERROR(f"❌ Cannot fix version {version.version_number} - no creator info")
                )
                return
            
            # Check if creator has relationship with clinic
            from clinicas.models import ClinicaUsuario
            clinic_usuario = ClinicaUsuario.objects.filter(
                clinica=version.clinica, 
                usuario=creator
            ).first()
            
            if clinic_usuario:
                # Create the missing assignment
                assignment, created = ClinicaUsuarioVersion.objects.update_or_create(
                    clinica_usuario=clinic_usuario,
                    defaults={'version': version}
                )
                
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✅ Fixed: Created assignment for clinic version {version.version_number} "
                            f"to user {creator.email}"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f"⚠️  Updated existing assignment for clinic version {version.version_number}"
                        )
                    )
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f"❌ Cannot fix version {version.version_number} - creator {creator.email} "
                        f"has no relationship with clinic {version.clinica.cns_clinica}"
                    )
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error fixing clinic version {version.version_number}: {e}")
            )