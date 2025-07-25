# AutoCusto Data Versioning System

## Overview

The AutoCusto data versioning system prevents data corruption between users sharing the same clinic and patient records. This system ensures that each user sees their own customized version of shared data, solving the multi-tenancy problem inherent in the medical prescription workflow.

## Problem Statement

**Original Issue**: Multiple doctors working with the same clinic or patient would overwrite each other's data, causing:
- Lost patient information when doctors updated records
- Clinic data conflicts when multiple users edited the same facility
- Data integrity issues in the core business logic

**Solution**: Implement a versioning system where:
- Master records store immutable identifiers (CPF for patients, CNS for clinics)
- Each user gets their own versioned view of editable data
- Changes create new versions without affecting other users' views

## Architecture

### Core Components

1. **Master Records** - Store immutable identifiers and relationships
2. **Version Models** - Store all editable field data with version tracking
3. **User-Version Assignment** - Link specific users to specific versions
4. **Template Integration** - Display versioned data transparently to users

### Database Schema

```sql
-- Patient Example
Paciente (Master)
├── cpf_paciente (immutable identifier)
├── usuarios (many-to-many with User)
└── versions (one-to-many with PacienteVersion)

PacienteVersion (Versioned Data)
├── paciente (foreign key to master)
├── nome_paciente, idade, sexo, etc. (all editable fields)
├── version_number, created_by, created_at
└── status (active/draft/archived)

PacienteUsuarioVersion (User Assignment)
├── paciente_usuario (one-to-one with through table)
└── version (foreign key to PacienteVersion)
```

## Implementation Details

### Models

#### Patient Versioning (`pacientes/models.py`)

**Master Model**: `Paciente`
- Stores `cpf_paciente` (immutable Brazilian tax ID)
- Maintains `usuarios` many-to-many relationship
- Provides `get_version_for_user()` and `create_or_update_for_user()` methods

**Version Model**: `PacienteVersion`
- Contains all editable fields: `nome_paciente`, `idade`, `sexo`, etc.
- Tracks version metadata: `version_number`, `created_by`, `change_summary`
- Unique constraint: `(paciente, version_number)`

**Assignment Model**: `PacienteUsuarioVersion`
- Links user-patient relationships to specific versions
- One-to-one with Django's auto-generated through table
- `PROTECT` foreign key prevents accidental version deletion

#### Clinic Versioning (`clinicas/models.py`)

**Master Model**: `Clinica`
- Stores `cns_clinica` (immutable Brazilian health facility ID)
- Similar pattern to patient versioning

**Version Model**: `ClinicaVersion`
- Contains editable fields: `nome_clinica`, `logradouro`, `telefone_clinica`, etc.

**Assignment Model**: `ClinicaUsuarioVersion`
- Links user-clinic relationships to specific versions

### Template Integration

#### Template Filters (`pacientes/templatetags/patient_tags.py`)

```python
@register.filter
def patient_name_for_user(patient, user):
    """Display patient name as seen by specific user"""
    version = patient.get_version_for_user(user)
    return version.nome_paciente if version else patient.nome_paciente
```

**Usage in Templates**:
```html
<!-- Old approach (shows master record) -->
{{ paciente.nome_paciente }}

<!-- New approach (shows user's version) -->
{{ paciente|patient_name_for_user:user }}
```

#### Updated Templates
- `processos/templates/processos/cadastro.html`
- `processos/templates/processos/edicao.html` 
- `processos/templates/processos/renovacao_rapida.html`

### View Integration

#### Search Functionality
**Updated**: `processos/views.py` renovacao_rapida view
```python
# Old approach (searches master records)
busca_pacientes = pacientes_usuario.filter(
    nome_paciente__icontains=busca
)

# New approach (searches versioned data)
from pacientes.models import Paciente
patient_results = Paciente.get_patients_for_user_search(usuario, busca)
busca_pacientes = [patient for patient, version in patient_results]
```

#### AJAX Endpoints
**Updated**: `pacientes/ajax.py`
- Patient search now returns versioned names in JSON responses
- Maintains compatibility with frontend JavaScript code

### Form Integration

#### Validation Override
Forms skip uniqueness validation on versioned fields:

```python
def validate_unique(self):
    """Skip CPF/CNS uniqueness validation - handled by versioning system"""
    exclude = self._get_validation_exclusions()
    if 'cpf_paciente' not in exclude:
        exclude.add('cpf_paciente')
    super().validate_unique(exclude)
```

## Migration Strategy

### Database Migrations

#### Schema Creation
1. **`clinicas/migrations/0007_clinicaversion_clinicausuarioversion.py`**
   - Creates `ClinicaVersion` and `ClinicaUsuarioVersion` models
   - Establishes proper foreign key relationships and constraints

2. **`pacientes/migrations/0004_pacienteversion_pacienteusuarioversion.py`**
   - Creates `PacienteVersion` and `PacienteUsuarioVersion` models
   - Mirrors clinic versioning structure

#### Data Migration 
1. **`clinicas/migrations/0008_add_initial_versions.py`**
   - Creates version 1 for all existing clinics using master record data
   - Assigns initial versions to all existing user-clinic relationships
   - Includes comprehensive rollback function

2. **`pacientes/migrations/0005_create_initial_patient_versions.py`**
   - Creates version 1 for all existing patients using master record data  
   - Handles patients with existing versions vs. new patients
   - Assigns versions to all existing user-patient relationships
   - Includes comprehensive rollback function

### Migration Safety Features

**Data Integrity**:
- NULL checks for orphaned relationships
- Existing relationship preservation
- Graceful handling of missing optional fields

