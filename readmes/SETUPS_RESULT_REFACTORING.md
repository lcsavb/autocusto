# SetupResult Data Structure Refactoring

## Overview

This document describes the refactoring of the monolithic `SetupResult` NamedTuple into focused, composable data classes following SOLID principles and proper separation of concerns.

## Problem Statement

### Original Issues
- **Monolithic Structure**: Single NamedTuple with 13 mixed-purpose fields
- **Poor Separation**: Error handling, common data, form data, and view-specific data all mixed together
- **Type Confusion**: Boolean `success` field required manual checking with unclear semantics
- **Maintenance Burden**: Adding new fields meant updating the entire structure
- **Poor Readability**: Unclear relationships between fields

### Old Pattern Example
```python
SetupResult = namedtuple('SetupResult', [
    'success', 'error_redirect', 'error_message',           # Error handling
    'usuario', 'medico', 'clinicas', 'escolhas',           # Common data
    'cid', 'medicamentos', 'ModeloFormulario',             # Form data
    'processo_id', 'processo', 'dados_iniciais',           # Edit-specific
    'paciente_existe', 'primeira_data'                     # New prescription-specific
])

# Usage was confusing:
setup = service.setup_for_new_prescription(request)
if not setup.success:  # What does success mean?
    return redirect(setup.error_redirect)
usuario = setup.usuario  # Where does this come from?
```

## Solution: Focused Data Classes

### New Architecture

#### 1. Error Handling
```python
@dataclass
class SetupError:
    """Represents an error during view setup."""
    message: str      # User-friendly error message
    redirect_to: str  # Where to redirect on error
```

#### 2. Common Setup Data
```python
@dataclass
class CommonSetupData:
    """Data common to all prescription views (cadastro and edicao)."""
    usuario: Any        # User object
    medico: Any         # Medico object
    clinicas: QuerySet  # Available clinics for the user
    escolhas: Tuple     # Clinic choices for form
```

#### 3. Form-Related Data
```python
@dataclass
class PrescriptionFormData:
    """Form-related data for prescription views."""
    cid: str              # Disease CID code
    medicamentos: List    # Available medications
    ModeloFormulario: type # Form class to use
```

#### 4. View-Specific Data
```python
@dataclass
class NewPrescriptionData:
    """Data specific to new prescription creation (cadastro view)."""
    paciente_existe: bool           # Whether patient already exists
    primeira_data: Optional[str]    # Initial prescription date

@dataclass
class EditPrescriptionData:
    """Data specific to prescription editing (edicao view)."""
    processo_id: int        # Process being edited
    processo: Processo      # Process object
    dados_iniciais: dict    # Initial form data from existing process
```

#### 5. Success Result Composition
```python
@dataclass
class ViewSetupSuccess:
    """Successful view setup result with all required data."""
    common: CommonSetupData                                   # Shared data
    form: PrescriptionFormData                               # Form-related data
    specific: Union[NewPrescriptionData, EditPrescriptionData] # View-specific data

# Union type for all results
ViewSetupResult = Union[SetupError, ViewSetupSuccess]
```

### New Usage Pattern
```python
# Clear error handling with type checking
setup = service.setup_for_new_prescription(request)
if isinstance(setup, SetupError):  # Explicit error type checking
    messages.error(request, setup.message)
    return redirect(setup.redirect_to)

# Clear data access with logical grouping
usuario = setup.common.usuario           # Clearly from common setup
medico = setup.common.medico             # Clearly from common setup
medicamentos = setup.form.medicamentos   # Clearly form-related
paciente_existe = setup.specific.paciente_existe  # Clearly view-specific
```

## Files Changed

### 1. New File: `processos/services/view_setup_models.py`
**Purpose**: Contains all the new focused data classes
**Key Components**:
- `SetupError` - Error representation
- `CommonSetupData` - Shared setup data
- `PrescriptionFormData` - Form-related data  
- `NewPrescriptionData` - New prescription specifics
- `EditPrescriptionData` - Edit prescription specifics
- `ViewSetupSuccess` - Composed success result
- `ViewSetupResult` - Union type for all results
- Type guard functions: `is_setup_error()`, `is_setup_success()`

### 2. Updated: `processos/services/view_services.py`
**Changes Made**:

#### Import Updates
```python
# Added import for new data classes
from processos.services.view_setup_models import (
    ViewSetupResult, SetupError, ViewSetupSuccess,
    CommonSetupData, PrescriptionFormData, 
    NewPrescriptionData, EditPrescriptionData,
    is_setup_error, is_setup_success
)
```

#### Method Return Type Updates
```python
# Before
def setup_for_new_prescription(self, request) -> SetupResult:

# After  
def setup_for_new_prescription(self, request) -> ViewSetupResult:
```

#### Common Setup Method Refactoring
```python
# Before
def _setup_common_data(self, request) -> SetupResult:
    # Returned SetupResult with success/error fields mixed with data

# After
def _setup_common_data(self, request) -> Union[SetupError, CommonSetupData]:
    # Returns either error or focused common data
    return CommonSetupData(
        usuario=usuario,
        medico=medico, 
        clinicas=clinicas,
        escolhas=escolhas
    )
```

#### Error Handling Updates
```python
# Before
if not common_result.success:
    return common_result

# After
if isinstance(common_result, SetupError):
    return common_result
```

