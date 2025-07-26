from django.db import models
from django.conf import settings

# Brazilian States choices
BRAZILIAN_STATES = [
    ('AC', 'Acre'),
    ('AL', 'Alagoas'),
    ('AP', 'Amapá'),
    ('AM', 'Amazonas'),
    ('BA', 'Bahia'),
    ('CE', 'Ceará'),
    ('DF', 'Distrito Federal'),
    ('ES', 'Espírito Santo'),
    ('GO', 'Goiás'),
    ('MA', 'Maranhão'),
    ('MT', 'Mato Grosso'),
    ('MS', 'Mato Grosso do Sul'),
    ('MG', 'Minas Gerais'),
    ('PA', 'Pará'),
    ('PB', 'Paraíba'),
    ('PR', 'Paraná'),
    ('PE', 'Pernambuco'),
    ('PI', 'Piauí'),
    ('RJ', 'Rio de Janeiro'),
    ('RN', 'Rio Grande do Norte'),
    ('RS', 'Rio Grande do Sul'),
    ('RO', 'Rondônia'),
    ('RR', 'Roraima'),
    ('SC', 'Santa Catarina'),
    ('SP', 'São Paulo'),
    ('SE', 'Sergipe'),
    ('TO', 'Tocantins'),
]

# Medical Specialties choices
MEDICAL_SPECIALTIES = [
    ('ALERGIA_IMUNOLOGIA', 'Alergia e Imunologia'),
    ('ANESTESIOLOGIA', 'Anestesiologia'),
    ('ANGIOLOGIA', 'Angiologia'),
    ('CARDIOLOGIA', 'Cardiologia'),
    ('CIRURGIA_CARDIOVASCULAR', 'Cirurgia Cardiovascular'),
    ('CIRURGIA_MAO', 'Cirurgia da Mão'),
    ('CIRURGIA_CABECA_PESCOCO', 'Cirurgia de Cabeça e Pescoço'),
    ('CIRURGIA_APARELHO_DIGESTIVO', 'Cirurgia do Aparelho Digestivo'),
    ('CIRURGIA_GERAL', 'Cirurgia Geral'),
    ('CIRURGIA_PEDIATRICA', 'Cirurgia Pediátrica'),
    ('CIRURGIA_PLASTICA', 'Cirurgia Plástica'),
    ('CIRURGIA_TORACICA', 'Cirurgia Torácica'),
    ('CIRURGIA_VASCULAR', 'Cirurgia Vascular'),
    ('CLINICA_MEDICA', 'Clínica Médica'),
    ('COLOPROCTOLOGIA', 'Coloproctologia'),
    ('DERMATOLOGIA', 'Dermatologia'),
    ('ENDOCRINOLOGIA', 'Endocrinologia e Metabologia'),
    ('ENDOSCOPIA', 'Endoscopia'),
    ('GASTROENTEROLOGIA', 'Gastroenterologia'),
    ('GENETICA_MEDICA', 'Genética Médica'),
    ('GERIATRIA', 'Geriatria'),
    ('GINECOLOGIA_OBSTETRICIA', 'Ginecologia e Obstetrícia'),
    ('HEMATOLOGIA', 'Hematologia e Hemoterapia'),
    ('HOMEOPATIA', 'Homeopatia'),
    ('INFECTOLOGIA', 'Infectologia'),
    ('MASTOLOGIA', 'Mastologia'),
    ('MEDICINA_FAMILIA', 'Medicina de Família e Comunidade'),
    ('MEDICINA_EMERGENCIA', 'Medicina de Emergência'),
    ('MEDICINA_TRABALHO', 'Medicina do Trabalho'),
    ('MEDICINA_TRAFEGO', 'Medicina do Tráfego'),
    ('MEDICINA_ESPORTIVA', 'Medicina Esportiva'),
    ('MEDICINA_FISICA_REABILITACAO', 'Medicina Física e Reabilitação'),
    ('MEDICINA_INTENSIVA', 'Medicina Intensiva'),
    ('MEDICINA_LEGAL', 'Medicina Legal e Perícia Médica'),
    ('MEDICINA_NUCLEAR', 'Medicina Nuclear'),
    ('MEDICINA_PREVENTIVA', 'Medicina Preventiva e Social'),
    ('NEFROLOGIA', 'Nefrologia'),
    ('NEUROCIRURGIA', 'Neurocirurgia'),
    ('NEUROLOGIA', 'Neurologia'),
    ('NUTROLOGIA', 'Nutrologia'),
    ('OBSTETRICIA', 'Obstetrícia'),
    ('OFTALMOLOGIA', 'Oftalmologia'),
    ('ORTOPEDIA_TRAUMATOLOGIA', 'Ortopedia e Traumatologia'),
    ('OTORRINOLARINGOLOGIA', 'Otorrinolaringologia'),
    ('PATOLOGIA', 'Patologia'),
    ('PATOLOGIA_CLINICA', 'Patologia Clínica/Medicina Laboratorial'),
    ('PEDIATRIA', 'Pediatria'),
    ('PNEUMOLOGIA', 'Pneumologia'),
    ('PSIQUIATRIA', 'Psiquiatria'),
    ('RADIOLOGIA', 'Radiologia e Diagnóstico por Imagem'),
    ('RADIOTERAPIA', 'Radioterapia'),
    ('REUMATOLOGIA', 'Reumatologia'),
    ('TOXICOLOGIA', 'Toxicologia Médica'),
    ('UROLOGIA', 'Urologia'),
    ('OUTRA', 'Outra'),
]


