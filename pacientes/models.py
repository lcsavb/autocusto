from django.db import models
from django.conf import settings
from django.utils import timezone


# Patient
class Paciente(models.Model):
    """
    Patient model storing patient information for medical prescriptions.
    
    Security: Patients are linked to specific doctors through the usuarios (users)
    ManyToManyField, ensuring data access control and patient privacy.
    
    Data Privacy: Contains sensitive personal health information (PHI) including
    CPF (Brazilian tax ID), CNS (national health card), and medical data.
    """
    # patient_name
    nome_paciente = models.CharField(max_length=100)
    # age
    idade = models.CharField(max_length=100)
    # gender
    sexo = models.CharField(max_length=100)
    # mothers_name
    nome_mae = models.CharField(max_length=100)
    # incapable (legally incapacitated, requiring guardian consent)
    incapaz = models.BooleanField()
    # responsible_name (guardian name for incapacitated patients)
    nome_responsavel = models.CharField(max_length=100)
    # id_number (Brazilian RG - state ID document)
    rg = models.CharField(max_length=100)
    # weight
    peso = models.CharField(max_length=100)
    # height
    altura = models.CharField(max_length=100, default="1,70m")
    # ethnicity_choice (patient's self-declared ethnicity choice)
    escolha_etnia = models.CharField(max_length=100)
    # patient_cpf (Brazilian social security number - unique identifier)
    cpf_paciente = models.CharField(unique=True, max_length=14)
    # patient_cns (Brazilian national health card number)
    cns_paciente = models.CharField(max_length=100)
    # patient_email
    email_paciente = models.EmailField(null=True)
    # patient_city
    cidade_paciente = models.CharField(max_length=100)
    # patient_address
    end_paciente = models.CharField(max_length=100)
    # patient_zip_code
    cep_paciente = models.CharField(max_length=100)
    # patient_phone1
    telefone1_paciente = models.CharField(max_length=100)
    # patient_phone2
    telefone2_paciente = models.CharField(max_length=100)
    # ethnicity (final ethnicity classification)
    etnia = models.CharField(max_length=100)
    # users (doctors who have access to this patient's data)
    usuarios = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="pacientes"
    )

    def __str__(self):
        return f"{self.nome_paciente}"
    
    def get_name_for_user(self, user):
        """Get the patient name as seen by a specific user (from their version)"""
        version = self.get_version_for_user(user)
        return version.nome_paciente if version else self.nome_paciente
    
    @classmethod
    def get_patients_for_user_search(cls, user, search_term=None):
        """
        Get patients for a user with their versioned data, optionally filtered by search term.
        Returns a list of tuples: (patient, version) where version contains the user's data.
        """
        user_patients = user.pacientes.all()
        results = []
        
        for patient in user_patients:
            version = patient.get_version_for_user(user)
            if version:
                # If search term provided, check if it matches versioned data
                if search_term:
                    if (search_term.lower() in version.nome_paciente.lower() or 
                        search_term in patient.cpf_paciente):  # CPF is in master record
                        results.append((patient, version))
                else:
                    results.append((patient, version))
            else:
                # Fallback to master record data
                if search_term:
                    if (search_term.lower() in patient.nome_paciente.lower() or 
                        search_term in patient.cpf_paciente):
                        results.append((patient, None))
                else:
                    results.append((patient, None))
        
        return results
    
    def get_version_for_user(self, user):
        """Get the appropriate version of this patient for a specific user"""
        try:
            # Check if user has a specific version assigned
            patient_usuario = self.usuarios.through.objects.get(paciente=self, usuario=user)
            if hasattr(patient_usuario, 'active_version'):
                return patient_usuario.active_version.version
        except self.usuarios.through.DoesNotExist:
            pass
        
        # Return latest active version as fallback
        return self.versions.filter(status='active').order_by('-version_number').first()
    
    def create_new_version(self, user, data):
        """Create a new version of this patient"""
        latest_version = self.versions.order_by('-version_number').first()
        new_version_number = (latest_version.version_number + 1) if latest_version else 1
        
        version = PacienteVersion.objects.create(
            paciente=self,
            version_number=new_version_number,
            created_by=user,
            **data
        )
        
        # Automatically assign this version to the user who created it
        patient_usuario = self.usuarios.through.objects.filter(paciente=self, usuario=user).first()
        if patient_usuario:
            PacienteUsuarioVersion.objects.update_or_create(
                paciente_usuario=patient_usuario,
                defaults={'version': version}
            )
        
        return version

    @classmethod
    def create_or_update_for_user(cls, user, patient_data):
        """Create new patient or new version for existing patient"""
        # Validate required parameters
        if not user:
            raise ValueError("User is required")
        if not patient_data:
            raise ValueError("Patient data is required")
            
        cpf = patient_data['cpf_paciente']
        
        # Check if patient with this CPF already exists
        existing_patient = cls.objects.filter(cpf_paciente=cpf).first()
        
        if existing_patient:
            # Create new version for this user
            version_data = {
                'nome_paciente': patient_data['nome_paciente'],
                'idade': patient_data.get('idade', ''),
                'sexo': patient_data.get('sexo', ''),
                'nome_mae': patient_data['nome_mae'],
                'incapaz': patient_data['incapaz'],
                'nome_responsavel': patient_data['nome_responsavel'],
                'rg': patient_data.get('rg', ''),
                'peso': patient_data['peso'],
                'altura': patient_data['altura'],
                'escolha_etnia': patient_data.get('escolha_etnia', ''),
                'cns_paciente': patient_data.get('cns_paciente', ''),
                'email_paciente': patient_data.get('email_paciente'),
                'cidade_paciente': patient_data.get('cidade_paciente', ''),
                'end_paciente': patient_data['end_paciente'],
                'cep_paciente': patient_data.get('cep_paciente', ''),
                'telefone1_paciente': patient_data['telefone1_paciente'],
                'telefone2_paciente': patient_data['telefone2_paciente'],
                'etnia': patient_data['etnia'],
                'change_summary': f'Atualização por {user.email}'
            }
            
            existing_patient.create_new_version(user, version_data)
            
            # Ensure user is connected to patient
            existing_patient.usuarios.add(user)
            
            existing_patient.was_created = False
            return existing_patient
        else:
            # Create new patient
            new_patient = cls.objects.create(
                nome_paciente=patient_data['nome_paciente'],
                cpf_paciente=patient_data['cpf_paciente'],
                idade=patient_data.get('idade', ''),
                sexo=patient_data.get('sexo', ''),
                nome_mae=patient_data['nome_mae'],
                incapaz=patient_data['incapaz'],
                nome_responsavel=patient_data['nome_responsavel'],
                rg=patient_data.get('rg', ''),
                peso=patient_data['peso'],
                altura=patient_data['altura'],
                escolha_etnia=patient_data.get('escolha_etnia', ''),
                cns_paciente=patient_data.get('cns_paciente', ''),
                email_paciente=patient_data.get('email_paciente'),
                cidade_paciente=patient_data.get('cidade_paciente', ''),
                end_paciente=patient_data['end_paciente'],
                cep_paciente=patient_data.get('cep_paciente', ''),
                telefone1_paciente=patient_data['telefone1_paciente'],
                telefone2_paciente=patient_data['telefone2_paciente'],
                etnia=patient_data['etnia']
            )
            
            # Create initial version
            version_data = {
                'nome_paciente': patient_data['nome_paciente'],
                'idade': patient_data.get('idade', ''),
                'sexo': patient_data.get('sexo', ''),
                'nome_mae': patient_data['nome_mae'],
                'incapaz': patient_data['incapaz'],
                'nome_responsavel': patient_data['nome_responsavel'],
                'rg': patient_data.get('rg', ''),
                'peso': patient_data['peso'],
                'altura': patient_data['altura'],
                'escolha_etnia': patient_data.get('escolha_etnia', ''),
                'cns_paciente': patient_data.get('cns_paciente', ''),
                'email_paciente': patient_data.get('email_paciente'),
                'cidade_paciente': patient_data.get('cidade_paciente', ''),
                'end_paciente': patient_data['end_paciente'],
                'cep_paciente': patient_data.get('cep_paciente', ''),
                'telefone1_paciente': patient_data['telefone1_paciente'],
                'telefone2_paciente': patient_data['telefone2_paciente'],
                'etnia': patient_data['etnia'],
                'change_summary': 'Cadastro inicial do paciente'
            }
            
            PacienteVersion.objects.create(
                paciente=new_patient,
                created_by=user,
                version_number=1,
                status='active',
                **version_data
            )
            
            # Connect user
            new_patient.usuarios.add(user)
            
            # Create version assignment for user
            patient_usuario = new_patient.usuarios.through.objects.get(usuario=user, paciente=new_patient)
            PacienteUsuarioVersion.objects.create(
                paciente_usuario=patient_usuario,
                version=new_patient.versions.first()
            )
            
            new_patient.was_created = True
            return new_patient