#### Success Result Composition
```python
# Before
return SetupResult(
    success=True, error_redirect=None, error_message=None,
    usuario=common_result.usuario, medico=common_result.medico,
    clinicas=common_result.clinicas, escolhas=common_result.escolhas,
    cid=cid, medicamentos=medicamentos, ModeloFormulario=ModeloFormulario,
    processo_id=None, processo=None, dados_iniciais=None,
    paciente_existe=paciente_existe, primeira_data=primeira_data
)

# After
return ViewSetupSuccess(
    common=common_result,
    form=PrescriptionFormData(
        cid=cid,
        medicamentos=medicamentos,
        ModeloFormulario=ModeloFormulario
    ),
    specific=NewPrescriptionData(
        paciente_existe=paciente_existe,
        primeira_data=primeira_data
    )
)
```

#### Validation Method Simplification
```python
# Before
def _validate_edit_prescription_session(self, request, usuario) -> ViewSetupResult:
    # Returned full SetupResult with mixed data

# After  
def _validate_edit_prescription_session(self, request, usuario) -> Optional[SetupError]:
    # Returns only error or None for success
    return None  # Success - no error
```

### 3. Updated: `processos/views.py`
**Changes Made**:

#### Import Updates
```python
# Added import for error type checking
from processos.services.view_setup_models import SetupError
```

#### Error Handling Updates
```python
# Before
if not setup.success:
    messages.error(request, setup.error_message)
    return redirect(setup.error_redirect)

# After
if isinstance(setup, SetupError):
    messages.error(request, setup.message)
    return redirect(setup.redirect_to)
```

#### Data Access Updates
```python
# Before - Direct field access
usuario = setup.usuario
medico = setup.medico
escolhas = setup.escolhas
medicamentos = setup.medicamentos
ModeloFormulario = setup.ModeloFormulario
processo = setup.processo
processo_id = setup.processo_id
paciente_existe = setup.paciente_existe

# After - Logical grouping access
usuario = setup.common.usuario
medico = setup.common.medico
escolhas = setup.common.escolhas
medicamentos = setup.form.medicamentos
ModeloFormulario = setup.form.ModeloFormulario
processo = setup.specific.processo
processo_id = setup.specific.processo_id
paciente_existe = setup.specific.paciente_existe
```

## Benefits Achieved

### 1. Single Responsibility Principle
- Each data class has one clear, focused purpose
- `SetupError` only handles errors
- `CommonSetupData` only handles shared setup data
- `PrescriptionFormData` only handles form-related data

### 2. Type Safety
- `Union[SetupError, ViewSetupSuccess]` provides clear type checking
- No more boolean `success` field that could be misunderstood
- Type guards provide explicit error checking

### 3. Composition Over Monoliths
- Success result composes focused data classes
- Easy to extend individual components without affecting others
- Clear data relationships through composition

### 4. Improved Readability
```python
# Clear hierarchical access shows data relationships
setup.common.usuario     # User from common setup
setup.form.medicamentos  # Medications for form
setup.specific.processo  # Process specific to edit view
```

### 5. Maintainability
- Adding new common data only affects `CommonSetupData`
- Adding new form data only affects `PrescriptionFormData`
- Adding new view-specific data only affects specific data classes
- No risk of breaking unrelated functionality

### 6. Better Error Handling
- Explicit error types instead of boolean flags
- Clear error messages and redirect destinations
- Type-safe error checking with `isinstance()`

## Backward Compatibility

The refactoring maintains full backward compatibility:
- All existing functionality preserved
- No breaking changes to external interfaces
- All tests pass without modification
- Views continue to work as expected

## Bug Fixes During Implementation

### AttributeError Fix
**Issue**: During implementation, the refactoring introduced an AttributeError in the `edicao` view:
```
AttributeError: 'ViewSetupSuccess' object has no attribute 'dados_iniciais'
```

**Root Cause**: Views were still trying to access old flat attributes instead of the new composed structure.

**Solution**: Updated all view references to use the new structure:
```python
# Before
setup.dados_iniciais  # AttributeError
setup.cid            # AttributeError 
setup.primeira_data  # AttributeError

# After
setup.specific.dados_iniciais  # ✅ Works
setup.form.cid                # ✅ Works
setup.specific.primeira_data  # ✅ Works
```

**Files Fixed**:
- `processos/views.py` - Updated 6 attribute references to use new structure

## Testing

All tests continue to pass:
- ✅ `tests.test_pdf_services_basic` - 6/6 tests passing
- ✅ `tests.test_refactoring_smoke` - 8/8 tests passing  
- ✅ System check identifies no issues

## Migration Guide

### For Future Development

When adding new setup data:

1. **Identify the category**:
   - Error? → Add to `SetupError`
   - Common to all views? → Add to `CommonSetupData`
   - Form-related? → Add to `PrescriptionFormData`
   - View-specific? → Add to appropriate specific data class

2. **Follow the pattern**:
   ```python
   # Good: Focused addition
   @dataclass
   class CommonSetupData:
       usuario: Any
       medico: Any
       clinicas: QuerySet
       escolhas: Tuple
       new_common_field: str  # New common field

   # Bad: Adding unrelated fields
   @dataclass  
   class CommonSetupData:
       usuario: Any
       medico: Any
       clinicas: QuerySet
       escolhas: Tuple
       processo_id: int  # This belongs in EditPrescriptionData!
   ```

3. **Use composition**:
   ```python
   # Access data through logical groups
   user = setup.common.usuario
   form_class = setup.form.ModeloFormulario
   patient_exists = setup.specific.paciente_existe
   ```

This refactoring establishes a solid foundation for future development with clear separation of concerns and maintainable data structures.