# Doctor
class Medico(models.Model):
    """
    Doctor model storing medical professional information.
    
    Business Logic: Each doctor has unique CRM (medical license) and CNS numbers.
    The relationship with users allows multiple user accounts per doctor and
    multiple doctors per user account (for complex medical practices).
    """
    # doctor_name
    nome_medico = models.CharField(max_length=200)
    # doctor_crm (Brazilian medical license number) - unique with state
    crm_medico = models.CharField(max_length=10, null=True, blank=True)
    # doctor_cns (Brazilian national health system registration)
    cns_medico = models.CharField(max_length=15, unique=True, null=True, blank=True)
    # doctor_state (Brazilian state where CRM is registered)
    estado = models.CharField(
        max_length=2, 
        choices=BRAZILIAN_STATES, 
        null=True, 
        blank=True,
        verbose_name="Estado do CRM"
    )
    # doctor_specialty
    especialidade = models.CharField(
        max_length=50, 
        choices=MEDICAL_SPECIALTIES, 
        null=True, 
        blank=True,
        verbose_name="Especialidade Médica"
    )
    # users (user accounts linked to this doctor)
    usuarios = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through="MedicoUsuario", related_name="medicos"
    )

    class Meta:
        unique_together = [['crm_medico', 'estado']]
        verbose_name = "Médico"
        verbose_name_plural = "Médicos"

    def __str__(self):
        if self.crm_medico and self.estado:
            return f"{self.crm_medico}/{self.estado}"
        return self.nome_medico or "Médico sem CRM"


# DoctorUser (intermediate model for doctor-user relationship)
class MedicoUsuario(models.Model):
    """
    Intermediate model for Doctor-User many-to-many relationship.
    
    Design Note: Uses SET_NULL to preserve data integrity if either
    doctor or user records are deleted, maintaining audit trail.
    """
    # QUESTION - SHOULD THIS BE SET_NULL?
    # user
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    # doctor
    medico = models.ForeignKey(Medico, on_delete=models.SET_NULL, null=True)

    class Meta:
        # OPTIMIZATION: Indexes for efficient through table lookups
        # These make queries like "find all doctors for this user" fast
        # Before: Full table scan on MedicoUsuario
        # After: Direct index lookups
        indexes = [
            models.Index(fields=['usuario'], name='medicousuario_usuario_idx'),
            models.Index(fields=['medico'], name='medicousuario_medico_idx'),
        ]

    def __str__(self):
        # Doctor: {doctor} and User {user}
        return f"Médico: {self.medico} e Usuário {self.usuario}"