# PacienteVersion (versioned patient data)
class PacienteVersion(models.Model):
    """
    Versioned patient data - all editable fields are stored here.
    Each edit creates a new version, allowing full history tracking
    and user-specific views of patient data.
    """
    # Reference to master patient record
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='versions')
    
    # Versionable fields (all editable patient data except CPF)
    nome_paciente = models.CharField(max_length=100)
    idade = models.CharField(max_length=100)
    sexo = models.CharField(max_length=100)
    nome_mae = models.CharField(max_length=100)
    incapaz = models.BooleanField()
    nome_responsavel = models.CharField(max_length=100)
    rg = models.CharField(max_length=100)
    peso = models.CharField(max_length=100)
    altura = models.CharField(max_length=100, default="1,70m")
    escolha_etnia = models.CharField(max_length=100)
    cns_paciente = models.CharField(max_length=100)
    email_paciente = models.EmailField(null=True, blank=True)
    cidade_paciente = models.CharField(max_length=100)
    end_paciente = models.CharField(max_length=100)
    cep_paciente = models.CharField(max_length=100)
    telefone1_paciente = models.CharField(max_length=100)
    telefone2_paciente = models.CharField(max_length=100)
    etnia = models.CharField(max_length=100)
    
    # Version metadata
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='patient_versions_created'
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
        unique_together = ['paciente', 'version_number']
        ordering = ['-version_number', '-created_at']
        verbose_name = 'Versão do Paciente'
        verbose_name_plural = 'Versões dos Pacientes'
    
    def __str__(self):
        return f"{self.nome_paciente} (v{self.version_number})"


# PacienteUsuarioVersion (which version each user sees)
class PacienteUsuarioVersion(models.Model):
    """
    Links a user's access to a patient with the specific version they work with.
    This ensures each user sees their own version of patient data.
    """
    paciente_usuario = models.OneToOneField(
        'Paciente_usuarios',  # Django's auto-generated through table
        on_delete=models.CASCADE,
        related_name='active_version'
    )
    version = models.ForeignKey(
        PacienteVersion, 
        on_delete=models.PROTECT,  # Can't delete a version in use
        related_name='user_assignments'
    )
    assigned_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name = 'Versão Ativa do Usuário (Paciente)'
        verbose_name_plural = 'Versões Ativas dos Usuários (Pacientes)'
    
    def __str__(self):
        return f"{self.paciente_usuario.usuario} - {self.version}"
