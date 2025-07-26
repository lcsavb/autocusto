from django.db import models
from medicos.models import Medico
from pacientes.models import Paciente
from django.conf import settings
from django.utils import timezone


# Clinic
class Clinica(models.Model):
    """
    Clinic model representing medical facilities where prescriptions are issued.
    
    Business Logic: Clinics can have multiple doctors and users. The Emissor model
    creates the doctor-clinic combinations that actually issue prescriptions.
    """
    # clinic_name
    nome_clinica = models.CharField(max_length=200)
    # clinic_cns (Brazilian national health system registration for clinic)
    cns_clinica = models.CharField(max_length=7, unique=True)
    # street_address
    logradouro = models.CharField(max_length=200)
    # street_number
    logradouro_num = models.CharField(max_length=6)
    # complement (address complement - currently unused)
    # complemento = models.CharField(max_length=20)
    # city
    cidade = models.CharField(max_length=30)
    # neighborhood
    bairro = models.CharField(max_length=30)
    # zip_code
    cep = models.CharField(max_length=9)
    # clinic_phone
    telefone_clinica = models.CharField(max_length=15)
    # doctors (doctors working at this clinic)
    medicos = models.ManyToManyField(Medico, through="Emissor", related_name="clinicas")
    # users (user accounts with access to this clinic)
    usuarios = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through="ClinicaUsuario", related_name="clinicas"
    )

    def __str__(self):
        return f"{self.nome_clinica}"
    
    def get_version_for_user(self, user):
        """Get the appropriate version of this clinic for a specific user"""
        try:
            # Check if user has a specific version assigned
            clinica_usuario = ClinicaUsuario.objects.get(clinica=self, usuario=user)
            if hasattr(clinica_usuario, 'active_version'):
                return clinica_usuario.active_version.version
        except ClinicaUsuario.DoesNotExist:
            pass
        
        # Return latest active version as fallback
        return self.versions.filter(status='active').order_by('-version_number').first()
    
    def create_new_version(self, user, data):
        """Create a new version of this clinic"""
        latest_version = self.versions.order_by('-version_number').first()
        new_version_number = (latest_version.version_number + 1) if latest_version else 1
        
        version = ClinicaVersion.objects.create(
            clinica=self,
            version_number=new_version_number,
            created_by=user,
            **data
        )
        
        # Automatically assign this version to the user who created it
        clinica_usuario = ClinicaUsuario.objects.filter(clinica=self, usuario=user).first()
        if clinica_usuario:
            ClinicaUsuarioVersion.objects.update_or_create(
                clinica_usuario=clinica_usuario,
                defaults={'version': version}
            )
        
        return version

    @classmethod
    def create_or_update_for_user(cls, user, doctor, clinic_data):
        """Create new clinic or new version for existing clinic"""
        # Validate required parameters
        if not user:
            raise ValueError("User is required")
        if not doctor:
            raise ValueError("Doctor is required")
        if not clinic_data:
            raise ValueError("Clinic data is required")
            
        cns = clinic_data['cns_clinica']
        
        # Check if clinic with this CNS already exists
        existing_clinic = cls.objects.filter(cns_clinica=cns).first()
        
        if existing_clinic:
            # Create new version for this user
            version_data = {
                'nome_clinica': clinic_data['nome_clinica'],
                'logradouro': clinic_data['logradouro'],
                'logradouro_num': clinic_data['logradouro_num'],
                'cidade': clinic_data['cidade'],
                'bairro': clinic_data['bairro'],
                'cep': clinic_data['cep'],
                'telefone_clinica': clinic_data['telefone_clinica'],
                'change_summary': f'Atualização por {user.email}'
            }
            
            existing_clinic.create_new_version(user, version_data)
            
            # Ensure user and doctor are connected to clinic
            existing_clinic.usuarios.add(user)
            existing_clinic.medicos.add(doctor)
            
            existing_clinic.was_created = False
            return existing_clinic
        else:
            # Create new clinic
            new_clinic = cls.objects.create(
                nome_clinica=clinic_data['nome_clinica'],
                cns_clinica=clinic_data['cns_clinica'],
                logradouro=clinic_data['logradouro'],
                logradouro_num=clinic_data['logradouro_num'],
                cidade=clinic_data['cidade'],
                bairro=clinic_data['bairro'],
                cep=clinic_data['cep'],
                telefone_clinica=clinic_data['telefone_clinica']
            )
            
            # Create initial version
            version_data = {
                'nome_clinica': clinic_data['nome_clinica'],
                'logradouro': clinic_data['logradouro'],
                'logradouro_num': clinic_data['logradouro_num'],
                'cidade': clinic_data['cidade'],
                'bairro': clinic_data['bairro'],
                'cep': clinic_data['cep'],
                'telefone_clinica': clinic_data['telefone_clinica'],
                'change_summary': 'Cadastro inicial da clínica'
            }
            
            ClinicaVersion.objects.create(
                clinica=new_clinic,
                created_by=user,
                version_number=1,
                status='active',
                **version_data
            )
            
            # Connect user and doctor
            new_clinic.usuarios.add(user)
            new_clinic.medicos.add(doctor)
            
            # Create version assignment for user
            clinica_usuario = ClinicaUsuario.objects.get(usuario=user, clinica=new_clinic)
            ClinicaUsuarioVersion.objects.create(
                clinica_usuario=clinica_usuario,
                version=new_clinic.versions.first()
            )
            
            new_clinic.was_created = True
            return new_clinic