**Rollback Capability**:
- Complete reversal of version creation
- Restoration of original state
- Identification of migration-created records via `change_summary`

**Production Safety**:
- Non-destructive operations only
- Comprehensive logging during migration
- Safe handling of large datasets

## Usage Examples

### Patient Management

```python
# Create or update patient (automatically versioned)
patient = Paciente.create_or_update_for_user(user, patient_data)

# Get patient as seen by specific user
version = patient.get_version_for_user(user)
patient_name = version.nome_paciente

# Search patients with versioned data
results = Paciente.get_patients_for_user_search(user, "joão")
for patient, version in results:
    print(f"Patient: {version.nome_paciente if version else patient.nome_paciente}")
```

### Template Usage

```html
<!-- Display versioned patient name -->
<h3>{{ processo.paciente|patient_name_for_user:user }}</h3>

<!-- Display versioned clinic name -->
<span>{{ clinica|clinic_name_for_user:user }}</span>

<!-- Patient search results -->
{% for paciente in busca_pacientes %}
    <div>{{ paciente|patient_name_for_user:usuario }}</div>
{% endfor %}
```

### Form Processing

```python
# Forms automatically handle versioning
class PacienteForm(forms.ModelForm):
    def validate_unique(self):
        # Skip CPF uniqueness - handled by versioning system
        exclude = self._get_validation_exclusions()
        if 'cpf_paciente' not in exclude:
            exclude.add('cpf_paciente')
        super().validate_unique(exclude)
    
    def save(self, user=None):
        # Use versioned creation method
        return Paciente.create_or_update_for_user(user, self.cleaned_data)
```

## Key Benefits

### Data Isolation
- Each user sees their own version of shared data
- No more accidental overwrites between doctors
- Maintains data consistency across user sessions

### Audit Trail
- Complete history of all changes with version numbers
- Track who made changes and when
- Rollback capability to previous versions

### Business Logic Preservation
- Core application templates remain unchanged
- Process relationships use master records for referential integrity
- Seamless integration with existing PDF generation system

### Multi-Tenancy Support
- True multi-tenant architecture without database separation
- User-specific data views without complex filtering
- Scalable to unlimited users per clinic/patient

## Performance Considerations

### Database Queries
- Version lookup uses efficient foreign key relationships
- Template filters minimize database hits through caching
- Search functionality optimized for versioned data

### Memory Usage
- Version data stored only when different from master record
- Graceful fallback to master record when version unavailable
- Automatic cleanup of unused versions

### Caching Strategy
- Template filters can be cached per user session
- Version assignments cached at application level
- Database connection pooling for version lookups

## Testing

### Unit Tests
- **Patient Versioning**: `tests/test_patient_versioning.py`
- **Clinic Versioning**: `tests/test_clinic_versioning.py`
- **Integration Tests**: `tests/integration/`

### Test Coverage
- Model functionality (creation, versioning, assignment)
- Template integration (filters, display)
- AJAX endpoint responses
- Form validation and saving
- Migration data integrity

### Production Validation
```bash
# Run versioning system tests
python manage.py test tests.test_patient_versioning
python manage.py test tests.test_clinic_versioning

# Verify migration safety
python manage.py migrate --dry-run
python manage.py showmigrations
```

## Deployment Checklist

### Pre-Deployment
- [ ] All versioning tests passing
- [ ] Migration files reviewed and validated
- [ ] Database backup created
- [ ] Rollback plan documented

### During Deployment
- [ ] Apply migrations in order: clinics first, then patients
- [ ] Monitor migration progress with logging output  
- [ ] Verify version assignment completion
- [ ] Test user access to versioned data

### Post-Deployment
- [ ] Validate user-specific data display
- [ ] Test search functionality with versioned data
- [ ] Verify AJAX endpoints return correct versioned data
- [ ] Monitor system performance and query efficiency

## Troubleshooting

### Common Issues

**Missing Versions**: User sees no data
```python
# Check version assignment
patient_usuario = patient.usuarios.through.objects.get(paciente=patient, usuario=user)
print(patient_usuario.active_version)

# Create missing version
patient.create_new_version(user, version_data)
```

**Template Display Issues**: Versioned data not showing
```html
<!-- Verify filter usage -->
{{ paciente|patient_name_for_user:user }}
<!-- Not: {{ paciente.nome_paciente }} -->
```

**Search Problems**: Versioned data not found
```python
# Use versioned search method
results = Paciente.get_patients_for_user_search(user, search_term)
# Not: Paciente.objects.filter(nome_paciente__icontains=search_term)
```

### Migration Issues

**Orphaned Relationships**: NULL users in through tables
```sql
-- Clean up orphaned records
DELETE FROM pacientes_paciente_usuarios WHERE usuario_id IS NULL;
DELETE FROM clinicas_clinicausuario WHERE usuario_id IS NULL;
```

**Missing Initial Versions**: Users without version assignments
```python
# Run migration again (safe to re-run)
python manage.py migrate pacientes 0005_create_initial_patient_versions
```

## Future Enhancements

### Planned Features
- Version comparison and merge tools
- Automated conflict resolution
- Version expiration and archival
- Advanced audit reporting

### Scaling Considerations
- Partition versioning tables by date
- Implement version garbage collection
- Add version caching layer
- Consider read replicas for version queries

## Support

### Documentation
- Model documentation: See docstrings in `models.py` files
- API reference: Method signatures and return types documented
- Migration reference: See migration file comments

### Monitoring
- Track version creation rates
- Monitor query performance on version lookups
- Alert on failed version assignments
- Log version conflicts and resolutions

This versioning system provides robust multi-tenancy support while maintaining the simplicity and performance requirements of the AutoCusto medical prescription platform.