# Issuer (doctor-clinic combination that can issue prescriptions)
class Emissor(models.Model):
    """
    Issuer model representing a doctor-clinic combination for prescription issuance.
    
    Business Logic: This model creates the specific doctor-clinic pairs that are
    authorized to issue prescriptions. One doctor can work at multiple clinics,
    and one clinic can have multiple doctors, creating multiple issuer combinations.
    """
    # doctor
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE)
    # clinic
    clinica = models.ForeignKey(Clinica, on_delete=models.CASCADE)
    # patients (patients served by this doctor-clinic combination)
    pacientes = models.ManyToManyField(
        Paciente,
        through="processos.Processo",
        through_fields=("emissor", "paciente"),
        related_name="emissores",
    )

    class Meta:
        # OPTIMIZATION: Composite index for efficient doctor-clinic lookups
        # This index makes queries like "find all issuers for this doctor at this clinic" fast
        # Before: Full table scan for medico+clinica combinations
        # After: Direct index lookup
        # Note: NO unique_together because versioning system allows multiple users
        # to have the same doctor-clinic combination with different versioned data
        indexes = [
            models.Index(fields=['medico', 'clinica'], name='emissor_medico_clinica_idx'),
        ]

    def __str__(self):
        # Issued by clinic: {clinic} and by doctor with CRM: {doctor}
        return (
            f"Emitido pela clínica: {self.clinica} e pelo médico com CRM: {self.medico}"
        )


# ClinicUser (intermediate model for clinic-user relationship)
class ClinicaUsuario(models.Model):
    """
    Intermediate model for Clinic-User many-to-many relationship.
    
    Design Note: Uses SET_NULL to preserve data integrity if either
    clinic or user records are deleted, maintaining audit trail.
    """
    # QUESTION - SHOULD THIS BE SET_NULL?
    # user
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    # clinic
    clinica = models.ForeignKey(Clinica, on_delete=models.SET_NULL, null=True)

    class Meta:
        # OPTIMIZATION: Indexes for efficient through table lookups
        # These make queries like "find all clinics for this user" fast
        # Before: Full table scan on ClinicaUsuario  
        # After: Direct index lookups
        indexes = [
            models.Index(fields=['usuario'], name='clinicausuario_usuario_idx'),
            models.Index(fields=['clinica'], name='clinicausuario_clinica_idx'),
        ]

    def __str__(self):
        # Clinic: {clinic} and User {user}
        return f"Clínica: {self.clinica} e Usuário {self.usuario}"


# ClinicVersion (versioned clinic data)
class ClinicaVersion(models.Model):
    """
    Versioned clinic data - all editable fields are stored here.
    Each edit creates a new version, allowing full history tracking
    and user-specific views of clinic data.
    """
    # Reference to master clinic record
    clinica = models.ForeignKey(Clinica, on_delete=models.CASCADE, related_name='versions')
    
    # Versionable fields (all editable clinic data)
    nome_clinica = models.CharField(max_length=200)
    logradouro = models.CharField(max_length=200)
    logradouro_num = models.CharField(max_length=6)
    cidade = models.CharField(max_length=30)
    bairro = models.CharField(max_length=30)
    cep = models.CharField(max_length=9)
    telefone_clinica = models.CharField(max_length=15)
    
    # Version metadata
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='clinic_versions_created'
    )
    created_at = models.DateTimeField(default=timezone.now)
    version_number = models.IntegerField()
    change_summary = models.TextField(blank=True, help_text="Summary of changes in this version")
    
    # Version status
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'Rascunho'),
            ('active', 'Ativo'), 
            ('archived', 'Arquivado'),
        ],
        default='active'
    )
    
    class Meta:
        unique_together = ['clinica', 'version_number']
        ordering = ['-version_number', '-created_at']
        verbose_name = 'Versão da Clínica'
        verbose_name_plural = 'Versões das Clínicas'
    
    def __str__(self):
        return f"{self.nome_clinica} (v{self.version_number})"


# ClinicUserVersion (which version each user sees)
class ClinicaUsuarioVersion(models.Model):
    """
    Links a user's access to a clinic with the specific version they work with.
    This ensures each user sees their own version of clinic data.
    """
    clinica_usuario = models.OneToOneField(
        ClinicaUsuario,
        on_delete=models.CASCADE,
        related_name='active_version'
    )
    version = models.ForeignKey(
        ClinicaVersion, 
        on_delete=models.PROTECT,  # Can't delete a version in use
        related_name='user_assignments'
    )
    assigned_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name = 'Versão Ativa do Usuário'
        verbose_name_plural = 'Versões Ativas dos Usuários'
    
    def __str__(self):
        return f"{self.clinica_usuario.usuario} - {self.version}"
